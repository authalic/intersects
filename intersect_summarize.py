# Justin Johnson, Nov 2016

import arcpy
import os
import time


# Intersection input features
# currently supports polygon and polyline features only
# ordering doesn't affect operation, but the output fc will be named by appending the inputs in order: name01_name02
# and the summary tables will be prepared for input_01

input_01 = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\inputs'
input_02 = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\designs'

# Set workspace for storing output feature classes and results tables
arcpy.env.workspace = r'C:\projects\000007473\wetlands\Wetland_Impacts_Level_2\test_wetland_impacts.gdb\test'

# names of the area and length fields in each output feature class
# these may already exist, if they're present in one of the input FCs
# if not, the fields will be created using the name assigned below
areafield = "AREA_AC"
lengthfield = "LEN_FT"

# units of measurement for intersect calculations
# must be spelled all lowercase
area_unit = "acres"  # valid:  acres, squarefeet, squaremiles, hectares, squaremeters
length_unit = "feet" # valid:  feet, meters, miles

# walk through input datasets
dirpath_01, dirnames_01, filenames_01 = arcpy.da.Walk(input_01).next()
dirpath_02, dirnames_02, filenames_02 = arcpy.da.Walk(input_02).next()


# Perform an Intersect operation with each input layer
# outer loop:  input_01
# inner loop:  input_02

starttime = time.time()

# outer loop
for filename_01 in filenames_01:

    # inner loop
    for filename_02 in filenames_02:

        inputFeatures = os.path.join(dirpath_01, filename_01) + ";" + os.path.join(dirpath_02, filename_02)
        output_fc = filename_01 + "_" + filename_02

        print output_fc

        # uncomment the next line to execute the Intersect geoprocessing tool
        # Also, look for a way to overwrite previous output
        arcpy.Intersect_analysis(inputFeatures, output_fc, "ALL", "", "INPUT")

        # create a list of fields in the feature class
        fields = [f.name for f in arcpy.ListFields(output_fc)]

        # obtain the geometry type of the feature class
        geomdesc = arcpy.Describe(output_fc).shapeType   # returns:  Point, Polyline, Polygon, Multipoint, MultiPatch

        # check if the feature class has the appropriate dimension field for its geometry type
        # if not, create it.  Note: a schema lock will need to be acquired in order to create the fields

        if geomdesc == "Polyline" and not (lengthfield in fields):
            print "  Creating a Length field for this polyline feature class"
            arcpy.AddField_management(output_fc, lengthfield, "DOUBLE")
        elif geomdesc == "Polygon" and not (areafield in fields):
            print "  Creating an Area field for this polygon feature class"
            arcpy.AddField_management(output_fc, areafield, "DOUBLE")


        # calculate the length or area of the intersects
        if geomdesc == "Polyline":
            calc_exp = "!shape.length@{}!".format(length_unit)
            arcpy.CalculateField_management(output_fc, lengthfield, calc_exp, "PYTHON_9.3", "")
        elif geomdesc == "Polygon":
            calc_exp = "!shape.area@{}!".format(area_unit)
            arcpy.CalculateField_management(output_fc, areafield, calc_exp, "PYTHON_9.3", "")


endtime = time.time()

print "Done in", str(endtime - starttime), "seconds"
# fcs = arcpy.ListFeatureClasses()
#
# for fc in fcs:
#     print fc
#     fields = [f.name for f in arcpy.ListFields(fc)]
#     print fields








# For each output layer, calculate the area or length of each intersected segment
# Iterate through each Intersect
# Sum the area or length for the entire layer
# write the name of the design and the total area/length to a row in a table, with a timestamp



# tab = 'C:\projects\ModelBuilder\ModelBuilder_data.gdb\output_table'
#
# fields = ['TEXTFIELD', 'NUMBER']
#
# # create an insert cursor to add rows to table
# cursor = arcpy.da.InsertCursor(tab, fields)
#
# for x in range(20):
#     cursor.insertRow(("fish", x))
#
# del cursor
