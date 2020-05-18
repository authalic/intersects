# Justin Johnson
# Senior GIS Analyst
# Utah Division of Forestry, Fire and State Lands
# May 2020

'''
Summary:
This script runs through all feature layers in a geodatabase
The feature classes containing privately owned forested pixels are intersected with the
forested pixel polygon layer.  This layer is the polygon representation of the raster
dataset from NLCD.

- National Land Cover Dataset: https://www.mrlc.gov/national-land-cover-database-nlcd-2016

The acreages of these intersected parcels will then be calculated.
Then, summaries of the intersected polygons will be run, to add up the total acreage
Then, that summary table will be joined to the original forested polygon layer.
Finally, the forested acre totals from the summary will be copied to the attribute table
of the forested polygon layer, in order to calcuate the percentage of the origianal parcel
that is covered by forest pixels.

https://pro.arcgis.com/en/pro-app/tool-reference/analysis/intersect.htm
'''


import arcpy
import datetime
import time

print("starting")
t1 = time.time() # start the timer to measure total runtime

# workspace must be set prior to listing feature classes
input_gdb = r'T:\Shared drives\DNR_FFSL\Forestry\GIS\Forest Stewardship\Parcels_Utah_2020.gdb'
arcpy.env.workspace = input_gdb

# feature layer containing forest cover layer (select_features layer)
forest = r'NLCD_2016_UT_Forest_polygon_NAD83utm12'

# get all feature class names in the workspace, as a list of strings
fcs = arcpy.ListFeatureClasses(feature_type='polygon')

# remove any feature class that does not have "privateforest" in its name
fcs = [fc for fc in fcs if "privateforest" in fc]

# iterate through the feature classes
for fc in fcs:
    if fc != forest:  # skip the forest cover layer

        print('\n', fc)

        # select the private parcels
        print("   intersecting forest pixels and private parcels")
        starttime = time.time()  # start the stopwatch

        arcpy.Intersect_analysis([fc, forest], fc + "_intersect", "ALL")

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


        # select the private parcels
        print("   adding 'Forest_Acres' field")
        starttime = time.time()  # start the stopwatch

        arcpy.AddField_management(fc + "_intersect", 'Forest_Acres', 'DOUBLE')

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))


        # calculate acreage
        print("   calculating geometry: area in acres")
        starttime = time.time()  # start the stopwatch

        arcpy.CalculateField_management(fc + "_intersect", "Forest_Acres", "!SHAPE.AREA@ACRES!", "PYTHON3")

        secs = round(time.time() - starttime, 1)
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))

t2 = time.time() # stop the total runtime timer
secs = round(t2 - t1, 1)
print("done - elapsed time: ", str(datetime.timedelta(seconds=secs)))
