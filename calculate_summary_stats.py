# Justin Johnson
# Senior GIS Analyst
# Utah Division of Forestry, Fire and State Lands
# May 2020

'''
Summary:
This script runs through all "intersect" feature layers in a geodatabase from the
previous intersect operation:  intersect_forest_parcels.py

Summary statistics are calculated on the attribute table.
https://pro.arcgis.com/en/pro-app/tool-reference/analysis/summary-statistics.htm


Case Field: The FID field from the original privateforest feature class used in the
    previous "intersect" operation.  Example:  "FID_Parcels_Carbon_privateforest"

Statistics Field:  Forest_Acres
Statistics Operation:  Sum

Output:  A standalone table, with all acres in the "Forest_Acres" fieled summed
according to the original privateforest FID field

Next step:  Join these summary tables to the original forest parcels layer, then
copy the summed acreage of forest cover into its "Forest_Acres" field, then
use that to calculate the percent forest cover for that parcel.
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
fcs = arcpy.ListFeatureClasses(feature_type='polygon')

# filter out any feature class that does not have "intersect" in its name
fcs = [fc for fc in fcs if "intersect" in fc]

# iterate through the "intersect" feature classes
for fc in fcs:

    print('\n', fc)

    # run the Summary Statistics function
    print("   calculating summary statistics")
    starttime = time.time()  # start the stopwatch

    # create the name of the field containing the FID Case Field
    # add "FID_" and slice off "_intersect" from filename
    casefield = "FID_" + fc[:-10]

    # create the name of the output table
    outtable = fc + "_summary"

    # summarize the Forest_Acres field
    arcpy.Statistics_analysis(fc, outtable, [["Forest_Acres", "SUM"]], casefield)

    secs = round(time.time() - starttime, 1)
    print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


t2 = time.time() # stop the total runtime timer
secs = round(t2 - t1, 1)
print("done - elapsed time: ", str(datetime.timedelta(seconds=secs)))
