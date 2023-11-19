from typing import List
from pathlib import Path
import pyotb


def search_files(directory: str, extension: str = None, resolution: str = None, band: str = None, regex: str = None) -> List[Path]:
    """
    Search for specific raster paths in a folder.

    :param directory: The working directory where the rasters are stored. This function is recursive thus it also takes
    into account nested folders.
    :type directory: str
    :param extension: Filter on image extension ('jp2', 'tif', 'jpg', etc...)
    :type extension: str, optional
    :param resolution: SENTINEL2A (only resolution tested for the moment)
    :type resolution: str, optional
    :param band: Filter on spectral band ('FRE_B4', 'FRC_B8', 'CLM_R1', etc...)
    :type band: str, optional
    :param regex: Filter with a suffix (not cut)
    :type regex: str, optional
    :return: A list of paths for the selected rasters
    :rtype: List[Path]
    """

    # Check if directory exists
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError

    # Create a regex with input
    if extension or resolution or band:
        regex0 = ''
        for arg in [resolution, band, extension]:
            if arg:
                regex0 += '*' + arg
        if not extension:
            regex0 += '*'
    else:
        regex0 = None

    if regex and regex0:
        liste0 = set(directory.rglob(regex0))
        liste1 = set(directory.rglob('*' + regex))
        return list(liste0.intersection(liste1))

    elif regex:
        return list(directory.rglob('*' + regex))

    elif regex0:
        return list(directory.rglob(regex0))

    else:
        return list(directory.rglob('*'))


def bands(multi: Path, band_list: List[str], pixel_type: str, out_directory: str) -> None:
    """
    Split a multispectral image into several spectral images

    :param multi: A path pointing to a multispectral image
    :type multi: Path
    :param band_list: List of bands in the right order (ex. ['B2', 'B3', 'B4', 'B8'])
    :type band_list: List[str]
    :param pixel_type: Pixel type for the new spectral images (ex. 'uint8', 'int16', 'float')
    :type pixel_type: str
    :param out_directory: Path to an output directory
    :return: None
    """

    # Check if directory exists
    out_directory = Path(out_directory)
    if not out_directory.is_dir():
        raise NotADirectoryError

    img = pyotb.Input(str(multi))

    # check if there's no band missing
    if img.shape[-1] != len(band_list):
        raise IndexError(f"Le nombre de bandes dans la liste {len(band_list)} ne concorde pas avec le nombre de "
                         f"bandes {img.shape[-1]} dans l'image multispectrale {multi}")

    for band in range(len(band_list)):
        img_path = str(multi).split('/')[-1].split('.')[0] + '_' + band_list[band] + '.tif'
        img_path = out_directory / Path(img_path)
        img[:, :, band].write(str(img_path), pixel_type=pixel_type)

    return


def multipsectral(band_path: List[Path], pixel_type: str, out_directory: str) -> None:
    """
    Agregate several spectral images into one multispectral image

    :param band_path: A list of paths pointing to the spectral images
    :type band_path: List[Path]
    :param pixel_type: Pixel type for the new multispectral image (ex. 'uint8', 'int16', 'float')
    :type pixel_type: str
    :param out_directory: Path to an output directory
    :type out_directory: str
    :return: None
    """

    # Check if directory exists
    out_directory = Path(out_directory)
    if not out_directory.is_dir():
        raise NotADirectoryError

    img = pyotb.ConcatenateImages({'il': [pyotb.Input(str(path)) for path in band_path]})
    img_path = str(band_path[0]).split('/')[-1].split('.')[0]
    for path in band_path[1:]:
        img_path += str(path).split('.')[0].split('_')[-1]
    img_path = out_directory / Path(img_path + '.tif')
    img.write(str(img_path), pixel_type=pixel_type)
    return


def ndvi(input_type: str, input_paths: List, red: int, nir: int, out_directory: str, mask: List[Path] = [], nodata_value: int = 0, pixel_type: str = 'float', pixel_range: tuple = (-1, 1)) -> None:
    """
    Compute the NDVI Radiometric indice (Normalized Difference Vegetation Index) from the input rasters and store the
    result in output directory. It can take as input multispectral images or single band images.

    :param input_type: 'multi' if multispectral images are provided or 'bands' if red-band and nir-band images are provided
    :type input_type: str
    :param input_paths: A list of paths for multispectral images or 2 lists of paths for red and nir images.
    :type input_paths: List[Path] | List[List[Path], List[Path]]
    :param red: Position of the red band in the multispectral image, or position of the red list in the input_paths list
    :type red: int
    :param nir: Position of the nir band in the multispectral image, or position of the nir list in the input_paths list
    :type nir: int
    :param mask: A list of paths for mask rasters (must be the same length as input_paths), else empty list []
    :type mask: List[Path]
    :param nodata_value: No data value (0, -999, None)
    :type nodata_value: int
    :param pixel_type: Pixel type for the NDVI raster (ex. 'uint8', 'int16', 'float')
    :type pixel_type: str
    :param pixel_range: Value range for NDVI (ex. (-1, 1), (0, 255), (-1000, 1000))
    :type pixel_range: tuple
    :param out_directory: Path to an output directory
    :type out_directory: str
    :return: None
    """

    # Check if directory exists
    out_directory = Path(out_directory)
    if not out_directory.is_dir():
        raise NotADirectoryError(f"{out_directory} n'est pas un répertoire valide.")

    # Check inputs
    if input_type not in ['multi', 'bands']:
        raise ValueError(f"La valeur de input_type doit être 'multi' ou 'bands', pas {input_type}.")

    if input_type == 'multi':

        if type(input_paths[0]) == list:
            raise ValueError("Avec 'multi', input_paths doit être une liste de chemins d'accès (List[Path]).")

        for i in range(len(input_paths)):
            img = pyotb.Input(str(input_paths[i]))
            a = (pixel_range[1] - pixel_range[0]) / 2
            b = pixel_range[0]
            ndvi_calc = ((2*a + b) * img[:, :, nir] + b * img[:, :, red]) / (img[:, :, nir] + img[:, :, red])

            if len(mask) != 0:

                if len(mask) != len(input_paths):
                    raise ValueError("Les listes mask et input_paths doivent avoir la même longueur.")

                ndvi_masked = pyotb.where(pyotb.Input(str(mask[i])) > 0, nodata_value, ndvi_calc)
                ndvi_masked.write(str(out_directory / Path(str(input_paths[i]).split('/')[-1].split('.')[0] + '_NDVI.tif')), pixel_type=pixel_type)

            else:
                ndvi_calc.write(
                    str(out_directory / Path(str(input_paths[i]).split('/')[-1].split('.')[0] + '_NDVI.tif')),
                    pixel_type=pixel_type)

    else:

        if not (type(input_paths[0]) == list and len(input_paths) == 2):
            raise ValueError(
                "Avec 'bands', input_paths doit être une liste de deux listes de chemins d'accès (List[List["
                "Path], List[Path]]).")

        if len(input_paths[0]) != len(input_paths[1]):
            raise ValueError("Les listes red et nir doivent avoir la même longueur dans input_paths.")

        for i in range(len(input_paths[0])):
            red_img, nir_img = pyotb.Input(str(input_paths[red][i])), pyotb.Input(str(input_paths[nir][i]))
            a = (pixel_range[1] - pixel_range[0]) / 2
            b = pixel_range[0]
            ndvi_calc = ((2*a + b) * nir_img + b * red_img) / (nir_img + red_img)

            if len(mask) != 0:

                if len(mask) != len(input_paths[0]):
                    raise ValueError("Les listes mask et input_paths doivent avoir la même longueur.")

                ndvi_masked = pyotb.where(pyotb.Input(str(mask[i])) > 0, nodata_value, ndvi_calc)
                ndvi_masked.write(
                    str(out_directory / Path(str(input_paths[red][i]).split('/')[-1].split('.')[0] + '_NDVI.tif')),
                    pixel_type=pixel_type)

            else:
                ndvi_calc.write(
                    str(out_directory / Path(str(input_paths[red][i]).split('/')[-1].split('.')[0] + '_NDVI.tif')),
                    pixel_type=pixel_type)
