# file name:	solar_vector.py
# description:	The Solar Insolation for a Stream Network tool calculates solar insolation for a user-supplied stream
#               network. The tool assumes that the stream network has been previously segmented.  Solar insolation is
#			    calculated per stream network segment. The end result of this tool and the Generate Solar Insolation for
#               a Stream Network is a model of mean solar radiation hitting each stream segment by creating a coarse.
#               approximation of shading based on topography and vegetation.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, util.py


import arcpy, os
import sys
import gc
import time
from arcpy.sa import *
import util as u
import metadata.meta_sfr as meta_sfr
import metadata.meta_rs as meta_rs
import riverscapes as rs

# set environmental variables
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# set input variables
in_raster = arcpy.GetParameterAsText(0) # Raster dataset representing solar insolation, output from solar_raster.py
in_stream = arcpy.GetParameterAsText(1) # Segmented stream network as a vector dataset.
in_strm_indx = arcpy.GetParameterAsText(2) # Unique ID field for segmented stream network (i.e. "LineOID")
in_strm_area = arcpy.GetParameterAsText(3) # Polygon representing open water areas of the stream (i.e. NHD Area)
result = arcpy.GetParameterAsText(4)  # Feature class that is the final output of the model.
workspace_temp = arcpy.GetParameterAsText(5) #
rs_bool = arcpy.GetParameterAsText(6) # Boolean value indicates if this is a Riverscapes project.
rs_dir = arcpy.GetParameterAsText(7) # Directory where Riverscapes project files are stored
rs_real_name = arcpy.GetParameterAsText(8) # Riverscapes project realization name.


def metadata(solarXML, in_raster, in_stream, in_strm_area, out_fc, real_id):
    """ Builds and writes an XML file according to the Riverscapes Project specifications

        Args:
            ecXML: Project XML object instance
    """

    # Finalize metadata
    timeStart, timeStop = solarXML.finalize()

    solarXML.getOperator()
    # add Realization input tags
    solarXML.addRealizationInputRef(solarXML.project, "Raster", "Solar", real_id, "SOL_RAS")
    solarXML.addMeta("solar_vector Start Time", timeStart, solarXML.project, "Solar", real_id)
    solarXML.addMeta("solar_vector Stop Time", timeStop, solarXML.project, "Solar", real_id)

    # add Analysis output tags
    solarXML.addOutput("Vector",
                       "Output polyline feature with solar values",
                       out_fc,
                       solarXML.project,
                       "Solar",
                       real_id,
                       "PRED_SOLAR",
                       solarXML.getUUID())
    solarXML.write()
    return


def main(in_raster, in_stream, in_strm_indx, in_strm_area, out_fc):
    # set environmental variables
    arcpy.env.outputCoordinateSystem = in_raster
    arcpy.env.snapRaster = in_raster
    arcpy.env.mask = in_raster
    desc = arcpy.Describe(in_raster)
    cellSize = desc.meanCellHeight
    arcpy.env.cellSize = cellSize
    arcpy.env.workspace = workspace_temp
    arcpy.env.scratchWorkspace = workspace_temp

    in_ras = arcpy.sa.Raster(in_raster)
    in_ras_extent = in_ras.extent
    arcpy.env.extent = in_ras_extent

    in_raster_name = os.path.basename(in_raster)
    in_stream_name = os.path.basename(in_stream)
    in_strm_area_name = os.path.basename(in_strm_area)
    out_dir = os.path.dirname(result)
    out_fc_name = os.path.basename(result)

    # start writing metadata
    time_stamp = time.strftime("%Y%m%d%H%M")
    out_xml = os.path.join(out_dir, "{0}_{1}.{2}".format("meta_solarVector", time_stamp, "xml"))
    mWriter = meta_sfr.MetadataWriter("Predict Solar Insolation for a Stream Network", "0.4")
    mWriter.createRun()
    mWriter.currentRun.addParameter("Solar insolation raster dataset", in_raster)
    mWriter.currentRun.addParameter("Stream network feature class", in_stream)
    mWriter.currentRun.addParameter("Stream unique ID field", in_strm_indx)
    mWriter.currentRun.addParameter("Stream area polygon feature class", in_strm_area)
    mWriter.currentRun.addOutput("Output polyline feature class with solar values", out_fc)
    mWriter.currentRun.addOutput("Metadata XML file", out_xml)

    # get OID of segmented stream network
    in_stream_oid = arcpy.Describe(in_stream).OIDFieldName

    if u.checkLineOID(in_stream) == True:
        gc.enable()

        # initiate Riverscapes project XML object and start processing timestamp
        if rs_bool == "true":
            rs_xml = "{0}\\{1}".format(rs_dir, "project.rs.xml")
            projectXML = meta_rs.ProjectXML("solar_vector", rs_xml)

        # convert stream and stream area polygon to two-class raster dataset
        arcpy.AddMessage("Processing stream segments...")
        tmp_stream_line = arcpy.FeatureClassToFeatureClass_conversion(in_stream, workspace_temp, "tmp_stream_line")
        tmp_stream_poly = arcpy.FeatureClassToFeatureClass_conversion(in_strm_area, workspace_temp, "tmp_strm_poly")
        arcpy.MakeFeatureLayer_management(tmp_stream_line, "in_strm_line_lyr")
        arcpy.MakeFeatureLayer_management(tmp_stream_poly, "in_strm_poly_lyr")
        poly_strm_area, strm_ras, poly_ras = u.raster_poly(in_raster, "in_strm_line_lyr", "in_strm_poly_lyr", workspace_temp)
        arcpy.CalculateStatistics_management(strm_ras)
        arcpy.CalculateStatistics_management(poly_ras)
        strm_ras_lyr = "strm_ras_lyr"
        poly_ras_lyr = "poly_ras_lyr"
        arcpy.MakeRasterLayer_management(strm_ras, strm_ras_lyr)
        arcpy.MakeRasterLayer_management(poly_ras, poly_ras_lyr)

        # buffer stream segments
        seg_poly = u.divide_polygon(in_stream, poly_strm_area, workspace_temp)
        arcpy.env.extent = in_ras_extent # reset because the divide_polygon function sets it to the stream area polygon extent

        # calculate solar values per stream segment
        arcpy.AddMessage("Summarizing solar values per stream segment...")
        zstat_result = workspace_temp + "\\zstat_result"
        ZonalStatisticsAsTable(seg_poly, "JOIN_FID", in_raster, zstat_result, "DATA", "MEAN")
        arcpy.AddField_management("in_strm_line_lyr", "area_solar", "DOUBLE")
        arcpy.JoinField_management("in_strm_line_lyr", in_stream_oid, zstat_result, "JOIN_FID", ["MEAN"])
        arcpy.CalculateField_management("in_strm_line_lyr","area_solar","!MEAN!", "PYTHON_9.3")
        arcpy.DeleteField_management("in_strm_line_lyr", ["MEAN"])
        arcpy.CopyFeatures_management("in_strm_line_lyr", out_fc)
        arcpy.AddMessage("Tool output saved to " + out_fc)

        # finalize and write metadata file
        strToolStatus = "Success"
        mWriter.finalizeRun(strToolStatus)
        mWriter.writeMetadataFile(out_xml)

        # export data files to Riverscapes project.
        if rs_bool == "true":
            arcpy.AddMessage("Exporting to Riverscapes project...")
            real_id = projectXML.realIDdict[rs_real_name]
            # copy input/output data to Riverscapes project directories
            abs_ras_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_raster_name)
            abs_strm_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_stream_name)
            abs_strm_area_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_strm_area_name)
            abs_out_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 2, real_id), out_fc_name)
            rs.copyRSFiles(in_raster, abs_ras_path)
            rs.copyRSFiles(in_stream, abs_strm_path)
            rs.copyRSFiles(in_strm_area, abs_strm_area_path)
            rs.copyRSFiles(out_fc, abs_out_path)
            # write project XML file. Note the use of the 'relative path version' of get directories function
            rel_ras_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_raster_name)
            rel_strm_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_stream_name)
            rel_strm_area_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_strm_area_name)
            rel_out_path = os.path.join(rs.getRSDirRel(1, 2, real_id), out_fc_name)
            metadata(projectXML, rel_ras_path, rel_strm_path, rel_strm_area_path, rel_out_path, real_id)

        # clean up in_memory files
        u.clear_inmem()

    else:
        arcpy.AddError("The LineOID attribute field is missing from " + in_stream + ". Cancelling process!")
        sys.exit(0)

    arcpy.CheckInExtension("Spatial")

    return


if __name__ == "__main__":
    main(in_raster, in_stream, in_strm_indx, in_strm_area, result)