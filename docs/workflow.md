### Using the Solar Stream Tools

#### Data Input Requirements:

* NHD+ 1:24k flowlines, segmented
* DEM 10m<sup>2</sup> raster dataset
* Stream area polygon dataset (i.e. bankfull or USGS NHD Area)
* NBDC canopy height raster dataset

#### Suggested User Workflow

1. Clip all data inputs using a watershed or hydrologic unit polygon
2. Convert all inputs to the same projected coordinate systems.
3. Split reaches in the stream network into segments of uniform length (based on a user-supplied 
length interval) using the [GNAT - Segment Stream Network](https://github.com/SouthForkResearch/gnat) tool.
4. Run the **Generate Solar Insolation Surface** tool. 
5. Using the resulting raster dataset as an input, run the **Solar Insolation for a Stream Network** 
tool, which results in a stream network polyline feature class with summarized solar insolation values 
stored in an attribute field. 

#### Automated Workflow

1. Converts the stream network and stream area polyon vector datasets into rasters and merges together 
into a single stream water surface raster.
2. Converts stream water surface water raster into a polygon and splits by stream segments.
3. Removes the stream surface raster from the NBCD canopy height raster dataset.
4. Merges the canopy height raster with the “bare earth” DEM.
5. Using the merged canopy height/bare earth DEM raster dataset, calculates solar insolation.
6. Calculate mean solar insolation per segmented stream polygons using Zonal Statistics
7. Join zonal statistics output back to segmented stream network polyline dataset
8. Export result to new stream network polyline dataset, with solar insolation values added as an attribute field.
9. Solar insolation output has units of watt hours per square meter (WH/m<sup>2</sup>).

#### Metadata

Successful completion of the tools results in the output of two XML metadata files. These XML files store metadata 
about the input and output parameters specified in each model run, as well as user-specified tool parameter values when 
applicable.

* **meta_solarRaster_YYYYMMDDmmss.xml** · Written by default by the first tool in the solar insolation modeling workflow
 – Generate Solar Insolation Surface.  Stores basic information on tool inputs/outputs, start and stop times, and total 
 processing time.
* **meta_solarVector_YYYYMMDDmmss.xml** · Written by default by second tool in modeling workflow – Solar Insolation for
 a Stream Network. Stores basic information on tool inputs/outputs, start/stop and total processing times.
* **project.rs.xml** · optional output, which is only written if the user indicates that the model is part of a
 Riverscapes project. The project.rs.xml file is more extensive then the Metadata_YYYYMMDD.xml file, and typically 
 includes metadata about the spatial extent of the project, model settings, the Riverscapes project name, a 
 “realization” representing the specific inputs and parameters associated with the model run, and an “analysis” which 
 is defined by the model data outputs.
