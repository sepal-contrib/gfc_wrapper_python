import os
import csv
import ee 
import geemap
import math
import shapely.geometry as sg

ee.Initialize()

def get_bounding_box(assetID):
    """return a list of str of the (minx, miny, maxx, maxy) of the asset
    """
    aoi = ee.FeatureCollection('users/bornToBeAlive/aoi_PU')
    aoiJson = geemap.ee_to_geojson(aoi)
    aoiShp = sg.shape(aoiJson['features'][0]['geometry'])
    
    bb = {}
    bb['minx'], bb['miny'], bb['maxx'], bb['maxy'] = aoiShp.bounds
    
    bb['minx'] = str(math.floor(bb['minx']))
    bb['miny'] = str(math.floor(bb['miny']))
    bb['maxx'] = str(math.ceil(bb['maxx']))
    bb['maxy'] = str(math.ceil(bb['maxy']))
    
    return bb
    

def create_FIPS_dic():
    """create the list of the country code in the FIPS norm using the CSV file provided in utils
        
    Returns:
        fips_dic (dic): the country FIPS_codes labelled with english country names
    """
     
    pathname = os.path.join(os.path.dirname(__file__), 'FIPS_code_to_country.csv')
    fips_dic = {}
    with open(pathname, newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            fips_dic[row[1]] = row[3]
            
        fips_sorted = {}
        for key in sorted(fips_dic):
            fips_sorted[key] = fips_dic[key]
        
    return fips_sorted

def get_aoi_name(asset_name):
    """Return the corresponding aoi_name from an assetId"""
    return os.path.split(asset_name)[1].replace('aoi_','')


def pixelCount():
    """pixel_count <- function(x){
  info    <- gdalinfo(x,hist=T)
  buckets <- unlist(str_split(info[grep("bucket",info)+1]," "))
  buckets <- as.numeric(buckets[!(buckets == "")])
  hist    <- data.frame(cbind(0:(length(buckets)-1),buckets))
  hist    <- hist[hist[,2]>0,]
}"""
    
def estimate():
    """estimate <- function(x,y){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0 &
      df$code == y
    ,])/
    nrow(df[
      df$lon_fact%%x == 0 & 
        df$lat_fact%%x == 0 &
        (df$code == 40 | (df$code > 0 & df$code < 30))
      ,])
}"""
    
def allaEstimate():
       """all_estimate <- function(x){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0  & 
      (df$code > 0 & df$code < 30)
    ,])/
    nrow(df[
      df$lon_fact%%x == 0 & 
        df$lat_fact%%x == 0 &
        (df$code == 40 | (df$code > 0 & df$code < 30))
      ,])
}"""
        
def nombre():
    """nombre <- function(x){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0 &
      (df$code == 40 | (df$code > 0 & df$code < 30))
    ,]
  )}"""


