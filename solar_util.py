# file name:	solar_util.py
# description:	This file includes functions that serve as data-processing utilities, primarily for the solar_predict.py
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, GNAT
# version:		0.1

import sys, arcpy
from arcpy.sa import *
sys.path.append(r'C:\repo\gnat')
import DividePolygonBySegment as divPoly

def convert_raster(in_dem, in_bf, in_strm):
	arcpy.AddMessage("Preparing the stream network...")
	arcpy.MakeFeatureLayer_management(in_strm, "in_strm_lyr")
	arcpy.MakeFeatureLayer_management(in_bf, "in_bf_lyr")

	# convert streams to a raster format
	desc = arcpy.Describe(in_dem)
	cellSize = desc.meanCellHeight
	arcpy.AddMessage("Converting stream polyline vectors to raster...")
	arcpy.AddField_management("in_strm_lyr", "VAL", "SHORT")
	arcpy.CalculateField_management("in_strm_lyr", "VAL", "1", "PYTHON_9.3")
	arcpy.PolylineToRaster_conversion("in_strm_lyr", "VAL", r"in_memory\strm_ras", "", "", cellSize)

	# convert bankful polygon
	arcpy.AddMessage("Converting bankfull polygon vectors to raster...")
	arcpy.AddField_management("in_bf_lyr", "VAL", "SHORT")
	arcpy.CalculateField_management("in_bf_lyr", "VAL", "1", "PYTHON_9.3")
	arcpy.PolygonToRaster_conversion("in_bf_lyr", "VAL", r"in_memory\bf_ras", "CELL_CENTER", "", cellSize)

	# Mosaic stream and bankful rasters
	arcpy.AddMessage("Merging stream and bankfull rasters together...")
	strm_final = arcpy.MosaicToNewRaster_management(r"in_memory\bf_ras;in_memory\strm_ras", 
													"in_memory", 
													"strm_final", 
													"", 
													"8_BIT_UNSIGNED", 
													cellSize, 
													1, 
													"LAST")
	return strm_final

def split_bf(in_strm, in_bf):
	arcpy.AddMessage("Segmenting bankfull polygon by stream segments...")
	out_bf = "in_memory\\bf_seg"
	divPoly.main(in_strm, in_bf, out_bf)
	return out_bf