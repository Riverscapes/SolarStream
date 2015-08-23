# file name:	solar_predict.py
# description:	This tool predicts solar insolation for a user-supplied stream network. The tool assumes that the  
#				stream network has been previously segmented. Solar insolation is calculated per stream network    
#				segment. Essentially, this tool attempts to model mean solar radiation hitting each stream segment 
#				by creating a coarse approximation of shading based on topography and vegetation. The tool relies   
#				on ESRI's Area Solar Radiation function.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, solar_util.py
# version:		0.1

import arcpy, os
from arcpy.sa import *
import solar_util as u

# input variables
in_huc = arcpy.GetParameterAsText(0) # Polygon feature class representing the study basin.
in_dem = arcpy.GetParameterAsText(1) # DEM representing "bare earth" topographic surface of study area.
in_canopy = arcpy.GetParameterAsText(2) # Raster dataset representing vegetation or canopy height
in_stream = arcpy.GetParameterAsText(3) # Segmented stream network as a vector dataset.
in_bf = arcpy.GetParameterAsText(4) # Polygon feature class representing bankfull widths for the stream network.
result = arcpy.GetParameterAsText(5)  # Feature class that is the final output of the model.
time_config = arcpy.GetParameterAsText(6) # Time period for calculating solar radiation. Required by AreaSolarRadiation.
day_intv = arcpy.GetParameterAsText(7) # Time interval (by days) used for calculation of sky vectors.
hour_intv = arcpy.GetParameterAsText(8)  # Time interval (by hour) used for calculating sky vectors.

def main(in_dem, in_canopy, in_stream, in_bf, out_fc, time_config, day_intrvl, hour_intrvl):
	# set environmental variables
	arcpy.env.overwriteOutput = True
	arcpy.env.outputCoordinateSystem = in_dem
	arcpy.env.snapRaster = in_dem
	desc = arcpy.Describe(in_dem)
	arcpy.env.cellSize =desc.meanCellHeight
	arcpy.env.mask = in_dem

	# solar parameters (not set by user)
	sky_size = 400

	# convert stream and bankful polygon to two-class raster dataset
	tmp_stream = arcpy.FeatureClassToFeatureClass_conversion(in_stream, "in_memory", "tmp_stream")
	arcpy.MakeFeatureLayer_management(tmp_stream, "in_stream_lyr")
	ras_strm = u.convert_raster(in_dem, in_bf, "in_stream_lyr")

	# split and buffer bankfull polygon based on stream segments
	bf_seg = u.split_bf(in_stream, in_bf)
	bf_buf = arcpy.Buffer_analysis(bf_seg, "in_memory\\bf_seg_buf10m", 10, "FULL")

	# find latitude of the study basin centroid
	prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], r"Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj")
	temp_spRef = arcpy.SpatialReference(prjFile)
	with (arcpy.da.SearchCursor(in_huc,["SHAPE@Y"], "#", temp_spRef)) as cursor:
		for row in cursor:
			latitude = row[0]

	# prepare elevation data for solar radiation modeling
	arcpy.AddMessage("Calculating solar radiation...")
	rcls_strm = Reclassify(ras_strm, "VALUE", RemapValue([[1,1],["NODATA",0]]))
	remove_strm = Con(rcls_strm, 0, in_canopy, "VALUE = 1")
	veg_div = Divide(remove_strm, 10.0)
	elev_vegtopo = Plus(veg_div, in_dem)
	area_solar = AreaSolarRadiation(elev_vegtopo, latitude, sky_size, time_config, day_intv, hour_intv)

	# calculate mean solar radiation per bankfull buffer
	zstat_result = "in_memory\\zstat_result"
	ZonalStatisticsAsTable(bf_buf, "JOIN_FID", area_solar, zstat_result, "DATA", "MEAN")
	arcpy.AddField_management("in_stream_lyr", "area_solar", "DOUBLE")
	arcpy.JoinField_management("in_stream_lyr", "OID", zstat_result, "JOIN_FID", ["MEAN"])
	arcpy.CalculateField_management("in_stream_lyr","area_solar","[MEAN]", "VB")
	arcpy.DeleteField_management("in_stream_lyr", ["MEAN"])
	arcpy.CopyFeatures_management("in_stream_lyr", result)

	# clean up in_memory files
	arcpy.Delete_management("in_memory\\bf_seg_buf10m")
	arcpy.Delete_management("in_memory\\zstat_result")

	return result

main(in_dem, in_canopy, in_stream, in_bf, result, time_config, day_intv, hour_intv)