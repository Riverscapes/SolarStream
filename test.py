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