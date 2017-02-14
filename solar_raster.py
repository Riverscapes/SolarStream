# file name:	solar_raster.py
# description:	This tool calculates solar insolation for a user-supplied raster. The tool automates the process of adding
#               a raster representing vegetation height to a topographic DEM raster, then using this raster to generate a
#               solar insolation raster dataset for a user-defined time period and interval.  The Generate Solar Insolation
#               Surface tool relies heavily on ESRI's Area Solar Radiation tool.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, util.py
# version:		0.5

import arcpy
import os
import time
from arcpy.sa import *
import util as u
import metadata.meta_rs as meta_rs
import metadata.meta_sfr as meta_sfr
import riverscapes as rs

# set environmental variables
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# # set input variables
in_dem = arcpy.GetParameterAsText(0) # input raster dataset represents "bare earth" topographic surface.
in_canopy = arcpy.GetParameterAsText(1) # input raster dataset represents vegetation or canopy height
in_stream = arcpy.GetParameterAsText(2) # segmented stream network as vector dataset.
in_strm_area = arcpy.GetParameterAsText(3) # polygon representing open water areas of the stream (i.e. bankfull)
time_config = arcpy.GetParameterAsText(4) # time period for calculating solar radiation.
day_intv = arcpy.GetParameterAsText(5) # time interval (by days) used for calculation of sky vectors.
hour_intv = arcpy.GetParameterAsText(6)  # time interval (by hour) used for calculating sky vectors.
result = arcpy.GetParameterAsText(7)  # raster dataset that is the final output of the model.
workspace_temp = arcpy.GetParameterAsText(8)
rs_bool = arcpy.GetParameterAsText(9) # boolean parameter indicates Riverscape project output requirement.
wshd_name = arcpy.GetParameterAsText(10) # name of project watershed. required for Riverscape XML file.
rs_proj_name = arcpy.GetParameterAsText(11) # Riverscapes project name
rs_real_name = arcpy.GetParameterAsText(12) # Riverscapes realization name
rs_dir = arcpy.GetParameterAsText(13) # directory where Riverscape project files will be written.=

# get output directory
out_dir = os.path.dirname(result)


def metadata(solarXML,
             in_dem,
             in_canopy,
             in_stream,
             in_strm_area,
             time_config,
             day_intv,
             hour_intv,
             result,
             wshd_name,
             real_name,
             real_id):
    """Builds and writes an XML file according to the Riverscapes Project specifications

        Args:
            solarXML: Project XML object instance
    """

    # Finalize Riverscapes metadata
    timeStart, timeStop= solarXML.finalize()

    solarXML.getOperator()
    # Add Project Meta tags
    huc_id = rs.getHUCID(wshd_name)
    solarXML.addMeta("HUCID", huc_id, solarXML.project)
    solarXML.addMeta("Region", "CRB", solarXML.project)
    solarXML.addMeta("Watershed", wshd_name, solarXML.project)
    # Add Project input tags
    solarXML.addProjectInput("Raster", "Bare earth DEM raster dataset", in_dem, solarXML.project, "DEM", solarXML.getUUID())
    # Add Realization tags
    solarXML.addRealization(real_name, real_id, timeStop, '0.1', solarXML.getUUID())
    solarXML.addMeta("Operator", solarXML.operator, solarXML.project, "SOLAR", real_id)
    solarXML.addMeta("ComputerID", solarXML.computerID, solarXML.project, "SOLAR", real_id)
    solarXML.addMeta("solar_raster Start Time", timeStart, solarXML.project, "SOLAR", real_id)
    solarXML.addMeta("solar_raster Stop Time", timeStop, solarXML.project, "SOLAR", real_id)
    # Add Parameter tags
    solarXML.addParameter("Time configuration", time_config, solarXML.project, "SOLAR", real_id)
    solarXML.addParameter("Day interval", day_intv, solarXML.project, "SOLAR", real_id)
    solarXML.addParameter("Hour interval", hour_intv, solarXML.project, "SOLAR", real_id)
    # Add Realization input tags
    solarXML.addRealizationInputRef(solarXML.project, "Raster", "SOLAR", real_id, "DEM")
    solarXML.addRealizationInputData(solarXML.project, "Raster", "SOLAR", real_id, "Vegetation height raster dataset", in_canopy,
                                 solarXML.getUUID())
    solarXML.addRealizationInputData(solarXML.project, "Vector", "SOLAR", real_id, "Stream network polyline feature class", in_stream,
                                 solarXML.getUUID())
    solarXML.addRealizationInputData(solarXML.project, "Vector", "SOLAR", real_id, "Stream area polygon feature class", in_strm_area,
                                 solarXML.getUUID())
    # Add Analysis output tags
    solarXML.addOutput("Raster", "Solar insolation raster dataset", result, solarXML.realizations, "SOLAR", real_id, "SOL_RAS",
                       solarXML.getUUID())
    solarXML.write()


def main(in_dem,
         in_canopy,
         in_stream,
         in_strm_area,
         workspace_temp,
         time_config,
         day_intrvl,
         hour_intrvl,
         out_raster,
         rs_bool,
         wshd_name='',
         proj_name='',
         real_name='',
         rs_dir=''):

    # set environmental variables
    arcpy.env.outputCoordinateSystem = in_dem
    arcpy.env.snapRaster = in_dem
    arcpy.env.mask = in_dem
    desc = arcpy.Describe(in_dem)
    cellSize = desc.meanCellHeight
    arcpy.env.cellSize = cellSize
    arcpy.env.workspace = workspace_temp
    arcpy.env.scratchWorkspace = workspace_temp
    in_ras = arcpy.sa.Raster(in_dem)
    in_ras_extent = in_ras.extent
    arcpy.env.extent = in_ras_extent

    in_dem_name = os.path.basename(in_dem)
    in_canopy_name = os.path.basename(in_canopy)
    in_stream_name = os.path.basename(in_stream)
    in_strm_area_name = os.path.basename(in_strm_area)
    out_raster_name = os.path.basename(out_raster)

    # initiate generic metadata XML object
    time_stamp = time.strftime("%Y%m%d%H%M")
    out_xml = os.path.join(out_dir, "{0}_{1}.{2}".format("meta_polystat", time_stamp, "xml"))
    mWriter = meta_sfr.MetadataWriter("Calculate Solar Insolation for a Stream Network", "0.1")
    mWriter.createRun()
    mWriter.currentRun.addParameter("DEM raster", in_dem)
    mWriter.currentRun.addParameter("Canopy height raster", in_canopy)
    mWriter.currentRun.addParameter("Stream network feature class", in_stream)
    mWriter.currentRun.addParameter("Stream area polygon feature class", in_strm_area)
    mWriter.currentRun.addParameter("Scratch workspace", workspace_temp)
    mWriter.currentRun.addParameter("Time configuration", time_config)
    mWriter.currentRun.addParameter("Day interval", day_intrvl)
    mWriter.currentRun.addParameter("Hour interval", hour_intrvl)
    mWriter.currentRun.addOutput("Output solar raster dataset", out_raster)
    mWriter.currentRun.addOutput("Metadata XML file", out_xml)

    # initiate Riverscapes project XML object
    if rs_bool == "true":
        rs.writeRSRoot(rs_dir)
        rs_xml = "{0}\\{1}".format(rs_dir, "solar_project.xml")
        projectXML = meta_rs.ProjectXML("solar_raster", rs_xml, "Solar", proj_name)

    # solar parameters
    sky_size = 400

    # find latitude of the study basin centroid
    wgs84_prj = r"Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj"
    prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], wgs84_prj)
    temp_spRef = arcpy.SpatialReference(prjFile)
    with (arcpy.da.SearchCursor(in_stream, ["SHAPE@Y"], "#", temp_spRef)) as cursor:
        for row in cursor:
            latitude = row[0]

    # convert stream and stream area polygon to two-class raster dataset
    tmp_stream_line = arcpy.FeatureClassToFeatureClass_conversion(in_stream, workspace_temp, "tmp_stream_line")
    tmp_stream_poly = arcpy.FeatureClassToFeatureClass_conversion(in_strm_area, workspace_temp, "tmp_strm_poly")
    arcpy.MakeFeatureLayer_management(tmp_stream_line, "in_strm_line_lyr")
    arcpy.MakeFeatureLayer_management(tmp_stream_poly, "in_strm_poly_lyr")
    poly_strm_area, strm_ras, poly_ras = u.raster_poly(in_dem, "in_strm_line_lyr", "in_strm_poly_lyr",
                                                       workspace_temp)
    arcpy.CalculateStatistics_management(strm_ras)
    arcpy.CalculateStatistics_management(poly_ras)
    strm_ras_lyr = "strm_ras_lyr"
    poly_ras_lyr = "poly_ras_lyr"
    arcpy.MakeRasterLayer_management(strm_ras, strm_ras_lyr)
    arcpy.MakeRasterLayer_management(poly_ras, poly_ras_lyr)

    # prepare elevation data for solar radiation modeling
    arcpy.AddMessage("Calculating solar radiation...")
    rcls_strm_line = Reclassify(strm_ras, "VALUE", RemapValue([[1, 1], ["NODATA", 0]]))
    rcls_strm_line.save(workspace_temp + r"\rcls_strm_line")
    rcls_strm_poly = Reclassify(poly_ras, "VALUE", RemapValue([[1, 1], ["NODATA", 0]]))
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
    area_solar.save(out_raster)
    arcpy.AddMessage("Tool output saved to " + out_raster)

    # Riverscapes output, including project XML and data files
    if rs_bool == "true":
        arcpy.AddMessage("Exporting as a Riverscapes project...")
        real_id = rs.getRealID(time_stamp)
        rs_dem_path = os.path.join(rs.getRSdirs(rs_dir, 0), in_dem_name)
        rs_canopy_path = os.path.join(rs.getRSdirs(rs_dir, 1, 0, real_id), in_canopy_name)
        rs_stream_path = os.path.join(rs.getRSdirs(rs_dir, 1, 0, real_id), in_stream_name)
        rs_strm_area_path = os.path.join(rs.getRSdirs(rs_dir, 1, 0, real_id), in_strm_area_name)
        rs_solar_path = os.path.join(rs.getRSdirs(rs_dir, 1, 1, real_id), out_raster_name)
        rs.writeRSDirs(rs_dir, real_id)
        rs.copyRSFiles(in_dem, rs_dem_path)
        rs.copyRSFiles(in_canopy, rs_canopy_path)
        rs.copyRSFiles(in_stream, rs_stream_path)
        rs.copyRSFiles(in_strm_area, rs_strm_area_path)
        rs.copyRSFiles(out_raster, rs_solar_path)
        metadata(projectXML,
                 rs_dem_path,
                 rs_canopy_path,
                 rs_stream_path,
                 rs_strm_area_path,
                 time_config,
                 day_intv,
                 hour_intv,
                 rs_solar_path,
                 wshd_name,
                 real_name,
                 real_id)

    # clean up in_memory files
    u.clear_inmem()

    # finalize and write generic metadata file
    strToolStatus = "Success"
    mWriter.finalizeRun(strToolStatus)
    mWriter.writeMetadataFile(out_xml)

    arcpy.CheckInExtension("Spatial")

    return result


if __name__ == "__main__":
    main(in_dem,
         in_canopy,
         in_stream,
         in_strm_area,
         workspace_temp,
         time_config,
         day_intv,
         hour_intv,
         result,
         rs_bool,
         wshd_name,
         rs_proj_name,
         rs_real_name,
         rs_dir)