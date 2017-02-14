import os

def test_copyRSFiles():
    import riverscapes as rs
    rs_dir = r"C:\JL\Testing\solar\Riverscapes\_2Model\rs"
    in_stream = r"C:\JL\Testing\solar\Riverscapes\_1Sources\segments_200m_20160921.gdb\segments200m"
    in_stream_name = os.path.basename(in_stream)
    rs_stream_path = os.path.join(rs.getRSdirs(rs_dir, 0), in_stream_name)
    print rs_stream_path
    rs.copyRSFiles(in_stream, rs_stream_path)

test_copyRSFiles()


#TEST solar_raster input variables
in_dem = r"C:\JL\Testing\solar\Riverscapes\IDE_test\Inputs\dem_100m.tif"
in_canopy = r"C:\JL\Testing\solar\Riverscapes\IDE_test\Inputs\nbcd_baw_100m.tif"
in_stream = r"C:\JL\Testing\solar\Riverscapes\IDE_test\Inputs\segments.gdb\segments200m"
in_strm_area = r"C:\JL\Testing\solar\Riverscapes\IDE_test\Inputs\NHD_area.shp"
time_config = "MultiDays   2016  182  183"
day_intv = "7"
hour_intv = "14"
result = r"C:\JL\Testing\solar\Riverscapes\IDE_test\Output\solar_raster.tif"
workspace_temp = r"C:\JL\Testing\solar\Riverscapes\IDE_test\scratch.gdb"
rs_bool = "true"
wshd_name = "Entiat"
rs_proj_name = "Entiat Solar Radiation"
rs_real_name = "Test Run 01"