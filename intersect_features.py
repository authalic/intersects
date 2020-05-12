# Justin Johnson, May 2020

import arcpy
import datetime
import time

print("starting")
t1 = time.time() # start the timer

# workspace must be set prior to listing feature classes
input_gdb = r'T:\Shared drives\DNR_FFSL\Forestry\GIS\Forest Stewardship\Parcels_Utah_2020.gdb'
arcpy.env.workspace = input_gdb

# feature layer containing forest cover layer (select_features layer)
forest = r'NLCD_2016_UT_Forest_polygon_NAD83utm12'

# get all feature classes in the workspace
fcs = arcpy.ListFeatureClasses(feature_type='polygon')  # returns a list of strings

# iterate through the feature classes
for fc in fcs:
    if fc != forest:

        print('\n', fc)

        # select the private parcels
        print("   selecting private parcels")
        starttime = time.time()  # start the stopwatch
        private_parcels = arcpy.SelectLayerByAttribute_management(fc, "NEW_SELECTION", "LOWER(OWN_TYPE) = 'private'")
        secs = time.time() - starttime
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))

        # select the private parcels that intersect the forested areas
        print("   selecting forested private")
        starttime = time.time()  # start the stopwatch
        private_forested = arcpy.SelectLayerByLocation_management(private_parcels, "INTERSECT", selection_type="SUBSET_SELECTION", select_features=forest)
        secs = time.time() - starttime
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))

        # save the remaining features as a new layer
        print("   saving output layer")
        starttime = time.time()  # start the stopwatch
        outlayername = fc + '_privateforest'
        arcpy.CopyFeatures_management(private_forested, outlayername)
        secs = time.time() - starttime
        print("     done - elapsed time: ", str(datetime.timedelta(seconds=secs)))

t2 = time.time()
print("done - elapsed time: ", str(datetime.timedelta(seconds=t2 - t1)))
