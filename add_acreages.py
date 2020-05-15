# Justin Johnson
# Senior GIS Analyst
# Utah Division of Forestry, Fire and State Lands
# May 2020

'''
Summary:
This script runs through all feature layers in a geodatabase and adds a new acreage
field, then calculates the acreage value.

Feature layers are privately owned parcel polygons containing forested areas in
each of the 29 counties in Utah.  Output of export_forest_parcels.py
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

# iterate through the feature classes
for fc in fcs:
    if '_privateforest' in fc:  # use the private forest parcel layers only

        print('\n', fc)

        # select the private parcels
        print("   adding 'Parcel_Acres' field")
        starttime = time.time()  # start the stopwatch

        arcpy.AddField_management(fc, 'Parcel_Acres', 'DOUBLE')

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


        # calculate acreage
        print("   calculating geometry: area in acres")
        starttime = time.time()  # start the stopwatch

        arcpy.CalculateField_management(fc, "Parcel_Acres", "!SHAPE.AREA@ACRES!", "PYTHON3")

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


        # add two new (empty) fields for future use
        # Forest_Acres will contain the total acreage of forested land in this parcel
        # the 'Forest_pct' field will contain the forested percent of the parcel

        print("   adding 'Forest_Acres' field")
        arcpy.AddField_management(fc, 'Forest_Acres', "DOUBLE")

        print("   adding 'Forest_pct' field")
        arcpy.AddField_management(fc, 'Forest_pct', "DOUBLE")

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


t2 = time.time() # stop the total runtime timer
secs = round(t2 - t1, 1)

print("done - elapsed time: ", str(datetime.timedelta(seconds=secs)))
