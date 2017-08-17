## Using the Solar Stream Tools

### Data Input Requirements:

* NHD+ 1:24k flowlines, segmented
* DEM 10m<sup>2</sup> raster dataset
* Stream area polygon dataset (i.e. bankfull or USGS NHD Area)
* NBDC canopy height raster dataset

### Suggested User Workflow

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
