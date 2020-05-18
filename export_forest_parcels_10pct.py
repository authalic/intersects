# Justin Johnson
# Senior GIS Analyst
# Utah Division of Forestry, Fire and State Lands
# May 2020

'''
Summary:
This script runs through all feature layers in a geodatabase
Filters out the feature classes that have the percent forest cover field
Using those FCs, select the parcels that are >10% forested
Save those as a new FC
'''

import arcpy
import datetime
import time

print("starting")
t1 = time.time() # start the timer to measure total runtime

# workspace must be set prior to listing feature classes
input_gdb = r'T:\Shared drives\DNR_FFSL\Forestry\GIS\Forest Stewardship\Parcels_Utah_2020.gdb'
arcpy.env.workspace = input_gdb

# get all feature classes in the workspace
fcs = arcpy.ListFeatureClasses(feature_type='polygon')  # returns a list of strings

# only use the FCs that end with "privateforest"
fcs = [fc for fc in fcs if fc[-13:] == "privateforest"]

# iterate through the feature classes
for fc in fcs:

    print('\n', fc)

    # select the private parcels
    print("   selecting private parcels >10% forest cover")

    starttime = time.time()  # start the stopwatch
    parcels_10 = arcpy.SelectLayerByAttribute_management(fc, "NEW_SELECTION", "Forest_Pct >= 10.0")

    secs = round(time.time() - starttime, 1)
    print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


    # save the remaining features as a new layer
    print("   saving output layer")
    starttime = time.time()  # start the stopwatch

    outlayername = fc + '_10pct'
    arcpy.CopyFeatures_management(parcels_10, outlayername)

    secs = round(time.time() - starttime, 1)
    print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))

t2 = time.time() # stop the total runtime timer
secs = round(t2 - t1, 1)
print("done - elapsed time: ", str(datetime.timedelta(seconds=secs)))
