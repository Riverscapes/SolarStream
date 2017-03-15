# file name:	solar_raster.py
# description:	This tool calculates solar insolation for a user-supplied raster. The tool automates the process of adding
#               a raster representing vegetation height to a topographic DEM raster, then using this raster to generate a
#               solar insolation raster dataset for a user-defined time period and interval.  The Generate Solar Insolation
#               Surface tool relies heavily on ESRI's Area Solar Radiation tool.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, util.py
# version:		0.5.4
import arcpy
import os
import time
from arcpy.sa import *
import util as u
import metadata.meta_rs as meta_rs
import metadata.meta_sfr as meta_sfr
import riverscapes as rs

version = "0.5.4"

# set environmental variables
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

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
    solarXML.addRealization(real_name, real_id, timeStop, version, solarXML.getUUID())
    solarXML.addMeta("Operator", solarXML.operator, solarXML.project, "Solar", real_id)
    solarXML.addMeta("ComputerID", solarXML.computerID, solarXML.project, "Solar", real_id)
    solarXML.addMeta("solar_raster Start Time", timeStart, solarXML.project, "Solar", real_id)
    solarXML.addMeta("solar_raster Stop Time", timeStop, solarXML.project, "Solar", real_id)
    # Add Parameter tags
    solarXML.addParameter("Time configuration", time_config, solarXML.project, "Solar", real_id)
    solarXML.addParameter("Day interval", day_intv, solarXML.project, "Solar", real_id)
    solarXML.addParameter("Hour interval", hour_intv, solarXML.project, "Solar", real_id)
    # Add Realization input tags
    solarXML.addRealizationInputRef(solarXML.project, "Raster", "Solar", real_id, "DEM")
    solarXML.addRealizationInputData(solarXML.project, "Raster", "Solar", real_id, "Vegetation height raster dataset", in_canopy,
                                 solarXML.getUUID())
    solarXML.addRealizationInputData(solarXML.project, "Vector", "Solar", real_id, "Stream network polyline feature class", in_stream,
                                 solarXML.getUUID())
    solarXML.addRealizationInputData(solarXML.project, "Vector", "Solar", real_id, "Stream area polygon feature class", in_strm_area,
                                 solarXML.getUUID())
    # Add Analysis output tags
    solarXML.addOutput("Raster", "Solar insolation raster dataset", result, solarXML.realizations, "Solar", real_id, "SOL_RAS",
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
    out_dir = os.path.dirname(out_raster)

    in_dem_name = os.path.basename(in_dem)
    in_canopy_name = os.path.basename(in_canopy)
    in_stream_name = os.path.basename(in_stream)
    in_strm_area_name = os.path.basename(in_strm_area)
    out_raster_name = os.path.basename(out_raster)

    # initiate generic metadata XML object
    time_stamp = time.strftime("%Y%m%d%H%M")
    out_xml = os.path.join(out_dir, "{0}_{1}.{2}".format("meta_solarRaster", time_stamp, "xml"))
    mWriter = meta_sfr.MetadataWriter("Calculate Solar Insolation for a Stream Network", version)
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
        rs_xml = "{0}\\{1}".format(rs_dir, "project.rs.xml")
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
    area_solar = AreaSolarRadiation(elev_vegtopo, latitude, sky_size, time_config, day_intrvl, hour_intrvl)
    area_solar.save(out_raster)
    arcpy.AddMessage("Tool output saved to " + out_raster)

    # Riverscapes project processing
    if rs_bool == "true":
        arcpy.AddMessage("Exporting as a Riverscapes project...")
        real_id = rs.getRealID(time_stamp)
        # copy input/output data to Riverscapes project directories
        abs_dem_path = os.path.join(rs.getRSDirAbs(rs_dir, 0), in_dem_name)
        abs_canopy_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_canopy_name)
        abs_stream_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_stream_name)
        abs_strm_area_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_strm_area_name)
        abs_solar_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 1, real_id), out_raster_name)
        rs.writeRSDirs(rs_dir, real_id)
        rs.copyRSFiles(in_dem, abs_dem_path)
        rs.copyRSFiles(in_canopy, abs_canopy_path)
        rs.copyRSFiles(in_stream, abs_stream_path)
        rs.copyRSFiles(in_strm_area, abs_strm_area_path)
        rs.copyRSFiles(out_raster, abs_solar_path)
        # write project XML file. Note the use of the 'relative path version' of get directories function
        rel_dem_path = os.path.join(rs.getRSDirRel(0), in_dem_name)
        rel_canopy_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_canopy_name)
        rel_stream_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_stream_name)
        rel_strm_area_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_strm_area_name)
        rel_solar_path = os.path.join(rs.getRSDirRel(1, 1, real_id), out_raster_name)
        metadata(projectXML,
                 rel_dem_path,
                 rel_canopy_path,
                 rel_stream_path,
                 rel_strm_area_path,
                 time_config,
                 day_intrvl,
                 hour_intrvl,
                 rel_solar_path,
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

    return


# if __name__ == "__main__":
#     main(in_dem,
#          in_canopy,
#          in_stream,
#          in_strm_area,
#          workspace_temp,
#          time_config,
#          day_intv,
#          hour_intv,
#          result,
#          rs_bool,
#          wshd_name,
#          rs_proj_name,
#          rs_real_name,
#          rs_dir)