# Justin Johnson, May 2020

import arcpy

# list all feature classes in a geodatabase

input_gdb = r'T:\Shared drives\DNR_FFSL\Forestry\GIS\Forest Stewardship\Parcels_Utah_2020.gdb'

# workspace must be set prior to listing feature classes
arcpy.env.workspace = input_gdb

# feature layer containing forest cover layer
forest = r'NLCD_2016_UT_Forest_polygon'


fcs = arcpy.ListFeatureClasses(feature_type='polygon')  # returns a list of strings

# iterate through each feature class
# print its name, and a list of its fields
for fc in fcs:
    print(fc)

    # fields = [fld.baseName for fld in arcpy.ListFields(fc)]

    # print(fields)


# print all raster layers in the workspace
rasters = arcpy.ListRasters()

for rast in rasters:
    print(rast)
