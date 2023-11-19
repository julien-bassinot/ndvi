# MEOSS - Test technique

Le projet se compose de deux fonctions : `search_files` et `nvdi` dans le fichier `utils.py`

### search_files

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

### ndvi

Cette fonction permet de calculer le ndvi pour une liste d'images rasters.
En option, on peut également fournir une plage de valeurs et le type des pixels à la manière du cas1, ainsi qu'une liste
de mask pour les nuages à la manière du cas2.
Les images d'entrée peuvent être des images multispectrales à la manière du cas1 ou plusieurs images spectrales à la manière
du cas 2.

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

## Optimisation

Pour implémenter ces fonctions j'ai choisi le framework [pyotb](https://pypi.org/project/pyotb/) qui a l'avantage d'allier les performances d'OTB dans
l'utilisation des ressources à l'écriture 'pythonic' de GDAL. Ainsi les images rasters ne sont pas chargées entièrement
en mémoire lors des calculs, et l'on peut utiliser des méthodes python comme le slicing ou intéragir avec la librairie
numpy.<br>

J'ai également réalisé des tests de performances dans le fichier `performance.py` en faisant varier la RAM disponible 
et le nombre de CPU, cependant je n'ai pas obtenu de variations significatives en temps de calcul, ce point sera donc à 
approfondir. De manière générale pour le calcul de gros volumes de données, le traitement 'au fil de l'eau' est à privilégier 
et les tâches parallélisables peuvent être accélérées par du multithreading.
<br> 

Ci-joint les résultats du test de performance. A titre de comparaison, le script simple Vegetation:NDVI de OTB s'execute en 
10 secondes sur ma machine.

| RAM disponible | Temps de calcul du NDVI |
| --------------- | ------------------|
| 128 | 11.8 |
|512 | 10.0 |
| 1028 | 11.7 |
| 4096 | 16.3 |

| Nombre de CPU | Temps de calcul du NDVI |
| ------------- | ----------------------- |
| 2 | 13.2 |
| 3 | 13.0 |
| 5 | 13.0 |

## Usage

### Environnement

L'environnement est encapsulé dans un conteneur Docker. Il s'agit de l'image officielle fournie par [OrfeoToolbox](https://hub.docker.com/r/orfeotoolbox/otb)
à laquelle vient s'ajouter d'autres librairies comme `pyotb` et `pytest`.

```shell
cd ~
git clone https://github.com/julien-bassinot/ndvi.git
docker build -t orfeo .
```

Pour lancer l'image en mode interactif procéder comme suit:

```shell
docker run --rm -it -v ~/ndvi:/root/ndvi orfeo
```

### Tests unitaires

Avant de lancer les tests unitaires du fichier test_utils, il faut copier les rasters suivants depuis les fichiers cas1_env-afo
et cas2_env-otb. Les deux derniers rasters NDVI_CAS1 et NDVI_CAS2 sont les résultats des fonctions cas1 et cas2.

```shell
/rasters/MASKS/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_CLM_R1.tif
/rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B4.tif
/rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_B8.tif
/rasters/SENTINEL2A_20231012-105856-398_L2A_T31TCJ_C_V3-1_FRE_ConcatenateImageBGRPIR.tif
/rasters/output/NDVI_CAS1.tif
/rasters/output/NDVI_CAS2.TIF
```

Ensuite lancer les tests comme suit:

```shell
cd /root/ndvi
pytest test_utils.py
```

### Calcul du NDVI

Deux exemples d'utilisation des deux fonctions dans un interpreteur python:

- Avec une image multispectrale.
```python
from utils import *

img_path = search_files('./rasters', extension='tif', resolution='SENTINEL2', regex='_FRE_ConcatenateImageBGRPIR.tif')

ndvi(input_type='multi', 
     input_paths=img_path, 
     red=2, 
     nir=3, 
     out_directory='./rasters/output', 
     mask=[],
     nodata_value=0, 
     pixel_type='float', 
     pixel_range=(-1, 1))
```

- Avec plusieurs bandes d'image spectrale et un mask pour les nuages.

```python
from utils import *

band_path = [
    search_files('./rasters', extension='tif', resolution='SENTINEL2', band='FRE_B4.')
    search_files('./rasters', extension='tif', resolution='SENTINEL2', band='FRE_B8.')
]
cloud_path = search_files('./rasters', extension='tif', resolution='SENTINEL2', band='CLM_R1')

ndvi(input_type='bands', 
     input_paths=band_path, 
     red=0, 
     nir=1, 
     out_directory='./rasters/output', 
     mask=cloud_path,
     nodata_value=0, 
     pixel_type='int16', 
     pixel_range=(-1000, 1000))
```

