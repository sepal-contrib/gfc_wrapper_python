import os
import sys
from utils import parameters as param

def set_glad2010_map(aoi):
    """
    Args:
        aoi(str) : the aoiId in gee
    """
    outputFile = 'toto'
    
    #retreive useful dir 
    gfc_dir = param.getGfcDir()
    
    #verify that the output already exist
    if os.isFile(outputFile):
        #faire une sortie user 
        return outputFile
    
    #align Glad with GFC 
    mask = gfc_dir + 'gfc_{}_merged.tif'.format(aoi_name)
    
    
    
    
    

  #################### ALIGN GLAD WITH GFC
  mask   <- paste0(gfc_dir,"gfc_",countrycode,"_",types[4],".tif")
  proj   <- proj4string(raster(mask))
  extent <- extent(raster(mask))
  res    <- res(raster(mask))[1]
  
  
  #################### ALIGN GFC TREE COVER WITH SEGMENTS
  input  <- paste0(gfc_dir,"glad2010_",countrycode,".tif")
  ouput  <- paste0(gfc_dir,"glad2010_aligned_",countrycode,".tif")
  
  system(sprintf("gdalwarp -co COMPRESS=LZW -t_srs \"%s\" -te %s %s %s %s -tr %s %s %s %s -overwrite",
                 proj4string(raster(mask)),
                 extent(raster(mask))@xmin,
                 extent(raster(mask))@ymin,
                 extent(raster(mask))@xmax,
                 extent(raster(mask))@ymax,
                 res(raster(mask))[1],
                 res(raster(mask))[2],
                 input,
                 ouput
  ))
  
  #################### COMBINATION FNF 2000
  system(sprintf("gdal_calc.py -A %s --co COMPRESS=LZW --outfile=%s --calc=\"%s\"",
                 paste0(gfc_dir,"gfc_",countrycode,"_",types[1],".tif"),
                 paste0(tmp_dir,"tmp_fnf_2000_",countrycode,".tif"),
                 paste0("(A>=",threshold,")*1+(A<",threshold,")*2")
  ))
  
  
  #################### COMBINATION FNF 2010
  system(sprintf("gdal_calc.py -A %s --co COMPRESS=LZW --overwrite --outfile=%s --calc=\"%s\"",
                 paste0(gfc_dir,"glad2010_aligned_",countrycode,".tif"),
                 paste0(tmp_dir,"tmp_fnf_2010_",countrycode,".tif"),
                 paste0("(A>=",threshold,")*1+(A<",threshold,")*2")
  ))
  
  #################### COMBINATION INTO NATIONAL SCALE MAP
  system(sprintf("gdal_calc.py -A %s -B %s -C %s -D %s --co COMPRESS=LZW --overwrite --outfile=%s --calc=\"%s\"",
                 paste0(tmp_dir,"tmp_fnf_2000_",countrycode,".tif"),
                 paste0(tmp_dir,"tmp_fnf_2010_",countrycode,".tif"),
                 paste0(gfc_dir,"gfc_",countrycode,"_",types[2],".tif"),
                 paste0(gfc_dir,"gfc_",countrycode,"_",types[3],".tif"),
                 paste0(tmp_dir,"tmp_glad_check_",countrycode,".tif"),
                 paste0("(A==1)*(B==1)*((C==0)+(C>=11))*1+",  # Foret accord
                        "(A==1)*(B==1)*( C> 0)*(C < 11)*2+",  # Pertes GLAD < Pertes GFC
                        "(A==1)*(B==2)*( C> 0)*(C < 11)*3+",  # Pertes accord
                        "(A==1)*(B==2)*((C==0)+(C>=11))*4+",  # Pertes GLAD > Pertes GFC
                        "(A==2)*(B==1)*( D==1)*5+",           # Gains accord
                        "(A==2)*(B==1)*( D==0)*6+",           # Gains GLAD > Gains GFC
                        "(A==2)*(B==2)*( D==1)*7+",           # Gains GLAD < Gains GFC
                        "(A==2)*(B==2)*( D==0)*8"             # Non Foret accord
                        )  
  ))
  
  #############################################################
  ### CROP TO COUNTRY BOUNDARIES
  system(sprintf("python %s/oft-cutline_crop.py -v %s -i %s -o %s -a %s",
                 scriptdir,
                 aoi_shp,
                 paste0(tmp_dir,"tmp_glad_check_",countrycode,".tif"),
                 paste0(tmp_dir,"tmp_glad_check_clip_",countrycode,".tif"),
                 aoi_field
  ))
  
  ###############################################################################
  ################### REPROJECT IN EA PROJECTION
  ###############################################################################
  system(sprintf("gdalwarp -t_srs \"%s\" -overwrite -ot Byte -co COMPRESS=LZW %s %s",
                 proj,
                 paste0(tmp_dir,"tmp_glad_check_clip_",countrycode,".tif"),
                 paste0(tmp_dir,"tmp_glad_check_clip_prj_",countrycode,".tif")
  ))
  
  
  ################################################################################
  #################### Add pseudo color table to result
  ################################################################################
  system(sprintf("(echo %s) | oft-addpct.py %s %s",
                 paste0(gfc_dir,"color_table_glad.txt"),
                 paste0(tmp_dir,"tmp_glad_check_clip_prj_",countrycode,".tif"),
                 paste0(tmp_dir,"tmp_glad_map_clip_prj_pct_",countrycode,".tif")
  ))
  
  ################################################################################
  #################### COMPRESS
  ################################################################################
  system(sprintf("gdal_translate -ot Byte -co COMPRESS=LZW %s %s",
                 paste0(tmp_dir,"tmp_glad_map_clip_prj_pct_",countrycode,".tif"),
                 paste0(gfc_dir,"glad_check_",countrycode,"_",threshold,".tif")
  ))
  
#}
