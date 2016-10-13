# file name:	solar_util.py
# description:	This file includes functions that serve as data-processing utilities, primarily for the solar_predict.py
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension

import arcpy
from arcpy.sa import *

def convert_raster(in_dem, in_strm, in_strm_area, workspace_temp):
    # convert streams and stream area polygons to a single raster dataset
    desc = arcpy.Describe(in_dem)
    cellSize = desc.meanCellHeight
    in_strm_oid = arcpy.Describe(in_strm).OIDFieldName
    in_strm_area_oid = arcpy.Describe(in_strm_area).OIDFieldName
    arcpy.AddMessage("Converting stream polyline and area vectors to raster format...")
    strm_ras = workspace_temp + r"\strm_ras"
    arcpy.PolylineToRaster_conversion(in_strm, in_strm_oid, strm_ras, "", "", cellSize)
    poly_ras = workspace_temp + r"\poly_ras"
    arcpy.PolygonToRaster_conversion(in_strm_area, in_strm_area_oid, poly_ras, "CELL_CENTER", "", cellSize)
    strm_poly = workspace_temp + r"\strm_poly"
    # Create stream area polygon for summarizing solar values later
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
    strm_area_ras = workspace_temp + r"\strm_area_ras"
    arcpy.PolygonToRaster_conversion(dslv_poly, "VAL", strm_area_ras, "CELL_CENTER", "", cellSize)

    return dslv_poly, strm_area_ras


def clear_inmem():
    arcpy.env.workspace = r"IN_MEMORY"
    arcpy.AddMessage("Deleting in_memory data...")

    list_fc = arcpy.ListFeatureClasses()
    list_tbl = arcpy.ListTables()

    ### for each FeatClass in the list of fcs's, delete it.
    for f in list_fc:
        arcpy.Delete_management(f)
        ### for each TableClass in the list of tab's, delete it.
    for t in list_tbl:
        arcpy.Delete_management(t)


# This is a modified version of the changeStartingVertex function pulled from
# geometry_functions module in the Geomorphic Network and Analysis Toolbox (GNAT),
# which can be found at: https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox
def changeStartingVertex(fcInputPoints,
                         fcInputPolygons):

    ## Create Geometry Object for Processing input points.
    g = arcpy.Geometry()
    geomPoints = arcpy.CopyFeatures_management(fcInputPoints, g)

    listPointCoords = []
    for point in geomPoints:
        listPointCoords.append([point.centroid.X, point.centroid.Y])
        # arcpy.AddMessage(str(point.centroid.X) + ","+ str(point.centroid.Y))

    with arcpy.da.UpdateCursor(fcInputPolygons, ["OID@", "SHAPE@"]) as ucPolygons:
        for featPolygon in ucPolygons:
            vertexList = []
            # arcpy.AddMessage("Feature: " + str(featPolygon[0]))
            i = 0
            iStart = 0
            for polygonVertex in featPolygon[1].getPart(0):  # shape,firstpart
                if polygonVertex:
                    # arcpy.AddMessage(' Vertex:' + str(i))
                    vertexList.append([polygonVertex.X, polygonVertex.Y])
                    if [polygonVertex.X, polygonVertex.Y] in listPointCoords:
                        # arcpy.AddMessage("  Point-Vertex Match!")
                        iStart = i
                    else:
                        pass
                        # arcpy.AddMessage("  No Match")
                i = i + 1
            if iStart == 0:
                newVertexList = vertexList
                # arcpy.AddMessage("No Change for: " + str(featPolygon[0]))
            else:
                # arcpy.AddMessage("Changing Vertex List for: " + str(featPolygon[0]))
                newVertexList = vertexList[iStart:i] + vertexList[0:iStart]
                for v in newVertexList:
                    arcpy.AddMessage(str(v[0]) + "," + str(v[1]))
                # listVertexPointObjects = []
                newShapeArray = arcpy.Array()
                for newVertex in newVertexList:
                    # arcpy.AddMessage("Changing Vertex: " + str(newVertex[0]) + ',' + str(newVertex[1]))
                    newShapeArray.add(arcpy.Point(newVertex[0], newVertex[1]))
                    # listVertexPointObjects.append(arcpy.Point(newVertex[0],newVertex[1]))
                # newShapeArray = arcpy.Array(listVertexPointObjects)
                newPolygonArray = arcpy.Polygon(newShapeArray)

                ucPolygons.updateRow([featPolygon[0], newPolygonArray])

    return


# This is a modified version of the DividePolygonBySegment module from the
# Geomorphic Network and Analysis Toolbox (GNAT), which can be found at:
# https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox
def divide_polygon(fcInputCenterline, fcInputPolygon, workspaceTemp,
                   dblPointDensity=10.0, dblJunctionBuffer=120.00):
    arcpy.AddMessage("Dividing stream area by segments...")

    arcpy.env.OutputMFlag = "Disabled"
    arcpy.env.OutputZFlag = "Disabled"

    ## Copy centerline to temporary workspace
    fcCenterline = workspaceTemp + r"\GNAT_DPS_Centerline"
    arcpy.CopyFeatures_management(fcInputCenterline, fcCenterline)

    ## Build Thiessan polygons
    arcpy.env.extent = fcInputPolygon  # Set extent to build Thiessan polygons over line network.
    arcpy.Densify_edit(fcCenterline, "DISTANCE", str(dblPointDensity) + " METERS")

    fcTribJunctionPoints = workspaceTemp + r"\GNAT_DPS_TribJunctionPoints"
    arcpy.Intersect_analysis(fcCenterline, fcTribJunctionPoints, output_type="POINT")

    fcThiessanPoints = workspaceTemp + r"\GNAT_DPS_ThiessanPoints"
    arcpy.FeatureVerticesToPoints_management(fcCenterline, fcThiessanPoints, "ALL")

    lyrThiessanPoints = "lyrThiessanPoints"
    arcpy.MakeFeatureLayer_management(fcThiessanPoints, lyrThiessanPoints)
    arcpy.SelectLayerByLocation_management(lyrThiessanPoints, "INTERSECT", fcTribJunctionPoints,
                                           str(dblJunctionBuffer) + " METERS", "NEW_SELECTION")

    fcThiessanPoly = workspaceTemp + r"\GNAT_DPS_ThiessanPoly"
    arcpy.CreateThiessenPolygons_analysis(lyrThiessanPoints, fcThiessanPoly, "ONLY_FID")

    fcThiessanPolyClip = workspaceTemp + r"\GNAT_DPS_TheissanPolyClip"
    arcpy.Clip_analysis(fcThiessanPoly, fcInputPolygon, fcThiessanPolyClip)

    # Code to split the junction Thiessan polygons
    lyrTribThiessanPolys = "lyrTribThiessanPolys"
    arcpy.MakeFeatureLayer_management(fcThiessanPolyClip, lyrTribThiessanPolys)
    arcpy.SelectLayerByLocation_management(lyrTribThiessanPolys, "INTERSECT", fcTribJunctionPoints,
                                           selection_type="NEW_SELECTION")

    fcSplitPoints = workspaceTemp + r"\GNAT_DPS_SplitPoints"
    arcpy.Intersect_analysis([lyrTribThiessanPolys, fcCenterline], fcSplitPoints, output_type="POINT")

    changeStartingVertex(fcTribJunctionPoints, lyrTribThiessanPolys)

    fcThiessanTribPolyEdges = workspaceTemp + r"\GNAT_DPS_ThiessanTribPolyEdges"
    arcpy.FeatureToLine_management(lyrTribThiessanPolys, fcThiessanTribPolyEdges)

    fcSplitLines = workspaceTemp + r"\GNAT_DPS_SplitLines"
    arcpy.SplitLineAtPoint_management(fcThiessanTribPolyEdges, fcSplitPoints, fcSplitLines, "0.1 METERS")

    fcMidPoints = workspaceTemp + r"\GNAT_DPS_MidPoints"
    arcpy.FeatureVerticesToPoints_management(fcSplitLines, fcMidPoints, "MID")
    arcpy.Near_analysis(fcMidPoints, fcTribJunctionPoints, location="LOCATION")
    arcpy.AddXY_management(fcMidPoints)

    fcTribToMidLines = workspaceTemp + r"\GNAT_DPS_TribToMidLines"
    arcpy.XYToLine_management(fcMidPoints, fcTribToMidLines, "POINT_X", "POINT_Y", "NEAR_X", "NEAR_Y")

    ### Select Polys by Centerline ###
    fcThiessanEdges = workspaceTemp + r"\GNAT_DPS_ThiessanEdges"
    arcpy.FeatureToLine_management(fcThiessanPolyClip, fcThiessanEdges)

    fcAllEdges = workspaceTemp + r"\GNAT_DPS_AllEdges"
    arcpy.Merge_management([fcTribToMidLines, fcThiessanEdges, fcCenterline],
                           fcAllEdges)  # include fcCenterline if needed

    fcAllEdgesPolygons = workspaceTemp + r"\GNAT_DPS_AllEdgesPolygons"
    arcpy.FeatureToPolygon_management(fcAllEdges, fcAllEdgesPolygons)

    fcAllEdgesPolygonsClip = workspaceTemp + r"\GNAT_DPS_AllEdgesPolygonsClip"
    arcpy.Clip_analysis(fcAllEdgesPolygons, fcInputPolygon, fcAllEdgesPolygonsClip)

    fcPolygonsJoinCenterline = workspaceTemp + r"\GNAT_DPS_PolygonsJoinCenterline"
    arcpy.SpatialJoin_analysis(fcAllEdgesPolygonsClip,
                               fcCenterline,
                               fcPolygonsJoinCenterline,
                               "JOIN_ONE_TO_MANY",
                               "KEEP_ALL",
                               match_option="SHARE_A_LINE_SEGMENT_WITH")

    fcPolygonsDissolved = workspaceTemp + r"\GNAT_DPS_PolygonsDissolved"
    arcpy.Dissolve_management(fcPolygonsJoinCenterline,
                              fcPolygonsDissolved,
                              "JOIN_FID",
                              multi_part="SINGLE_PART")

    lyrPolygonsDissolved = "lyrPolygonsDissolved"
    arcpy.MakeFeatureLayer_management(fcPolygonsDissolved, lyrPolygonsDissolved)
    arcpy.SelectLayerByAttribute_management(lyrPolygonsDissolved, "NEW_SELECTION", """ "JOIN_FID" = -1 """)

    fcSegmentedPolygons = workspaceTemp + r"\GNAT_DPS_PolygonsSegmented"
    arcpy.Eliminate_management(lyrPolygonsDissolved, fcSegmentedPolygons, "LENGTH")

    return fcSegmentedPolygons