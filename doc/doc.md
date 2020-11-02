# Welcome in the user documentation 

This documentation should explain every step to execute the module. If any question or bug remains, please consider post it on the [bug report page](https://github.com/openforis/gfc_wrapper_python/issues)

## Before starting 
This module will require the user to register to GEE instead of using the public SEPAL account. Follow this [link](https://earthengine.google.com) to create a GEE account. Once done, select your GEE account in the SEPAL bottom right corner and use your personal credentials. 

![gee_account](./img/gee_account.png)

Then go to your terminal, start a `t1` session and run:  
```
$ earthengine authenticate
```

Follow the instructions provided by the command. You are now ready to go.

## table of content
1. [select an AOI](./select_aoi.md)  
  1.1. [country boundaries](./select_aoi.md)  
  1.2. [draw a shape](./select_aoi.md)  
  1.3. [import shapefile](./select_aoi.md)  
  1.4. [use Google Earth Engine](./select_aoi.md) 
2. [GFC visualization](./gfc_viz.md) 
3. [export data](./export.md)  


> :warning: **Troubleshooting:** This module is executed through a voila application that create a User Interface on top of a Jupyter notebook. The reactivity of some components will thus be a little slower than what you are used to on a standard website. Please be nice with them.

[let's start!](./select_aoi.md)
