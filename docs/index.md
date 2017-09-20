---
title: Home
weight: 1
---

### Summary
The [Integrated Status and Effectivness Monitoring Program](https://isemp.org) (ISEMP) will 
be developing a gross primary production (GPP) model for stream networks in the Columbia 
Basin in order to make spatially-explicit predictions regarding salmonid habitat needs. 
Solar insolation directly affects stream temperature (Sinokrot and Stefan, 1993) and the 
primary productivity of streams (Fisher and Likens, 1973; Hill et al., 1995). Eco Logical 
Research, Inc. has explored using areal solar insolation as an input parameter for a 
forthcoming gross primary production model. South Fork Research, Inc. (SFR) is investigating 
methods for modeling solar insolation of streams in the Columbia Basin. Specifically, SFR 
seeks to develop a methodology for modeling solar insolation that will more closely emulate 
the effects of shading from riparian vegetation and topography.

The [Columbia Habitat Monitoring Program](https://www.champmonitoring.org/) (CHaMP) protocol 
requires the collection of solar insolation data during stream surveys, however, collecting 
field-based solar insolation measurements comprehensively for the entire stream network of 
the Columbia Basin is resource prohibitive. Developing a spatially-explicit model to predict 
solar insolation for all stream networks and associated riparian buffers within the Columbia 
Basin will potentially provide a robust, reliable input for GPP modeling efforts, and may 
preclude the need for field-based data collection. 

To date, our solar modeling efforts have relied on raster data derived from the National Biomass 
and Carbon Dataset (NBCD) basal area-weighted canopy height dataset. The [NBCD](http://www.whrc.org/mapping/nbcd) 
was developed by the Woods Hole Research Center in 2000, and combines high-resolution inSAR data 
acquired by the 2000 Shuttle Radar Topography Mission (SRTM), US Forest Service Forest Inventory 
and Analysis (FIA) data, and remotely-sensed data from the Landsat ETM+ sensor. The tool then 
combines basal area-weighted canopy height values with bare-earth topographic values from a 
high-resolution digital elevation model (DEM), resulting in a relatively close approximation of 
stream shading, when calculating solar insolation using ESRI’s[Area Solar Radiation](http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/area-solar-radiation.htm) 
tool. While 
we have obtained good results using NBCD basal area-weighted canopy height data, any vegetation 
height raster dataset (with elevation values in meters) will work as an input for the tool.

It is recommended that prior to using this tool, the required stream network input be segmented 
using the [Geomorphic Network and Analysis Toolbox (GNAT) Segment Stream Network](https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox).


### Citation

* Fisher, S. G. and G. E. Likens (1973). "Energy Flow in Bear Brook, New Hampshire: An Integrative 
Approach to Stream Ecosystem Metabolism." Ecological monographs 43(4): 421-439.
* Hill, W. R., et al. (1995). "Light Limitation in a Stream Ecosystem: Responses by Primary Producers 
and Consumers." Ecology 76(4): 1297-1309.
* Sinokrot, B. A. and H. G. Stefan (1993). "Stream temperature dynamics: Measurements and modeling." 
Water Resources Research 29(7): 2299-2312.


### Acknowledegments

The Solar Streams model and tool is actively developed and maintained by [South Fork Research, Inc.](http://southforkresearch.org) (SFR). Funding for these
tools was provided by the Bonneville Power Administration (BPA).


### License

Licensed under the [GNU General Public License Version 3](../License.txt).