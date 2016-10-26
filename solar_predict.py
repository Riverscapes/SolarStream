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
import metadata

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

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
out_meta = arcpy.GetParameterAsText(10) # Metadata XML file (file name and directory path

def raster_poly(in_dem, in_strm, in_strm_area, workspace_temp):
    # convert streams and stream area polygons to a single polygon with rasterized boundaries
    desc = arcpy.Describe(in_dem)
    cellSize = desc.meanCellHeight
    arcpy.AddField_management(in_strm, "VAL", "SHORT")
    arcpy.AddField_management(in_strm_area, "VAL", "SHORT")
    arcpy.CalculateField_management(in_strm, "VAL", "1", "PYTHON_9.3")
    arcpy.CalculateField_management(in_strm_area, "VAL", "1", "PYTHON_9.3")
    arcpy.AddMessage("Converting stream polyline and area vectors to raster format...")
    strm_ras = workspace_temp + r"\strm_ras"
    arcpy.PolylineToRaster_conversion(in_strm, "VAL", strm_ras, "", "", cellSize)
    poly_ras = workspace_temp + r"\poly_ras"
    arcpy.PolygonToRaster_conversion(in_strm_area, "VAL", poly_ras, "CELL_CENTER", "", cellSize)
    # Create stream area polygon for summarizing solar values later
    strm_poly = workspace_temp + r"\strm_poly"
    arcpy.RasterToPolygon_conversion(strm_ras, strm_poly, "NO_SIMPLIFY")
    area_poly = workspace_temp + r"\area_poly"
    arcpy.RasterToPolygon_conversion(poly_ras, area_poly, "NO_SIMPLIFY")
    merge_poly = workspace_temp + r"\merge_poly"
    arcpy.Merge_management(strm_poly + ";" + area_poly, merge_poly)
    dslv_poly = workspace_temp + r"\dslv_poly"
    arcpy.Dissolve_management(merge_poly, dslv_poly)
    # Create stream area raster for reconditioning canopy raster data
    arcpy.AddField_management(dslv_poly, "VAL", "SHORT")
    arcpy.CalculateField_management(dslv_poly, "VAL", "1", "PYTHON_9.3")

    return dslv_poly, strm_ras, poly_ras


def main(in_dem, in_canopy, in_stream, in_strm_indx, in_strm_area, out_fc, workspace_temp, time_config, day_intrvl, hour_intrvl, out_meta):
    # set environmental variables
    arcpy.env.outputCoordinateSystem = in_dem
    arcpy.env.snapRaster = in_dem
    arcpy.env.mask = in_dem
    desc = arcpy.Describe(in_dem)
    cellSize = desc.meanCellHeight
    arcpy.env.cellSize = cellSize
    arcpy.env.workspace = workspace_temp
    arcpy.env.scratchWorkspace = workspace_temp

    dem_ras = arcpy.sa.Raster(in_dem)
    dem_extent = dem_ras.extent
    arcpy.env.extent = dem_extent

    # start writing metadata
    mWriter = metadata.MetadataWriter("Predict Solar Insolation for a Stream Network", "0.2")
    mWriter.createRun()
    mWriter.currentRun.addParameter("Bare earth DEM", in_dem)
    mWriter.currentRun.addParameter("Canopy height raster", in_canopy)
    mWriter.currentRun.addParameter("Stream network feature class", in_stream)
    mWriter.currentRun.addParameter("Stream unique ID field", in_strm_indx)
    mWriter.currentRun.addParameter("Stream area polygon feature class", in_strm_area)
    mWriter.currentRun.addParameter("Scratch workspace", workspace_temp)
    mWriter.currentRun.addParameter("Time configuration", time_config)
    mWriter.currentRun.addParameter("Day interval", day_intrvl)
    mWriter.currentRun.addParameter("Hour interval", hour_intrvl)
    mWriter.currentRun.addOutput("Output feature class", out_fc)
    mWriter.currentRun.addOutput("Metadata XML file", out_meta)

    # solar parameters (not set by user)
    sky_size = 400

    # get OID of segmented stream network
    in_stream_oid = arcpy.Describe(in_stream).OIDFieldName

    # convert stream and stream area polygon to two-class raster dataset
    tmp_stream_line = arcpy.FeatureClassToFeatureClass_conversion(in_stream, workspace_temp, "tmp_stream_line")
    tmp_stream_poly = arcpy.FeatureClassToFeatureClass_conversion(in_strm_area, workspace_temp, "tmp_strm_poly")
    arcpy.MakeFeatureLayer_management(tmp_stream_line, "in_strm_line_lyr")
    arcpy.MakeFeatureLayer_management(tmp_stream_poly, "in_strm_poly_lyr")
    poly_strm_area, strm_ras, poly_ras = raster_poly(in_dem, "in_strm_line_lyr", "in_strm_poly_lyr", workspace_temp)
    strm_ras_lyr = "strm_ras_lyr"
    poly_ras_lyr = "poly_ras_lyr"
    arcpy.MakeRasterLayer_management(strm_ras, strm_ras_lyr)
    arcpy.MakeRasterLayer_management(poly_ras, poly_ras_lyr)

    # buffer stream segments
    seg_poly = u.divide_polygon(in_stream, poly_strm_area, workspace_temp)
    arcpy.env.extent = dem_extent # reset because the divide_polygon function sets it to the stream area polygon extent

    # find latitude of the study basin centroid
    wgs84_prj = r"Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj"
    prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], wgs84_prj)
    temp_spRef = arcpy.SpatialReference(prjFile)
    with (arcpy.da.SearchCursor(in_stream,["SHAPE@Y"], "#", temp_spRef)) as cursor:
        for row in cursor:
            latitude = row[0]

    # prepare elevation data for solar radiation modeling
    arcpy.AddMessage("Calculating solar radiation...")
    arcpy.CalculateStatistics_management(strm_ras)
    arcpy.CalculateStatistics_management(poly_ras)
    rcls_strm_line = Reclassify(strm_ras_lyr, "VALUE", RemapValue([[1, 1], ["NODATA", 0]]))
    rcls_strm_line.save(workspace_temp + r"\rcls_strm_line")
    rcls_strm_poly = Reclassify(poly_ras_lyr, "VALUE", RemapValue([[1, 1], ["NODATA", 0]]))
    rcls_strm_poly.save(workspace_temp + r"\rcls_strm_poly")
    plus_rcls = Plus(rcls_strm_line, rcls_strm_poly)
    plus_rcls.save(workspace_temp + r"\plus_rcls")
    strm_mask = Reclassify(plus_rcls, "VALUE", RemapValue([[0, 0], [1,1], [2,1]]))
    strm_mask.save(workspace_temp + r"\strm_mask")
    remove_strm = Con(strm_mask, 0, in_canopy, "VALUE = 1")
    remove_strm.save(workspace_temp + r"\remove_strm")
    veg_div = Divide(remove_strm, 10.0)
    veg_div.save(workspace_temp + r"\veg_div")
    elev_vegtopo = Plus(veg_div, in_dem)
    elev_vegtopo.save(workspace_temp + r"\elev_vegtopo")

    # calculate mean solar radiation per bankfull buffer
    area_solar = AreaSolarRadiation(elev_vegtopo, latitude, sky_size, time_config, day_intv, hour_intv)
    area_solar.save(workspace_temp + r"\area_solar")
    zstat_result = "in_memory\\zstat_result"
    ZonalStatisticsAsTable(seg_poly, "JOIN_FID", area_solar, zstat_result, "DATA", "MEAN")
    arcpy.AddField_management("in_strm_line_lyr", "area_solar", "DOUBLE")
    arcpy.JoinField_management("in_strm_line_lyr", in_stream_oid, zstat_result, "JOIN_FID", ["MEAN"])
    arcpy.CalculateField_management("in_strm_line_lyr","area_solar","!MEAN!", "PYTHON_9.3")
    arcpy.DeleteField_management("in_strm_line_lyr", ["MEAN"])
    arcpy.CopyFeatures_management("in_strm_line_lyr", out_fc)

    # clean up in_memory files
    u.clear_inmem()

    # finalize and write metadata file
    strToolStatus = "Success"
    mWriter.finalizeRun(strToolStatus)
    mWriter.writeMetadataFile(out_meta)

    arcpy.CheckInExtension("Spatial")

    return result


main(in_dem, in_canopy, in_stream, in_strm_indx, in_strm_area, result, workspace_temp, time_config, day_intv, hour_intv, out_meta)

# TESTING
# in_dem = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\elev10m_HUtest.tif"
# in_canopy = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\nbcd_HUtest.tif"
# in_stream = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\segments_200m_20161013.gdb\seg200m_HUtest"
# in_strm_indx = "LineOID"
# in_strm_area = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\NHDArea_HUtest.shp"
# result = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\solar_20161019.gdb\solar_006"
# workspace_temp = r"C:\JL\Testing\solar\Lemhi_Full\test_20161019\scratch_006.gdb"
# time_config = "TimeMultiDays(2015, 182, 183)"
# day_intv = "7"
# hour_intv = "14"