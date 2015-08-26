# Solar Stream Tools

## Summary
Solar insolation directly affects stream temperature and the primary productivity of streams.   Eco Logical Research, Inc. (ELR) has explored using areal solar insolation for the solar input parameter. South Fork Research, Inc. (SFR) is investigating methods for modeling solar insolation of streams in the Columbia Basin. Specifically, SFR seeks to develop a methodology for modeling solar insolation that will more closely emulate the effects of shading from riparian vegetation and topography.
The [Columbia Habitat Monitoring Program](https://www.champmonitoring.org/) (CHaMP) protocol requires the collection of solar insolation data during stream surveys, however, collecting field-based solar insolation measurements comprehensively for the entire stream network of the Columbia Basin is resource prohibitive.  Developing a spatially-explicit model to predict solar insolation for all stream networks and associated riparian buffers within the Columbia Basin will potentially provide a robust, reliable input for GPP modeling efforts, and may preclude the need for field-based data collection. 

The process relies on raster data derived from the National Biomass and Carbon Dataset (NBCD) basal area-weighted canopy height dataset.  The [NBCD](http://www.whrc.org/mapping/nbcd/) was developed by the Woods Hole Research Center in 2000, and combines high-resolution inSAR data acquired by the 2000 Shuttle Radar Topography Mission (SRTM), US Forest Service Forest Inventory and Analysis (FIA) data, and remotely-sensed data from the Landsat ETM+ sensor.  The tool then combines basal-area-weighted canopy height values with bare-earth topographic values from a high-resolution digital elevation model (DEM), resulting in a relatively close approximation of stream shading, when calculating solar insolation using ESRI’s area solar radiation tool.  

It is recommended that prior to using this tool, the required stream network input be segmented using the SFR [Segment](http://github.com/jesselangdon/segment_tool) tool.

## Project Status and Updates
* Solar insolation modeling completed for the Middle Fork John Day and Entiat basins.
* 8/22/2015 - Beta version of the Solar Streams Tool, v0.1, uploaded to Github.

## Data Input Requirements:
* NHD+ 1:24k flowlines, segmented
* DEM 10m<sup>2</sup>
* USGS HUC 4 polygon
* Bankfull polygons
* NBDC canopy height

## Method Workflow
1. Data pre-processing steps, including segmentation of the stream network, and clipping all data inputs by HUC polygon.
2. Convert stream network and bankfull polyon datasets into rasters and merge together into a single stream water surface raster.
3. Segment bankfull polygons by stream segments.
4. Remove the stream surface raster from the NBCD canopy height raster dataset
5. Merge canopy height raster with “bare earth” DEM.
6. Using the merged canopy height/bare earth DEM, calculate solar insolation:
    a. Latitude: centroid of HUC 4
    b. Sky size/resolution: 400
    c. Time range: July 1 through Aug. 31
    d. Day Interval: 7
    e. Hour interval: 0.5
7. Create 10 meter buffers around segmented bankfull polygons.
8. Calculate mean solar insolation per segmented bankfull polygons buffers.
9. Join the resulting mean solar insolation table back to the segmented stream network.

## Acknowledegments
The Solar Streams model and tool is developed and maintained by Jesse Langdon, [South Fork Research, Inc.](http://southforkresearch.org) (SFR).

