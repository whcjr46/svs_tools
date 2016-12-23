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
from multiprocessing import Process,BoundedSemaphore
from shutil import rmtree

#Load previosly logged keys
def loadLoggedKeys(args,caType):
    try:
        with open(args.keys+caType) as f:
            loggedKeys = f.read().splitlines()
    except IOError:
        loggedKeys=['RootDir','SVSFileName']
    return loggedKeys
                    
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
#            if args.verbosity>=2:
#                print("Adding tag {}".format(key),file=sys.stderr)

def loadScannedResults(args,caType):
    if os.path.exists(args.results+caType):
        with open(args.results+caType) as f:
            return json.load(f)
    else:
        return []

#Process a single svs file.
def scanSvsFile(args,loggedKeys,ignoredKeys,rootDir,svsFile):
    print("{}:{}/{}".format(time.ctime(),rootDir,svsFile),file=sys.stdout)
    sys.stdout.flush()
    try:
        slide=openslide.OpenSlide(args.scratch+svsFile)
        props=slide.properties
        updateLoggedKeys(args,props,loggedKeys,ignoredKeys)
        keyValues={}
        for key in loggedKeys:
            if key =='RootDir':
                keyValues['RootDir']=rootDir
            elif key =='SVSFileName':
                keyValues['SVSFileName']=svsFile
            elif key in props.keys():
                keyValues[key]=props[key]
            else:
                keyValues[key]=""
        return (1,keyValues)
    except openslide.OpenSlideError:
        print("Openslide could not open {}{}".format(rootDir,svsFile),file=sys.stderr)
        sys.stderr.flush()
        return (0,0)

def flushResults(args,caType,scanResults,loggedKeys):
    #Output results of scanning files of caType
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

def scanned(rootDir, scanResults):
    for scanResult in scanResults:
        if rootDir==scanResult['RootDir']:
            if args.verbosity>=2:
                print("Skipping {}".format(rootDir),file=sys.stdout)
                sys.stdout.flush()
            return True
    return False
    
def scanCaType(args,dir,sema):
    if args.verbosity>0:
        print("Starting scan of {}".format(dir),file=sys.stdout)
        sys.stdout.flush()
    scannedCount=0
    caType = dir.rstrip('/').rpartition('/')[2]
    
    ignoredKeys=loadIgnoredKeys(args)
    loggedKeys=loadLoggedKeys(args,caType)
    scanResults=loadScannedResults(args,caType)

    
    svsFiles = subprocess.check_output(['gsutil','ls',dir+'Other/*/*/*svs']).split('\n')

    numFiles = len(svsFiles)
    if args.fraction != '100':
        #Sample a random subset of files
        random.shuffle(svsFiles)
        fileCount = int(max(float(args.fraction)*numFiles/100,1))
        svsFiles = svsFiles[0:fileCount]
    else:
        fileCount=numFiles

    with open(args.progress+caType,'a') as f:
        if f.tell()==0:
            print("Scanning {} of {} file". format(fileCount,numFiles),file=f)
            f.flush()
        for svsFile in svsFiles:
            if svsFile!='':
                rootDir=svsFile.rpartition('/')[0]
                if not scanned(rootDir,scanResults):
                    for attempt in range(3):
                        #Copy the file from GS
                        if subprocess.call(['gsutil','-q','cp',svsFile,args.scratch]) == 0:
                            scanResult=scanSvsFile(args,loggedKeys,ignoredKeys,rootDir,svsFile.rpartition('/')[2])
                            subprocess.call(['rm',args.scratch+svsFile.rpartition('/')[2]])
                            if scanResult[0]:
                                scanResults.append(scanResult[1])
                                if args.verbosity>1:
                                    print("{}".format(svsFile),file=f)
                                    f.flush()
                                scannedCount+=1
                                if scannedCount%int(args.flush)==0:
                                    print("{} flushed".format(caType),file=sys.stdout)
                                    sys.stdout.flush()
                                    flushResults(args,caType,scanResults,loggedKeys)
                                break                              
                        else:
                            print("Error copying {}".format(svsFile),file=sys.stderr)
                            sys.stderr.flush()
                    else:
                        print("Failed to scan {}".format(svsFile),file=sys.stderr)
                        sys.stderr.flush()

    flushResults(args,caType,scanResults,loggedKeys)


    if args.verbosity>0:
        print("Completed scan of {}".format(dir),file=sys.stdout)
        sys.stdout.flush()

    sema.release()

        
def scanAllCaTypes(args):
    procs=[]
    dirs=subprocess.check_output(['gsutil','ls','gs://isb-cgc-open/NCI-GDC/legacy/TCGA']).split('\n')
    sema=BoundedSemaphore(int(args.procs))

    for dir in dirs:
        if dir!='':
            sema.acquire()
            p = Process(target = scanCaType, args = (args,dir,sema))
            p.start()
            procs.append((p,dir))
            
    for p in procs:
        p[0].join()

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
    parser.add_argument ( "-c", "--procs", type=str, help="Number of concurrent processes to run", 
                          default='8')
    parser.add_argument ( "-f", "--fraction", type=str, help="Fraction of files to scan as percent", 
                          default='100')
    parser.add_argument ( "-l", "--flush", type=str, help="Count of files to scan between flushes", 
                          default='25')
    parser.add_argument ( "-n", "--klean", type=str, help="Y to remove all files", 
                          default='N')
    args = parser.parse_args()
    
    #Empty the various target directories
#    for dir in (args.results, args.keys, args.progress, args.error, args.scratch):
    for dir in (args.scratch,):
        if os.path.exists(dir):
            rmtree(dir)

    if args.klean=='Y':
        for dir in (args.results, args.keys, args.progress, args.error, args.scratch):
            if os.path.exists(dir):
                rmtree(dir)
            
    for dir in (args.results, args.keys, args.progress, args.error, args.scratch):
        if not os.path.exists(dir):
            os.mkdir(dir)
        
    t0 = time.time()
    scanAllCaTypes(args)
    t1 = time.time()
    
    if args.verbosity>0:
        print("{} seconds".format(t1-t0),file=sys.stdout)


        
