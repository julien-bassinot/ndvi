# MEOSS - Test technique

Le projet se compose de deux fonctions : search_files et nvdi

### search_files

Cette fonction permet de rechercher des images rasters dans une arcborescence de fichiers.
Les options permettent de filtrer à la fois sur des suffixes à la manière du cas1, et également sur des mots clefs comme
l'extension ou les bandes spectrales à la manière du cas2.

### ndvi

Cette fonction permet de calculer le ndvi pour une liste d'images rasters.
En option, on peut également fournir une plage de valeurs et le type des pixels à la manière du cas1, ainsi qu'une liste
de mask pour les nuages à la manière du cas2.

## Optimisation

Pour implémenter ces fonctions j'ai choisi le framework pyotb qui a l'avantage d'allier les performances d'OTB dans
l'utilisation des ressources à l'écriture 'pythonic' de GDAL. Ainsi les images rasters ne sont pas chargées entièrement
en mémoire lors des calculs, et l'on peut utiliser des méthodes python comme le slicing ou intéragir avec la librairie
numpy.
