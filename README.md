# Solar Stream Tools

## Summary
Solar insolation directly affects stream temperature and the primary productivity of streams.   Eco Logical Research, Inc. (ELR) has explored using areal solar insolation as an input parameter for a forthcoming gross primary production model. South Fork Research, Inc. (SFR) is investigating methods for modeling solar insolation of streams in the Columbia Basin. Specifically, SFR seeks to develop a methodology for modeling solar insolation that will more closely emulate the effects of shading from riparian vegetation and topography.
The [Columbia Habitat Monitoring Program](https://www.champmonitoring.org/) (CHaMP) protocol requires the collection of solar insolation data during stream surveys, however, collecting field-based solar insolation measurements comprehensively for the entire stream network of the Columbia Basin is resource prohibitive.  Developing a spatially-explicit model to predict solar insolation for all stream networks and associated riparian buffers within the Columbia Basin will potentially provide a robust, reliable input for GPP modeling efforts, and may preclude the need for field-based data collection. 

The process relies on raster data derived from the National Biomass and Carbon Dataset (NBCD) basal area-weighted canopy height dataset.  The [NBCD](http://www.whrc.org/mapping/nbcd) was developed by the Woods Hole Research Center in 2000, and combines high-resolution inSAR data acquired by the 2000 Shuttle Radar Topography Mission (SRTM), US Forest Service Forest Inventory and Analysis (FIA) data, and remotely-sensed data from the Landsat ETM+ sensor.  The tool then combines basal-area-weighted canopy height values with bare-earth topographic values from a high-resolution digital elevation model (DEM), resulting in a relatively close approximation of stream shading, when calculating solar insolation using ESRI’s area solar radiation tool.  

It is recommended that prior to using this tool, the required stream network input be segmented using the [Geomorphic Network and Analysis Toolbox (GNAT) Segment Stream Network](https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox).

## Project Status and Updates
* 10/12/2016 - Tool updated to version 0.2
* 8/22/2015 - Beta version of the Solar Streams Tool, v0.1, uploaded to Github.

## Data Input Requirements:
* NHD+ 1:24k flowlines, segmented
* DEM 10m<sup>2</sup>
* USGS HUC 4 polygon
* Stream area polygon (i.e. bankfull or NHD Area)
* NBDC canopy height

## Method Workflow
1. Data pre-processing steps, including convertion all data inputs to the same coordinate system, segmentation of the stream network, and clipping all data inputs by HUC polygon.
_Automated_
2. Convert stream network and stream area polyon vector datasets into rasters and merge together into a single stream water surface raster.
3. Convert stream water surface water raster into a polygon and split by stream segments.
4. Remove the stream surface raster from the NBCD canopy height raster dataset
5. Merge canopy height raster with “bare earth” DEM.
6. Using the merged canopy height/bare earth DEM, calculate solar insolation:
  * **Study basin (HUC polygon)**: A polygon feature class that encompasses the area of analysis. Typically a hydrologic unit or watershed.
  * **Bare earth DEM**: Digital elevation or digital terrain model as a raster dataset, representing bare earth topology.
  * **Canopy height raster**: Digital elevation representing vegetation or canopy heights.  The NBCD BAW canopy height dataset is highly recommended for this input parameter.
  * **Stream network feature class**: The polyline feature class that will contain the results of the predicted solar insolation modeling.  The stream network should already been segmented, using the [GNAT Segment Stream Network](https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox) tool.
  * **Stream area feature class**: This dataset represents stream surface area or each stream in the network.  As example, a bankfull polygon or NHD Area dataset could be used here.
  * **Output feature class**: The resulting stream network feature class that will contain the predicted solar insolation values per stream segment.
  * **Scracth workspace**: File geodatabase that store temporary data produced by the tool.
  * **Solar insolation model parameters**:
  (Recommended settings when developing solar insolation for ISEMP GPP modeling)
    * _Time configuration_: Multiple days in a year
    * _Year_: 2014 (to coincide with CHaMP SunEye monitoring data for validation purposes)
    * _Start day_: 182 (July 1st)
    * _End day_: 243 (August 31st)
    * _Day interval_: 7
    * _Hour interval_: 0.5
7. Calculate mean solar insolation per segmented stream polygons using Zonal Statistics
8. Join zonal statistics output back to segmented stream network polyline dataset
9. Export result to new stream network polyline dataset, with solar insolation added as an attribute field.
10. Solar insolation output has units of watt hours per square meter (WH/m<sup>2</sup>).

## Suggested User Workflow
1. Clip all data inputs using a watershed or hydrologic unit polygon
2. Convert all inputs to the same projected coordinate systems.
3. Split reaches in the stream network into segments of uniform length (based on a user-supplied length interval) using the [GNAT Segment Stream Network](https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox) tool.

## Data Validation with CHaMP SunEye Measurements
* To validate the results of the solar insolation model, solar measurement data can be downloaded from [Columbia Habitat Monitoring Program](https://www.champmonitoring.org/) website.  Solar radiation data has been collected by CHaMP field survey crews using SunEye instruments, and this data can be compared modeled solar insolation values.
  * SunEye data must be downloaded separately per CHaMP survey site. 
  * Navigate to Watershed (Name) > Field Support > Data Check In > click the "File Upload" icon associated with the Site ID > Solar Input Photos.  Download the AverageSolarAccess.csv files.
  * Once all of the AverageSolarAccess files have been downloaded for the basin of interest, run the compile\_SunEye.py from the command line (i.e. > python compile\_SunEye.py).
  * Enter the filepath to the directory containing all of the downloaded SunEye files.
  * Enter the name of the output file.  This will be stored in the same directory as the SunEye files.

## Acknowledegments
The Solar Streams model and tool is developed and maintained by Jesse Langdon for [South Fork Research, Inc.](http://southforkresearch.org) (SFR).