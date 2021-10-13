# Forest change mask

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Black badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## About

Base Forest mask and Fragmentation tool 

This application allows the user to:
- define an area of interest
- retrieve tree cover change data from the [Hansen et al., (2013)](https://science.sciencemag.org/content/342/6160/850) dataset
- combine the layers to produce a forest change map, for a given canopy cover threshold and between selected years

![example](./doc/img/full_viz.png)

for more information about usage please read the [documentation](https://docs.sepal.io/en/latest/modules/dwn/gfc_wrapper_python.html)

### Background info on GLobal Forest Change (GFC)

GFC provides global layers of information on tree cover and tree cover change since 2000, at 30m spatial resolution and consists of:

- Tree canopy cover for the year 2000 (treecover2000)
- Global forest cover gain 2000–2012 (gain)
- Year of gross forest cover loss event (lossyear)

For more information please refer to:

- [Hansen, M. C. et Al. 2013. “High-Resolution Global Maps of 21st-Century Forest Cover Change.” Science 342 (15 November): 850–53.](https://science.sciencemag.org/content/342/6160/850)
- University of Maryland, GFC [dataset](http://earthenginepartners.appspot.com/science-2013-global-forest)

![gfc](https://earthengine.google.com/static/images/hansen.jpg)

## contribute

to install the project on your SEPAL account 
```
$ git clone https://github.com/openforis/gfc_wrapper_python.git
```

please follow the contributing [guidelines](CONTRIBUTING.md).