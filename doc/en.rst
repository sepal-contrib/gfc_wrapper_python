Forest change mask
==================

Base Forest mask and Fragmentation tool 

This application allows the user to:
-   define an area of interest
-   retrieve tree cover change data from the Hansen et al., (2013) dataset
-   combine the layers to produce a forest change map, for a given canopy cover threshold

Background info on GFC
----------------------

GFC provides global layers of information on tree cover and tree cover change since 2000, at 30m spatial resolution and consists of:

-   Tree canopy cover for the year 2000 (treecover2000)
-   Global forest cover gain 2000–2012 (gain)
-   Year of gross forest cover loss event (lossyear)

For more information please refer to:

-   `Hansen, M. C. et Al. 2013. “High-Resolution Global Maps of 21st-Century Forest Cover Change.” Science 342 (15 November): 850–53.<https://science.sciencemag.org/content/342/6160/850>`_
-   University of Maryland, GFC `dataset <http://earthenginepartners.appspot.com/science-2013-global-forest>`_

.. figure:: https://earthengine.google.com/static/images/hansen.jpg

    worldwide GFC
    
Usage
-----

Select an AOI
^^^^^^^^^^^^^

Using the provided AOI selector, select an AOI of your choice between the different methods available in the tool. We provide 3 administration descriptions (from level 0 to 2) and 3 custom shapes (drawn directly on the map, asset or shapefile). 

.. figure:: https://raw.githubusercontent.com/openforis/gfc_wrapper_python/master/doc/img/select_aoi.png 
    
    aoi selector 
    
.. note::

    If a custom aoi from shape or drawing is selected, you will be able to use it directly and the upload to GEE will be launched in the background
    
GFC visualization
^^^^^^^^^^^^^^^^^

Use the slider to change the threshold to consider between forest and non-forest areas. Once you've selected a value, click on :code:`update map` to update the interactive map layers. 

The new layer is a combination of the GFC layers to produce a forest change map, for a given canopy cover threshold. The legend is displayed in the map. You're allowed to zoom in-out as the data are processed in GEE. 

When changing the value of the threshold, a new layer will be added to the map so you can compare and select the more appropriate value of threshold for your analysis. 

.. warning:: 

    The value that will be used for the next step is the last asked value of threshold. If you want to come back to a previous value, move the slider back and click on `update map` again.  
  

.. figure:: https://raw.githubusercontent.com/openforis/gfc_wrapper_python/master/doc/img/viz.png

    vizualization

Export selected data 
^^^^^^^^^^^^^^^^^^^^

Considering the Aoi selected in step 1 and the threshold selected in step two the module will generate a combination of the GFC layers to produce a forest change map, for a given canopy cover threshold. It will live in a `~/gfc_wrapper_results` folder of your sepal environment. 

2 results will be produced: 
-   the map of the forest change mask using the color tab presented in the interactive maps
-   the distribution of each defined zone in a .csv file

You can download these two files directly from the interface using the green buttons

.. figure:: https://raw.githubusercontent.com/openforis/gfc_wrapper_python/master/doc/img/export.png
