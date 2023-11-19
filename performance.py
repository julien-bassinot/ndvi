from utils import *
import timeit
import os

# bandes spectrales pour le calcul du NDVI
band_path = [
    [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif')],
    [Path('./rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B8.tif')]
]

# Utilisation de la mémoire
os.environ['OTB_MAX_RAM_HINT'] = '128'
print('RAM 128: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

os.environ['OTB_MAX_RAM_HINT'] = '512'
print('RAM 512: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

os.environ['OTB_MAX_RAM_HINT'] = '1028'
print('RAM 1028: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

os.environ['OTB_MAX_RAM_HINT'] = '4096'
print('RAM 4096: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)


# Utilisation du nombre de CPU pour les opérations IO et les calculs

os.environ['OTB_MAX_RAM_HINT'] = '512'

os.environ['GDAL_NUM_THREADS'] = '2'
os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = '2'
print('CPU 1: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

os.environ['GDAL_NUM_THREADS'] = '3'
os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = '3'
print('CPU 3: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

os.environ['GDAL_NUM_THREADS'] = '5'
os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = '5'
print('CPU 5: ', timeit.timeit(lambda: ndvi(input_type='bands', input_paths=band_path, red=0, nir=1, out_directory='./rasters/output', mask=[], nodata_value=0, pixel_type='uint8', pixel_range=(0, 255)), number=2) / 2)

