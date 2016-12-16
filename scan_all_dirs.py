# -*- coding: utf-8 -*-
"""
Perform some dcm file processing tasks
"""
from __future__ import print_function
import os,sys
import argparse
from os.path import join
import time
import openslide
import json
import subprocess
import random

#Build a list of keys whose values are to be ignored
def loadIgnoredKeys(args):
    with open(args.ignore) as f:
        ignoredKeys = f.read().splitlines()
    return ignoredKeys    

#Need to incrementally add keys to logged keys   
def updateLoggedKeys(args,props,loggedKeys):
    for key in props.keys():
        if key not in loggedKeys and key not in ignoredKeys:
            loggedKeys.append(key)
            if args.verbosity>=2:
                print("Adding tag {}".format(key),file=sys.stderr)

#Process a single svs file.
def scanSvsFile(args,loggedKeys,ignoredKeys,rootDir,svsFile):
    slide=openslide.OpenSlide(svsFile)
    props=slide.properties
    updateLoggedKeys(args,props,loggedKeys)
    keyValues={}
    for key in loggedKeys:
        if key =='RootDir':
            #print("{}".format(args.dir),end="")
            keyValues['RootDir']=rootDir
        elif key =='SVSFileName':
            #print("\t{}".format(args.file),end="")
            keyValues['SVSFileName']=svsFile
        elif key in props.keys():
            #print("\t{}".format(props[key]),end="")
            keyValues[key]=props[key]
        else:
            #print("\t{}".format(""),end="")
            keyValues[key]=""
    return keyValues
    
def scanCaType(args,dir):
    loggedKeys=['RootDir','SVSFilename']
    scanResults=[]
    ignoredKeys = loadIgnoredKeys(args)

    caType = dir.rstrip('/').rpartition('/')[2]
    svsFiles = subprocess.check_output(['gsutil','ls',dir+'Other/*/*/*svs']).split('\n')
    
    if args.percent != '100':
        #Sample a random subset of files
        random.shuffle(svsFiles)
        fileCount = max(float(args.percent)*len(svsFiles)/100,1)
        svsFiles = svsFiles[0:fileCount]

    try:
        with open(args.progress+'/'+caType,'w') as f:
            for svsFile in svsFiles:
                if svsFile!='':
                    rootDir=sysFile.rpartition('/')[0]
                    if args.verbosity>1:
                        print("{}".format(svsFile),file=f)
                    subprocess.call(['gsutil','cp',svsFile,'.'])
                    scanResults.append(scanSVSFile(args,loggedKeys,ignoredKeys,rootDir,svsFile))
                    subprocess.call(['rm',svsFile])
    except IOError:
        print("Can't open progress file {} for write".format(args.progress+'/'+args.type),file=sys.stderr)
        exit()

    #Output results of scanning all files of caType
    try:
        with open(args.results+'/'+caType) as f:
            json.dump(scanResults,f)
    except IOError:
        print("Can't open results  file {} for write".format(args.results+'/'+args.type),file=sys.stderr)
        exit()

    #Output the keys
    try:
        with open(args.keys+'/'+caTtype,'w') as f:
            for key in loggedKeys:
                f.write("%s\n"%key)
    except IOError:
        print("Can't open loggedKeys file {} for write".format(args.keys+'/'+args.type),file=sys.stderr)
        exit()

def scanAllCaType(args):
    dirs=subprocess.check_output(['gsutil','ls','gs://isb-cgc-open/NCI-GDC/legacy/*']).split('\n')
    
    for dir in dirs:
        if args.verbosity>0:
            print("Starting scan of {}".format(dir),file=sys.stderr)
        if dir!='':
            scanType(args,dir)


    
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-r", "--results", type=str, help="path to directory of resulting per-type files", 
                          default='./results')
    parser.add_argument ( "-k", "--keys", type=str, help="path to directory of per-type logged keys files", 
                          default='./keys')
    parser.add_argument ( "-p", "--progress", type=str, help="path to directory of per-type progress files", 
                          default='./progress')
    parser.add_argument ( "-e", "--error", type=str, help="path to directory of per-type error files", 
                          default='./errors')
    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
                          default='./ignoredKeys.txt')
    parser.add_argument ( "-p", "--percent", type=str, help="Fraction of files to scan", 
                          default='1')
    args = parser.parse_args()
    
    t0 = time.time()
    scanAllCaTypes(args)
#    outputScanResults(scanData)
    t1 = time.time()
    
    if args.verbosity>0:
        print("{} seconds".format(t1-t0),file=sys.stderr)


            
