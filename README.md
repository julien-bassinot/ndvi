# MEOSS - Test technique

Le projet se compose de deux fonctions : `search_files` et `nvdi`

### `search_files`

Cette fonction permet de rechercher des images rasters dans une arcborescence de fichiers.
Les options permettent de filtrer à la fois sur des suffixes à la manière du cas1, et également sur des mots clefs comme
l'extension ou les bandes spectrales à la manière du cas2.

```python
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
```

### `ndvi`

```python
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
```

Cette fonction permet de calculer le ndvi pour une liste d'images rasters.
En option, on peut également fournir une plage de valeurs et le type des pixels à la manière du cas1, ainsi qu'une liste
de mask pour les nuages à la manière du cas2.

## Optimisation

Pour implémenter ces fonctions j'ai choisi le framework pyotb qui a l'avantage d'allier les performances d'OTB dans
l'utilisation des ressources à l'écriture 'pythonic' de GDAL. Ainsi les images rasters ne sont pas chargées entièrement
en mémoire lors des calculs, et l'on peut utiliser des méthodes python comme le slicing ou intéragir avec la librairie
numpy.

## Usage

```shell
cd ~
git clone https://github.com/julien-bassinot/ndvi.git
docker build -t orfeo .
```

```shell
docker run --rm -it -v ~/ndvi:/root/ndvi orfeo
```

```shell
cd /root/ndvi
pytest test_utils.py
```