# Justin Johnson
# Senior GIS Analyst
# Utah Division of Forestry, Fire and State Lands
# May 2020

'''
Summary:

Join two tables:
summary statistics (standalone table) and forest parcels (attribute table)
copy the forest acres sum from the summary to the feature class
calculate the percent forest cover for each private forested parcel

output:  At the end of this operation, each county will have a feature class
of privately owned forested parcels, with percent forest cover of each parcel
calculated in the attribute table.

next?
join all county parcel layers into a single statewide layer?
publish to ArcGIS Online
'''


import arcpy
import datetime
import time

print("starting")
t1 = time.time() # start the timer to measure total runtime

# workspace must be set prior to listing feature classes
input_gdb = r'T:\Shared drives\DNR_FFSL\Forestry\GIS\Forest Stewardship\Parcels_Utah_2020.gdb'
arcpy.env.workspace = input_gdb

# get all feature class names in the workspace, as a list of strings
fcs = arcpy.ListFeatureClasses()

# filter out any feature class that does not have "intersect" in its name
fcs = [fc for fc in fcs if "intersect" in fc]


# iterate through the "intersect" feature classes
for fc in fcs:

    print('\n', fc)

    # Join the forested private parcel layer with the summary table
    # https://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-join.htm
    print("  joining tables")
    starttime = time.time()  # start the stopwatch

    # Create the join arguments
    in_layer = fc[:-10]             # ex: "Parcels_Grand_privateforest" (remove the "_intersect" from end of fc name)
    in_field = "OBJECTID"
    join_table = fc + "_summary"    # ex: "Parcels_Grand_privateforest_intersect_summary"
    join_field = "FID_" + in_layer  # ex: "FID_Parcels_Grand_privateforest"

    join_fc = arcpy.AddJoin_management(in_layer, in_field, join_table, join_field, 'KEEP_ALL')

    secs = round(time.time() - starttime, 1)
    print("    done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


    # copy the total forest acres field
    # https://pro.arcgis.com/en/pro-app/tool-reference/data-management/calculate-field.htm
    print("  copying Forest_Acres field")
    starttime = time.time()  # start the stopwatch

    # create the CalculateField arguments
    in_table = join_fc  # use the joined table
    field = in_layer + ".Forest_Acres"
    expression = "!" + join_table + ".SUM_Forest_Acres!"
    expression_type = "PYTHON3"
    code_block = ""
    field_type = ""

    arcpy.CalculateField_management(in_table, field, expression, expression_type, code_block, field_type)

    secs = round(time.time() - starttime, 1)
    print("    done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


    # remove the join
    # https://pro.arcgis.com/en/pro-app/tool-reference/data-management/remove-join.htm
    print("  removing the join")
    starttime = time.time()  # start the stopwatch

    arcpy.RemoveJoin_management(join_fc)

    secs = round(time.time() - starttime, 1)
    print("    done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


    # calculate the forest parcent
    print("  calculating Pct_Forest")
    starttime = time.time()  # start the stopwatch

    arcpy.CalculateField_management(in_layer, "Forest_pct", "!Forest_Acres! / !Parcel_Acres! * 100", "PYTHON3", "", "")

    secs = round(time.time() - starttime, 1)
    print("    done - elapsed time: ", str(datetime.timedelta(seconds=secs)))



t2 = time.time() # stop the total runtime timer
secs = round(t2 - t1, 1)
print("done - elapsed time: ", str(datetime.timedelta(seconds=secs)))
