import os
import arcpy
import metadata.meta_rs as meta
import create_project
import solar_raster
import solar_vector

# CONSTANTS
version = "0.5.6"
list_wshd = ['Big-Navarro-Garcia (CA)',
             'Clearwater',
             'Entiat',
             'Hells Canyon',
             'Imnaha',
             'Little Salmon',
             'Lower John Day',
             'Lower Selway',
             'Lemhi',
             'Lolo Creek',
             'Lower North Fork Clearwater'
             'Lower Salmon',
             'Lower Snake-Asotin',
             'Lower Snake-Tucannon',
             'Methow',
             'Middle Fork Clearwater'
             'Middle Fork John Day',
             'Middle Salmon-Panther',
             'Minam',
             'North Fork John Day',
             'Okanogan',
             'Pahsimeroi',
             'South Fork Clearwater'
             'South Fork Salmon',
             'Umatilla',
             'Upper Grande Ronde',
             'Upper John Day',
             'Upper Middle Fork Salmon',
             'Upper North Fork Clearwater'
             'Walla Walla',
             'Wenatchee',
             'Yankee Fork']


class Toolbox(object):
    def __init__(self):
        self.label = 'Solar Stream Tools'
        self.alias = 'Solar'
        self.tools = [CreateProjectTool, SolarRasterTool, SolarVectorTool]
        self.description = "Modeling solar insolation for a spatially-explicit stream network."


class CreateProjectTool(object):
    def __init__(self):
        self.label = 'Create Riverscapes Project'
        self.description = "This tool creates a new Riverscapes project XML " \
                           "file and associated data directories, based on the " \
                           "Riverscapes protocol."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        reload(create_project)

        param0 = arcpy.Parameter(
            name='rs_dir',
            displayName='Riverscapes workspace',
            parameterType='Required',
            direction='Input',
            datatype='DEWorkspace')
        param0.filter.list = ['File System']

        param1 = arcpy.Parameter(
            name='region_name',
            displayName='Region name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')
        param1.filter.list = ['CRB']

        param2 = arcpy.Parameter(
            name='wshd_name',
            displayName='Watershed name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')
        param2.filter.list = list_wshd

        param3 = arcpy.Parameter(
            name='proj_name',
            displayName='Riverscapes project name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')

        return [param0,
                param1,
                param2,
                param3]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        reload(create_project)
        create_project.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText)
        return


class SolarRasterTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Generate Solar Insolation Surface'
        self.description = "This tool calculates solar insolation for a " \
                           "user-supplied raster. The tool automates the " \
                           "process of adding a raster representing vegetation" \
                           " height to a topographic DEM raster, then using " \
                           "this raster to generate a solar insolation raster" \
                           " for a user-defined time period and interval. The" \
                           " Generate Solar Insolation Surface tool relies " \
                           "heavily on ESRI's Area Solar Radiation tool."
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            name = 'in_dem',
            displayName = 'Bare earth DEM raster dataset',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPRasterLayer')

        param1 = arcpy.Parameter(
            name = 'in_canopy',
            displayName = 'Vegetation height raster dataset',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPRasterLayer')

        param2 = arcpy.Parameter(
            name = 'in_stream',
            displayName = 'Stream network polyline feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPFeatureLayer')
        param2.filter.list = ['Polyline']

        param3 = arcpy.Parameter(
            name = 'in_strm_area',
            displayName = 'Stream area polygon feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPFeatureLayer')
        param3.filter.list = ['Polygon']

        param4 = arcpy.Parameter(
            name = 'workspace_temp',
            displayName = 'Scratch workspace',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DEWorkspace')
        param4.filter.list = ['File System', 'Local Database']

        param5 = arcpy.Parameter(
            name = 'time_config',
            displayName = 'Time configuration',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPSATimeConfiguration')
        param5.value = 'MultiDays   2016  182  243'

        param6 = arcpy.Parameter(
            name = 'day_intrvl',
            displayName = 'Day interval',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPDouble')
        param6.value = '7'

        param7 = arcpy.Parameter(
            name = 'hour_intrvl',
            displayName = 'Hour interval',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPDouble')
        param7.value = '2'

        param8 = arcpy.Parameter(
            name = 'out_raster',
            displayName = 'Output solar insolation raster dataset',
            parameterType = 'Required',
            direction = 'Output',
            datatype = 'DERasterDataset')

        param9 = arcpy.Parameter(
            name = 'rs_bool',
            displayName = 'Is this a Riverscapes project?',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPBoolean',
            category='Riverscapes Project Management')

        param10 = arcpy.Parameter(
            name = 'rs_dir',
            displayName = 'Riverscapes workspace',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'DEWorkspace',
            category = 'Riverscapes Project Management')
        param10.filter.list = ['File System']

        param11 = arcpy.Parameter(
            name = 'proj_name',
            displayName = 'Riverscapes project name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            enabled = 'false',
            category = 'Riverscapes Project Management')

        param12 = arcpy.Parameter(
            name = 'real_name',
            displayName = 'Realization name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            category = 'Riverscapes Project Management')


        return [param0,
                param1,
                param2,
                param3,
                param4,
                param5,
                param6,
                param7,
                param8,
                param9,
                param10,
                param11,
                param12]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        if parameters[9].value == True:
            parameters[10].enabled = True
            parameters[12].enabled = True
            # add project name from XML if it exists
            if parameters[10].altered == True:
                if os.path.isdir(str(parameters[10].value)):
                    rs_xml = "{0}\\{1}".format(parameters[10].value, "project.rs.xml")
                    if os.path.isfile(str(rs_xml)):
                        projectXML = meta.ProjectXML("existing", rs_xml, "Solar")
                        proj_name = projectXML.getProjectName(projectXML.project, "Name")
                        parameters[11].value = proj_name[0]
        else:
            parameters[10].enabled = False
            # the Project Name parameter is always disabled for editing in this tool
            parameters[11].value = ''
            parameters[12].enabled = False

    def updateMessages(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[10].altered == True:
            pathProjectInputs = "{0}\\{1}".format(parameters[10].value,"ProjectInputs")
            pathRealizations = "{0}\\{1}".format(parameters[10].value, "Realizations")
            # check if this is a Riverscapes project folder
            if os.path.exists(pathProjectInputs) and os.path.exists(pathRealizations):
                rs_xml = "{0}\\{1}".format(parameters[10].value, "project.rs.xml")
                if not os.path.isfile(rs_xml):
                    parameters[10].setErrorMessage("This is not a valid Riverscapes project!")
            else:
                parameters[10].setErrorMessage("Valid Riverscape data folders are missing from this directory!")
        return

    def execute(self, p, messages):
        solar_raster.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText,
                         p[4].valueAsText,
                         p[5].valueAsText,
                         p[6].valueAsText,
                         p[7].valueAsText,
                         p[8].valueAsText,
                         p[9].valueAsText,
                         p[10].valueAsText,
                         p[11].valueAsText,
                         p[12].valueAsText)
        return


class SolarVectorTool(object):
    def __init__(self):
        self.label = 'Solar Insolation for a Stream Network'
        self.description = "This tool predicts solar insolation for a stream " \
                           "network. The tool assumes that the stream network " \
                           "has been previously segmented. Solar insolation is " \
                           "calculated per stream network segment. This tool " \
                           "relies on ESRI's Area Solar Radiation."
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        reload(solar_vector)

        param0 = arcpy.Parameter(
            name = 'in_raster',
            displayName = 'Solar insolation raster dataset',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DERasterDataset')

        param1 = arcpy.Parameter(
            name = 'in_stream',
            displayName = 'Stream network polyline feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DEFeatureClass')
        param1.filter.list = ['Polyline']

        param2 = arcpy.Parameter(
            name = 'in_strm_indx',
            displayName = 'Stream unique ID field',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'Field')
        param2.parameterDependencies = [param1.name]

        param3 = arcpy.Parameter(
            name = 'in_strm_area',
            displayName = 'Stream area polygon feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DEFeatureClass')
        param3.filter.list = ['Polygon']

        param4 = arcpy.Parameter(
            name = 'out_fc',
            displayName = 'Output polyline feature with solar values',
            parameterType = 'Required',
            direction = 'Output',
            datatype = 'DEFeatureClass')
        param4.filter.list = ['Polyline']

        param5 = arcpy.Parameter(
            name = 'workspace_temp',
            displayName = 'Scratch workspace',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'Workspace')
        param5.filter.list = ['File System', 'Local Database']

        param6 = arcpy.Parameter(
            name = 'rs_bool',
            displayName = 'Is this a Riverscapes project?',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPBoolean',
            category='Riverscapes Project Management')

        param7 = arcpy.Parameter(
            name = 'rs_dir',
            displayName = 'Riverscapes workspace',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'DEWorkspace',
            category='Riverscapes Project Management')
        param7.filter.list = ['File System']

        param8 = arcpy.Parameter(
            name = 'rs_proj',
            displayName = 'Project name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            enabled = 'false',
            category = 'Riverscapes Project Management')

        param9 = arcpy.Parameter(
            name = 'rs_real_name',
            displayName = 'Realization name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            category='Riverscapes Project Management')
        param9.filter.type = "ValueList"
        param9.filter.list = []

        return [param0,
                param1,
                param2,
                param3,
                param4,
                param5,
                param6,
                param7,
                param8,
                param9]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""

        if parameters[6].value == True:
            parameters[7].enabled = True
            parameters[9].enabled = True
            # add project name from XML if it exists
            if parameters[7].altered == True:
                if os.path.isdir(str(parameters[7].value)):
                    rs_xml = "{0}\\{1}".format(parameters[7].value, "project.rs.xml")
                    if os.path.isfile(str(rs_xml)):
                        projectXML = meta.ProjectXML("existing", rs_xml, "Solar")
                        proj_name = projectXML.getProjectName(projectXML.project, "Name")
                        parameters[8].value = proj_name[0]
                        real_names = projectXML.getRealNames(projectXML.project, "Solar")
                        parameters[9].filter.list = real_names
        else:
            parameters[7].value = ''
            parameters[7].enabled = False
            parameters[8].value = ''
            parameters[9].value = ''
            parameters[9].enabled = False

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[7].altered == True:
            pathProjectInputs = "{0}\\{1}".format(parameters[7].value,"ProjectInputs")
            pathRealizations = "{0}\\{1}".format(parameters[7].value, "Realizations")
            # check if this is a Riverscapes project folder
            if os.path.exists(pathProjectInputs) and os.path.exists(pathRealizations):
                rs_xml = "{0}\\{1}".format(parameters[7].value, "project.rs.xml")
                if not os.path.isfile(rs_xml):
                    parameters[7].setErrorMessage("This is not a valid Riverscapes project!")
            else:
                parameters[7].setErrorMessage("Valid Riverscape data folders are missing from this directory!")
        return

    def execute(self, p, messages):
        solar_vector.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText,
                         p[4].valueAsText,
                         p[5].valueAsText,
                         p[6].valueAsText,
                         p[7].valueAsText,
                         p[8].valueAsText,
                         p[9].valueAsText)
        return

# def main():
#     tbx = Toolbox()
#     tool = SolarVectorTool()
#     tool.execute(tool.getParameterInfo(), None)
#
# if __name__ == "__main__":
#     main()