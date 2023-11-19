from utils import *
import pytest
import imageio
import numpy as np


def test_search_files():
    # test band
    assert search_files('./rasters', extension='tif', resolution='SENTINEL2', band='FRE_B4.') == [
        Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif')
    ]
    # test nested folder
    assert search_files('./rasters', extension='tif', resolution='SENTINEL2', band='CLM_R1') == [
        Path('./rasters/MASKS/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_CLM_R1.tif')
    ]
    # test regex
    assert search_files('./rasters', extension='tif', resolution='SENTINEL2',
                        regex='_FRE_ConcatenateImageBGRPIR.tif') == [
               Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_ConcatenateImageBGRPIR.tif')
           ]

    # test band & regex
    # assert len(search_files('./rasters', extension='tif', resolution='SENTINEL2', band='R2', regex='D0*')) == 6

    # test all xml files
    # assert len(search_files('./rasters', extension='xml')) == 12

    # test all files in MASKS
    # assert len(search_files('./rasters/MASKS')) == 26

    # test NotADirectoryError
    with pytest.raises(NotADirectoryError):
        search_files('./random/folder')


"""
def test_bands():
    img_path = Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_ConcatenateImageBGRPIR.tif')
    bands(img_path[0], band_list=['B2', 'B3', 'B4', 'B8'], pixel_type='int16', out_directory='./rasters/output')
    img_result = search_files('./rasters/output', extension='tif', regex='_FRE_ConcatenateImageBGRPIR_*')
    assert len(img_result) == 4


def test_multispectral():
    band_path = [
        Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif'),
        Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B8.tif')
    ]
    multipsectral(band_path, pixel_type='int16', out_directory='./rasters/output')
    img_path = search_files('./rasters/output', extension='tif', band='B4B8')
    img = pyotb.Input(str(img_path[0]))
    assert img.shape[-1] == 2
"""


def test_ndvi_multi_versus_OTB():
    img_path = [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_ConcatenateImageBGRPIR.tif')]
    ndvi(input_type='multi', input_paths=img_path, red=2, nir=3, out_directory='./rasters/output', mask=[],
         nodata_value=0, pixel_type='float', pixel_range=(-1, 1))
    pyotb.RadiometricIndices({'in': str(img_path[0]), 'channels.nir': 4, 'channels.red': 3, 'list': ['Vegetation:NDVI'],
                              'out': './rasters/output/NDVI_OTB.tif'})
    with imageio.get_reader('./rasters/output/NDVI_OTB.tif') as reader1:
        img1 = reader1.get_data(0)[4000:6000, 4000:6000]
    with imageio.get_reader('./rasters/output/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3'
                            '-1_FRE_ConcatenateImageBGRPIR_NDVI.tif') as reader2:
        img2 = reader2.get_data(0)[4000:6000, 4000:6000]
    assert np.all(img1 == img2)
    del img1, img2


def test_ndvi_multi_versus_cas1():
    img_path = [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_ConcatenateImageBGRPIR.tif')]
    ndvi(input_type='multi', input_paths=img_path, red=2, nir=3, out_directory='./rasters/output', mask=[],
         nodata_value=0, pixel_type='float', pixel_range=(-1, 1))
    with imageio.get_reader('./rasters/output/NDVI_CAS1.tif') as reader1:
        img1 = reader1.get_data(0)[4000:6000, 4000:6000]
    with imageio.get_reader('./rasters/output/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3'
                            '-1_FRE_ConcatenateImageBGRPIR_NDVI.tif') as reader2:
        img2 = reader2.get_data(0)[4000:6000, 4000:6000]
    assert np.all(img1 == img2)
    del img1, img2


def test_ndvi_bands_versus_OTB():
    band_path = [
        [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif')],
        [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B8.tif')]
    ]
    ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[],
         nodata_value=0, pixel_type='float', pixel_range=(-1, 1))
    with imageio.get_reader('./rasters/output/NDVI_OTB.tif') as reader1:
        img1 = reader1.get_data(0)[4000:6000, 4000:6000]
    with imageio.get_reader('./rasters/output/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4_NDVI.tif') as reader2:
        img2 = reader2.get_data(0)[4000:6000, 4000:6000]
    assert np.all(img1 == img2)
    del img1, img2


def test_ndvi_bands_versus_cas2():
    band_path = [
        [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif')],
        [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B8.tif')]
    ]
    cloud_path = [Path('./rasters/MASKS/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_CLM_R1.tif')]
    ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=cloud_path,
         nodata_value=0, pixel_type='int16', pixel_range=(-1000, 1000))
    with imageio.get_reader('./rasters/output/NDVI_CAS2.TIF') as reader1:
        img1 = reader1.get_data(0)[4000:6000, 4000:6000]
    with imageio.get_reader('./rasters/output/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4_NDVI.tif') as reader2:
        img2 = reader2.get_data(0)[4000:6000, 4000:6000]
    assert np.all(img1 == img2)
    del img1, img2
