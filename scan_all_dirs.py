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
from multiprocessing import Process

#Build a list of keys whose values are to be ignored
def loadIgnoredKeys(args):
    with open(args.ignore) as f:
        ignoredKeys = f.read().splitlines()
    return ignoredKeys    

#Need to incrementally add keys to logged keys   
def updateLoggedKeys(args,props,loggedKeys,ignoredKeys):
    for key in props.keys():
        if key not in loggedKeys and key not in ignoredKeys:
            loggedKeys.append(key)
            if args.verbosity>=2:
                print("Adding tag {}".format(key),file=sys.stderr)

#Process a single svs file.
def scanSvsFile(args,loggedKeys,ignoredKeys,rootDir,svsFile):
#    print("Opening {}".format(svsFile))
    slide=openslide.OpenSlide(args.scratch+svsFile)
    props=slide.properties
    updateLoggedKeys(args,props,loggedKeys,ignoredKeys)
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
    loggedKeys=['RootDir','SVSFileName']
    scanResults=[]
    ignoredKeys = loadIgnoredKeys(args)

    caType = dir.rstrip('/').rpartition('/')[2]
    svsFiles = subprocess.check_output(['gsutil','ls',dir+'Other/*/*/*svs']).split('\n')
    
    if args.fraction != '100':
        #Sample a random subset of files
        random.shuffle(svsFiles)
        fileCount = int(max(float(args.fraction)*len(svsFiles)/100,1))
        svsFiles = svsFiles[0:fileCount]
    else:
        fileCount=len(svsFiles)

    try:
        with open(args.progress+caType,'w') as f:
            print("Scanning {} of {} file". format(fileCount, len(svsFiles)),file=f)
            for svsFile in svsFiles:
                if svsFile!='':
                    rootDir=svsFile.rpartition('/')[0]
                    if args.verbosity>1:
                        print("{}".format(svsFile),file=f)
                        f.flush()
                    #Copy the file from GS
                    if subprocess.call(['gsutil','-q','cp',svsFile,args.scratch]) == 0:
                        scanResults.append(scanSvsFile(args,loggedKeys,ignoredKeys,rootDir,svsFile.rpartition('/')[2]))
                        subprocess.call(['rm',args.scratch+svsFile.rpartition('/')[2]])
                    else:
                        print("Error copying {}".format(svsFile),file=sys.stderr
    except IOError:
        print("Can't open progress file {} for write".format(args.progress+caType),file=sys.stderr)
        exit()

    #Output results of scanning all files of caType
    try:
        with open(args.results+caType,'w') as f:
            json.dump(scanResults,f)
    except IOError:
        print("Can't open results file {} for write".format(args.results+caType),file=sys.stderr)
        exit()

    #Output the keys
    try:
        with open(args.keys+caType,'w') as f:
            for key in loggedKeys:
                f.write("%s\n"%key)
    except IOError:
        print("Can't open loggedKeys file {} for write".format(args.keys+caType),file=sys.stderr)
        exit()

def scanAllCaTypes(args):
    procs=[]
    dirs=subprocess.check_output(['gsutil','ls','gs://isb-cgc-open/NCI-GDC/legacy/TCGA']).split('\n')
    
    for dir in dirs:
        if dir!='':
            if args.verbosity>0:
                print("Starting scan of {}".format(dir),file=sys.stderr)
            p = Process(target = scanCaType, args = (args,dir))
            p.start()
            procs.append((p,dir))
    for p in procs:
        p[0].join()
        if args.verbosity>0:
            print("scan of {} completed".format(p[1]),file=sys.stderr)
    
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-r", "--results", type=str, help="Directory of resulting per-type files", 
                          default='./results/')
    parser.add_argument ( "-k", "--keys", type=str, help="Directory of per-type logged keys files", 
                          default='./keys/')
    parser.add_argument ( "-p", "--progress", type=str, help="Directory of per-type progress files", 
                          default='./progress/')
    parser.add_argument ( "-e", "--error", type=str, help="Directory of per-type error files", 
                          default='./errors/')
    parser.add_argument ( "-s", "--scratch", type=str, help="Directory into which to copy .svs files", 
                          default='./scratch/')
    parser.add_argument ( "-i", "--ignore", type=str, help="file containing ignored keys", 
                          default='./ignoredKeys.txt')
    parser.add_argument ( "-f", "--fraction", type=str, help="Fraction of files to scan as percent", 
                          default='1')
    args = parser.parse_args()
    
    t0 = time.time()
    scanAllCaTypes(args)
#    outputScanResults(scanData)
    t1 = time.time()
    
    if args.verbosity>0:
        print("{} seconds".format(t1-t0),file=sys.stderr)


            
