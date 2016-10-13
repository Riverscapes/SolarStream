# file name:	solar_predict.py
# description:	This tool predicts solar insolation for a user-supplied stream network. The tool assumes that the  
#				stream network has been previously segmented. Solar insolation is calculated per stream network    
#				segment. Essentially, this tool attempts to model mean solar radiation hitting each stream segment 
#				by creating a coarse approximation of shading based on topography and vegetation. The tool relies   
#				on ESRI's Area Solar Radiation tool.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, solar_util.py
# version:		0.2

import arcpy, os
from arcpy.sa import *
import solar_util as u

# input variables
in_dem = arcpy.GetParameterAsText(0) # DEM representing "bare earth" topographic surface of study area.
in_canopy = arcpy.GetParameterAsText(1) # Raster dataset representing vegetation or canopy height
in_stream = arcpy.GetParameterAsText(2) # Segmented stream network as a vector dataset.
in_strm_indx = arcpy.GetParameterAsText(3) # Unique ID field for segmented stream network (i.e. "LineOID")
in_strm_area = arcpy.GetParameterAsText(4) # Polygon representing open water areas of the stream (i.e. NHD Area)
result = arcpy.GetParameterAsText(5)  # Feature class that is the final output of the model.
workspace_temp = arcpy.GetParameterAsText(6)  # File geodatabase to serve as temporary scratch workspace.
time_config = arcpy.GetParameterAsText(7) # Time period for calculating solar radiation. Required by AreaSolarRadiation.
day_intv = arcpy.GetParameterAsText(8) # Time interval (by days) used for calculation of sky vectors.
hour_intv = arcpy.GetParameterAsText(9)  # Time interval (by hour) used for calculating sky vectors.

def main(in_dem,
         in_canopy,
         in_stream,
         in_strm_indx,
         in_strm_area,
         out_fc,
         workspace_temp,
         time_config,
         day_intrvl,
         hour_intrvl):
    # set environmental variables
    arcpy.env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = in_dem
    arcpy.env.snapRaster = in_dem
    desc = arcpy.Describe(in_dem)
    arcpy.env.cellSize =desc.meanCellHeight
    arcpy.env.mask = in_dem
    arcpy.env.workspace = workspace_temp
    arcpy.env.scratchWorkspace = workspace_temp

    # solar parameters (not set by user)
    sky_size = 400

    # get OID of segmented stream network
    in_stream_oid = arcpy.Describe(in_stream).OIDFieldName

    # convert stream and stream area polygon to two-class raster dataset
    tmp_stream = arcpy.FeatureClassToFeatureClass_conversion(in_stream, workspace_temp, "tmp_stream")
    arcpy.MakeFeatureLayer_management(tmp_stream, "in_stream_lyr")
    arcpy.MakeFeatureLayer_management(in_strm_area, "in_strm_area_lyr")
    poly_strm_area, ras_strm_area = u.convert_raster(in_dem, "in_stream_lyr", "in_strm_area_lyr", workspace_temp)

    # buffer stream segments
    seg_poly = u.divide_polygon(in_stream, poly_strm_area, workspace_temp)

    # find latitude of the study basin centroid
    wgs84_prj = r"Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj"
    prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], wgs84_prj)
    temp_spRef = arcpy.SpatialReference(prjFile)
    with (arcpy.da.SearchCursor(in_stream,["SHAPE@Y"], "#", temp_spRef)) as cursor:
        for row in cursor:
            latitude = row[0]

    # prepare elevation data for solar radiation modeling
    arcpy.AddMessage("Calculating solar radiation...")
    rcls_strm = Reclassify(ras_strm_area, "VALUE", RemapValue([[1,1],["NODATA",0]]))
    rcls_strm.save(workspace_temp + r"\rcls_strm")
    remove_strm = Con(rcls_strm, 0, in_canopy, "VALUE = 1")
    veg_div = Divide(remove_strm, 10.0)
    elev_vegtopo = Plus(veg_div, in_dem)

    # calculate mean solar radiation per bankfull buffer
    area_solar = AreaSolarRadiation(elev_vegtopo, latitude, sky_size, time_config, day_intv, hour_intv)
    area_solar.save(workspace_temp + r"\area_solar")
    zstat_result = "in_memory\\zstat_result"
    ZonalStatisticsAsTable(seg_poly, "JOIN_FID", area_solar, zstat_result, "DATA", "MEAN")
    arcpy.AddField_management("in_stream_lyr", "area_solar", "DOUBLE")
    arcpy.JoinField_management("in_stream_lyr", in_stream_oid, zstat_result, "JOIN_FID", ["MEAN"])
    arcpy.CalculateField_management("in_stream_lyr","area_solar","!MEAN!", "PYTHON_9.3")
    arcpy.DeleteField_management("in_stream_lyr", ["MEAN"])
    arcpy.CopyFeatures_management("in_stream_lyr", out_fc)

    # clean up in_memory files
    u.clear_inmem()

    return result

main(in_dem, in_canopy, in_stream, in_strm_indx, in_strm_area, result, workspace_temp, time_config, day_intv, hour_intv)