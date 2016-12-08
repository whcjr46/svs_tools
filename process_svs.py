# -*- coding: utf-8 -*-
"""
Perform some dcm file processing tasks
"""
from __future__ import print_function

import os,sys
from os.path import join
import openslide

#Build a list of keys whose values are to be logged
def loadLoggedKeys(args):
    with open(args.keys) as f:
        loggedKeys = f.read().splitlines()
    loggedKeys.sort()
    return loggedKeys

#Build a list of keys whose values are to be ignored
def loadIgnoredKeys(args):
    with open(args.ignore) as f:
        ignoredKeys = f.read().splitlines()
    return ignoredKeys    

#Output tag names as the first row of the table   
def initScanData(scanData):
    scanData['RootDir']=[]
    scanData['SVSFileName']=[]
    
#Process a single svs file.
def collectSvsTags(args, ignoredKeys, svsroot, svsfile, scanData, fileCount):
#    tcia_path = "gs://isb-cgc-open/NCI-GDC/legacy/TCGA/"
    if args.verbosity>=3 :
        print("Processing file: ", join(svsroot,svsfile), file=sys.stderr)
    #Output the zip and svs file paths
    scanData['RootDir'].append(svsroot)
    scanData['SVSFileName'].append(svsfile)
#    print("{}\t{}".format(svsroot,svsfile),end="")
#    ds = dicom.read_file(join(svsroot,svsfile), stop_before_pixels=True)
    slide=openslide.OpenSlide(join(svsroot,svsfile))
    props=slide.properties
    for key in props.keys():
        if key not in ignoredKeys:
            if key not in scanData:
                if args.verbosity>=2:
                    print("Adding key {}".format(key),file=sys.stderr)
                scanData[key] = []
                #Append nulls for all previously processed files
                for i in range(fileCount-1):
                    scanData[key].append("")
    #Add values for all known keys
    for key in scanData:
        if key!='RootDir' and key!='SVSFileName':
            if key in props.keys():
                scanData[key].append(props[key])
            else:
                scanData[key].append("")
#    print("")
    
if __name__ == '__main__':    
    pass
   

            
