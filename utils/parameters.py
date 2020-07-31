import os
import sys
sys.path.append("..") 
from utils import utils
import pandas as pd 
import matplotlib as mpl


def create_folder(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname


################################################################
########                        folders                 ########
################################################################

def getResultDir():
    pathname = os.path.join(os.path.expanduser('~'), 'gfc_wrapper_results') + '/'
    return create_folder(pathname)

def getDwnDir():
    pathname = os.path.join(getResultDir(), 'downloads') + '/'
    return create_folder(pathname) 

def getRootDir():
    pathname = os.path.join(os.path.expanduser('~'), 'gfc_wrapper_python') + '/'
    return create_folder(pathname) 

def getscriptDir():
    pathname = os.path.join(getRootDir(), 'scripts') + '/'
    return create_folder(pathname)

def getDataDir():
    pathname = os.path.join(getRootDir(), 'data') + '/'
    return create_folder(pathname)

def getTmpDir():
    pathname = os.path.join(getResultDir(), 'tmp') + '/'
    return create_folder(pathname)

def getGfcDir():
    pathname = os.path.join(getResultDir(), 'gfc') + '/'
    return create_folder(pathname)

def getAoiDir():
    pathname = os.path.join(getRootDir(), 'aoi') + '/'
    return create_folder(pathname)

def getStatDir():
    pathname = os.path.join(getResultDir(), 'stat') + '/'
    return create_folder(pathname)

def getMspaDir():
    pathname = os.path.join(getRootDir(), 'mspa') + '/'
    return create_folder(pathname)

def getTmpMspaDir():
    pathname = os.path.join(getResultDir(), 'tmp/mspa') + '/'
    return create_folder(pathname)

def getUtilsDir():
    pathname = os.path.join(getRootDir(), 'utils') + '/'
    return create_folder(pathname)

########################################################
##########              hard-coded params          #####
########################################################
def getMaxYear():
    return 19

def getSpacing():
    return 0.011

def getOffset():
    return 0.001

def getProj():
    return '+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m no_defs'

def getDataset():
    return "GFC-2019-v1.7"

def getClasses():
    return [100,50,40,30,20,10,5,4,3,2,1]

def getTypes():
    return ["treecover2000","lossyear","gain","datamask"]

##########################################################
#########                     legend                ######
##########################################################

def getMyClasses():
    
    years = [i for i in range (1, getMaxYear()+1)]
    pos = 1
    my_classes = [0,30,40,50,51]
    my_classes[pos:pos] = years

    return my_classes

def getMyLabel():
    
    years = ['loss_{}'.format(str(2000+i)) for i in range (1, getMaxYear()+1)]
    labels = ["no data","non forest","forest","gains","gain+loss"]
    pos = 1
    labels[pos:pos] = years
    
    return labels

def getCodes():
    return {getMyClasses()[index]: value for index, value in enumerate(getMyLabel()) }

def getColorTable():
    
    pathname = getTmpDir() + 'color_table.txt'
    
    if not os.path.isfile(pathname):
        
        length = len(getMyClasses())
        color_r = {}
        color_g = {}
        color_b = {}
        
        color_r[0], color_g[0], color_b[0] = mpl.colors.to_rgb('black') #no data
        for i in range(1, getMaxYear()+1):
            color_r[i], color_g[i], color_b[i], _ = utils.colorFader(i)
        color_r[30], color_g[30], color_b[30] = mpl.colors.to_rgb('lightgrey') #non forest
        color_r[40], color_g[40], color_b[40] = mpl.colors.to_rgb('darkgreen') #forest
        color_r[50], color_g[50], color_b[50] = mpl.colors.to_rgb('lightgreen') #gains
        color_r[51], color_g[51], color_b[51] = mpl.colors.to_rgb('purple') #gain + loss
        
        color_r = [int(round(color_r[idx]*255)) for idx in color_r.keys()]
        color_g = [int(round(color_g[idx]*255)) for idx in color_g.keys()]
        color_b = [int(round(color_b[idx]*255)) for idx in color_b.keys()]
        
        color_table = pd.DataFrame({'classes':getMyClasses(), 'red': color_r, 'green': color_g, 'blue': color_b})
        
        color_table.to_csv(pathname, header=False, index=False, sep=' ')
    
    return pathname

def getColorTableGlad():
    
    pathname = getTmpDir() + 'color_table_glad.txt'
    
    if not os.path.isfile(pathname):
    
        classes = [i for i in range(0,9)]
        
        length = len(classes)
        color_r = {}
        color_g = {}
        color_b = {}
        
        color_r[0], color_g[0], color_b[0] = mpl.colors.to_rgb('black') # no data
        color_r[1], color_g[1], color_b[1] = mpl.colors.to_rgb('green') # Foret accord
        color_r[2], color_g[2], color_b[2] = mpl.colors.to_rgb('red') # Pertes GLAD < Pertes GFC
        color_r[3], color_g[3], color_b[3] = mpl.colors.to_rgb('yellow') # Pertes agree
        color_r[4], color_g[4], color_b[4] = mpl.colors.to_rgb('purple') # Pertes GLAD > Pertes GFC
        color_r[5], color_g[5], color_b[5] = mpl.colors.to_rgb('blue') # Gains accord
        color_r[6], color_g[6], color_b[6] = mpl.colors.to_rgb('lightblue') # Gains GLAD > Gains GFC
        color_r[7], color_g[7], color_b[7] = mpl.colors.to_rgb('darkblue') # Gains GLAD < Gains GFC
        color_r[8], color_g[8], color_b[8] = mpl.colors.to_rgb('grey') # Non Foret accord
        
        #transform the dicts into lists
        color_r = [int(round(color_r[idx]*255)) for idx in color_r.keys()]
        color_g = [int(round(color_g[idx]*255)) for idx in color_g.keys()]
        color_b = [int(round(color_b[idx]*255)) for idx in color_b.keys()]
        
        color_table = pd.DataFrame({'classes':classes, 'red': color_r, 'green': color_g, 'blue': color_b})
        
        color_table.to_csv(pathname, header=False, index=False, sep=' ')
        
    return pathname

def getPalette():
    return [
        'yellow',
        'darkred', #loss
        'lightgrey', #non forest
        'darkgreen', #forest
        'lightgreen', #gain
        'black', #ndat
        'purple' #gnls
    ]

def getZonalLabels():
    
    legend = [
        'zone_id',
        'total',
        'no_data',
        'non_forest',
        'forest',
        'gain',
        'gain_loss'
    ]

    years = [ 'loss_{}'.format(str(i)) for i in range(1, getMaxYear()+1)]
    legend[3:3] = years
    
    return legend

def getGladLabels():
    
    my_class = [i for i in range(8+1)]
    fnf_gfc_2000 = ['nodata'] + ['forest']*4 + ['non_forest']*4
    fnf_glad_2010 = ['nodata'] + ['forest']*2 + ['non_forest']*2 + ['forest']*2 + ['non_forest']*2
    chg_gfc = ['nodata','Stable','Loss','Loss','Stable','Gain','Stable','Gain','Stable']
    agree = ['nodata','Yes','No','Yes','No','Yes','No','No','Yes']
    
    df = pd.DataFrame({
        'code': my_class,
        'fnf_gfc_2000': fnf_gfc_2000,
        'fnf_glad_2010': fnf_glad_2010,
        'chg_gfc': chg_gfc,
        'agree': agree
    })
    
    return df