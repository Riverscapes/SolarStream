import os
import shutil
import arcpy

arcpy.env.overwriteOutput = True

# constants
RS_SUBDIRS = ["ProjectInputs", "Realizations"] # directories in the Riverscape Project root
RS_OUTDIRS = ["Inputs", "SolarRasterOutput", "SolarVectorOutput"] # directories storing Riverscape realization inputs/outputs

HUCID_DICT = {"Big-Navarro-Garcia":"18010108",
              "Clearwater":"17060306",
              "Entiat":"17020010",
              "Hells Canyon":"17060101",
              "Imnaha":"17060102",
              "Klickitat":"17070106",
              "Lemhi":"17060204",
              "Little Salmon":"17060210",
              "Lochsa":"17060303",
              "Lolo Creek": "1706030602",
              "Lower John Day":"17070204",
              "Lower North Fork Clearwater":"17060308",
              "Lower Salmon":"17060209",
              "Lower Selway": "17060302",
              "Lower Snake-Asotin":"17060103",
              "Lower Snake-Tucannon": "17060107",
              "Lower Yakima":"17030003",
              "Methow":"17020008",
              "Middle Fork Clearwater" : "17060304",
              "Middle Fork John Day":"17070203",
              "Middle Salmon-Panther":"17060203",
              "Minam":"1706010505",
              "North Fork John Day":"17070202",
              "Okanogan":"17020006",
              "Pahsimeroi":"17060202",
              "South Fork Clearwater":"17060305",
              "South Fork Salmon":"17060208",
              "Umatilla":"17070103",
              "Upper John Day":"17070201",
              "Upper Grande Ronde":"17060104",
              "Upper Middle Fork Salmon":"17060205",
              "Upper North Fork Clearwater":"17060307",
              "Upper Selway":"17060301",
              "Upper Yakima":"17030001",
              "Walla Walla":"17070102",
              "Wallowa":"17060105",
              "Wenatchee":"17020011"}


def writeRSRoot(rs_root):
    if os.path.exists(rs_root):
        shutil.rmtree(rs_root)
        os.mkdir(rs_root)
        os.chmod(rs_root, 0o777)
    else:
        os.mkdir(rs_root)
        os.chmod(rs_root, 0o777)


def writeRSDirs(rs_root):
    """Writes optional Riverscape project file folders"""
    for subdir in RS_SUBDIRS:
        os.makedirs(os.path.join(rs_root, subdir))


def writeRealDir(rs_root, real_id):
    for outdir in RS_OUTDIRS:
        os.makedirs(os.path.join(rs_root, RS_SUBDIRS[1], real_id, outdir))


def copyRSFiles(from_file, out_file):
    from_desc = arcpy.Describe(from_file)
    if from_desc.dataType == "DbaseTable":
        arcpy.MakeTableView_management(from_file, "from_file_view")
        arcpy.CopyRows_management("from_file_view", out_file)
        arcpy.Delete_management("from_file_view")
    elif from_desc.dataType == "FeatureClass" or from_desc.dataType == "ShapeFile":
        arcpy.MakeFeatureLayer_management(from_file, "from_file_lyr")
        arcpy.CopyFeatures_management("from_file_lyr", out_file)
        arcpy.Delete_management("from_file_lyr")
    elif from_desc.dataType == "RasterDataset":
        arcpy.MakeRasterLayer_management(from_file, "from_ras_lyr")
        arcpy.CopyRaster_management("from_ras_lyr", out_file)
        arcpy.Delete_management("from_ras_lyr")


def getRSDirAbs(root, subdir_index='', outdir_index='', real_id=''):
    if subdir_index != '' and outdir_index != '':
        return os.path.join(root, RS_SUBDIRS[subdir_index], real_id, RS_OUTDIRS[outdir_index]) # Realizations folder
    if subdir_index != '' and outdir_index == '':
        return os.path.join(root, RS_SUBDIRS[subdir_index]) # Inputs folder


def getRSDirRel(subdir_index='', outdir_index='', real_id=''):
    if subdir_index != '' and outdir_index != '':
        return os.path.join(RS_SUBDIRS[subdir_index], real_id, RS_OUTDIRS[outdir_index]) # Realizations folder
    if subdir_index != '' and outdir_index == '':
        return RS_SUBDIRS[subdir_index] # Inputs folder


def getHUCID(wshd_name):
    huc_id = HUCID_DICT[wshd_name]
    return huc_id


def getRealID(timestamp):
    return "{0}{1}".format("run", timestamp)