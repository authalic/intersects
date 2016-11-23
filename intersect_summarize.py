# Justin Johnson, Nov 2016

import arcpy
import os
import time

# Intersection input features
# currently supports polygon and polyline features only
# ordering doesn't affect operation, but the output fc will be named by appending the inputs in order: name01_name02
# and the summary tables will be prepared for each feature class in input_01

input_01 = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\inputs'
input_02 = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\designs'

# Set workspace for storing output intersect feature classes
arcpy.env.workspace = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\intersects'

# Tables can't be created in a Feature Dataset, so place them in the GDB root level
sumtables = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb'

# Field names in output intersect feature classes for Area or Length geometry calculation.
# These may already exist, if they're present in one of the input FCs
# if not, the fields will be created using the name assigned below.
# Change these names to match the particular units involved in the area/length calculations
areafield = "AREA_AC"
lengthfield = "LEN_FT"

# Units of measurement for intersect geometry calculations
area_unit = "acres"  # valid:  acres, squarefeet, squaremiles, hectares, squaremeters
length_unit = "feet" # valid:  feet, meters, miles

# walk through input datasets and unpack the lists of filenames
# Note: Walk() returns a Generator object. Each next() call returns a tuple of 3
# since we're not browsing subdirectories, only one call to next() is required
dirpath_01, dirnames_01, filenames_01 = arcpy.da.Walk(input_01).next()
dirpath_02, dirnames_02, filenames_02 = arcpy.da.Walk(input_02).next()

# Perform an Intersect operation with each layer in input_01 and input_02
# outer loop:  input_01
# inner loop:  input_02

starttime = time.time()  # start the stopwatch

# outer loop
for filename_01 in filenames_01:

    # create the new summary table here, for storing the length or area of each intersection
    sumtablename = filename_01 + '_geomcalc'  # name of the summary table
    arcpy.CreateTable_management(sumtables, sumtablename)

    # add the field to store the name of the input file in the output summary table
    arcpy.AddField_management(os.path.join(sumtables, sumtablename), 'INPUTNAME', 'TEXT', '', '', 80)

    # get the geometry type of the current feature class
    # add the appropriate field for either area or length, depending on geometry type
    # create an insert cursor for writing records to the table
    geomdesc = arcpy.Describe(os.path.join(dirpath_01, filename_01)).shapeType

    if geomdesc == "Polyline":
        # add the length field
        arcpy.AddField_management(os.path.join(sumtables, sumtablename), lengthfield, 'DOUBLE')
        # create an insert cursor for the table
        cursor = arcpy.da.InsertCursor(os.path.join(sumtables, sumtablename), ['INPUTNAME', lengthfield])
    elif geomdesc == "Polygon":
        # add the area field
        arcpy.AddField_management(os.path.join(sumtables, sumtablename), areafield, 'DOUBLE')
        # create an insert cursor for the table
        cursor = arcpy.da.InsertCursor(os.path.join(sumtables, sumtablename), ['INPUTNAME', areafield])

    # inner loop
    for filename_02 in filenames_02:
        # create a string containing the full paths to the two current input features
        inputFeatures = os.path.join(dirpath_01, filename_01) + ";" + os.path.join(dirpath_02, filename_02)

        # create the string for the name of the feature class storing the intersect results
        output_fc = filename_01 + "_" + filename_02

        print output_fc

        # execute the Intersect geoprocessing tool
        arcpy.Intersect_analysis(inputFeatures, output_fc, "ALL", "", "INPUT")

        # get a list of fields to check if the Geometry Calculation field already exists in the output feature class
        fields = [f.name for f in arcpy.ListFields(output_fc)]

        # obtain the geometry type of the output feature class
        outgeomdesc = arcpy.Describe(output_fc).shapeType   # returns:  Point, Polyline, Polygon, Multipoint, MultiPatch

        # check if the feature class has the appropriate dimension field for its geometry type. if not, create it.
        # Note: a schema lock will need to be acquired in order to create the fields, so check ArcCatalog

        if outgeomdesc == "Polyline" and not (lengthfield in fields):
            print "  Creating a Length field for this polyline feature class"
            arcpy.AddField_management(output_fc, lengthfield, "DOUBLE")
        elif outgeomdesc == "Polygon" and not (areafield in fields):
            print "  Creating an Area field for this polygon feature class"
            arcpy.AddField_management(output_fc, areafield, "DOUBLE")

        # calculate the geometry (length or area) of the intersects
        # Then, copy each record to the "geomcalc" results table

        if outgeomdesc == "Polyline":
            calc_exp = "!shape.length@{}!".format(length_unit)
            arcpy.CalculateField_management(output_fc, lengthfield, calc_exp, "PYTHON_9.3", "")

            # test if the current layer is empty and insert a row into the results table indicating such
            # Note: GetCount_management returns a Result object. To get the count value, extract the [0] element
            if arcpy.GetCount_management(output_fc)[0] == '0': # returned value is a String
                cursor.insertRow([filename_02, 0])
            else:  # loop through all values in the table
                with arcpy.da.SearchCursor(output_fc, [lengthfield]) as searchcurs:
                    for row in searchcurs:
                        # store the layer name and the geometry calc as a new row in the geomcalc table
                        cursor.insertRow([filename_02, row[0]])

        elif outgeomdesc == "Polygon":
            calc_exp = "!shape.area@{}!".format(area_unit)
            arcpy.CalculateField_management(output_fc, areafield, calc_exp, "PYTHON_9.3", "")

            # test if the current layer is empty and insert a row into the results table indicating such
            # Note: GetCount_management returns a Result object. To get the count value, extract the [0] element
            if arcpy.GetCount_management(output_fc)[0] == '0':
                cursor.insertRow([filename_02, 0])
            else:  # loop through all values in the table
                with arcpy.da.SearchCursor(output_fc, [areafield]) as searchcurs:
                    for row in searchcurs:
                        # store the layer name and the geometry calc as a new row in the geomcalc table
                        cursor.insertRow([filename_02, row[0]])
    # delete the input cursor
    del cursor

    # Create the Summarize tables from the geomcalc tables, using Statiscics_analysis()
    # Summarize by length/area, group by the "INPUTNAME" field

    if geomdesc == "Polyline":
        # summarize each input on the length field
        in_table = os.path.join(sumtables, filename_01 + '_geomcalc')
        out_table = os.path.join(sumtables, filename_01 + '_summarize')
        arcpy.Statistics_analysis(in_table, out_table, [[lengthfield, "SUM"]], "INPUTNAME")

    elif geomdesc == "Polygon":
        # summarize each input on the area field
        in_table = os.path.join(sumtables, filename_01 + '_geomcalc')
        out_table = os.path.join(sumtables, filename_01 + '_summarize')
        arcpy.Statistics_analysis(in_table, out_table, [[areafield, "SUM"]], "INPUTNAME")

endtime = time.time()  # stop the stopwatch

# Done.  Print the elapsed seconds.
print "Done in", str(endtime - starttime), "seconds"