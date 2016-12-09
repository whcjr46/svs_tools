# -*- coding: utf-8 -*-
"""
Perform some dcm file processing tasks
"""
from __future__ import print_function
from process_svs import loadIgnoredKeys, initScanData, collectSvsTags
import os,sys
import argparse
from os.path import join
import time
import openslide
from cgi import log

#Build a list of keys whose values are to be logged
def loadLoggedKeys(args):
    try:
        with open(args.keys) as f:
            loggedKeys = f.read().splitlines()
    except IOError:
        loggedKeys=[]
    return loggedKeys

#Build a list of keys whose values are to be ignored
def loadIgnoredKeys(args):
    with open(args.ignore) as f:
        ignoredKeys = f.read().splitlines()
    return ignoredKeys    

#Output tag names as the first row of the table   
def updateLoggedKeys(args,props,loggedKeys):
    if 'RootDir' not in loggedKeys:
        loggedKeys.append('RootDir')
    if 'SVSFileName' not in loggedKeys:
        loggedKeys.append('SVSFileName')
    for key in props.keys():
        if key not in loggedKeys and key not in ignoredKeys:
            loggedKeys.append(key)
            if args.verbosity>=2:
                print("Adding tag {}".format(key),file=sys.stderr)
            
    #Output the updated list
    try:
        with open(args.keys,'w')as f:
            for key in loggedKeys:
                f.write("%s\n"%key)
    except IOError:
        print("Can't open loggedKeys file for write")
    
#Process a single svs file.
def scanSvsFile(args, loggedKeys, ignoredKeys):
    if args.verbosity>=3 :
        print("Processing file: ", join(args.dir,args.file), file=sys.stderr)

    slide=openslide.OpenSlide(args.file)
    props=slide.properties
    updateLoggedKeys(args,props,loggedKeys)
    for key in loggedKeys:
        if key =='RootDir':
            print("{}".format(args.dir),end="")
        elif key =='SVSFileName':
            print("\t{}".format(args.file),end="")
        elif key in props.keys():
            print("\t{}".format(props[key]),end="")
        else:
            print("\t{}".format(""),end="")
    print("")
    
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-d", "--dir", type=str, help="path to directory containing DICOM files", 
                          default='/users/bcliffor/svs/images1/TCGA')
    parser.add_argument ( "-f", "--file", type=str, help="file to process, assumed to be in .", 
                          default='t1.svs')
    parser.add_argument ( "-k", "--keys", type=str, help="path to file containing logged keys", 
                          default='./loggedKeys.txt')
    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
                          default='./ignoredKeys.txt')
#    parser.add_argument ( "-s", "--scratch", type=str, help="path to scratch directory", 
#                          default='./scratch')
    args = parser.parse_args()
    
    loggedKeys = loadLoggedKeys(args)
    ignoredKeys = loadIgnoredKeys(args)
    
    t0 = time.time()
    scanSvsFile(args,loggedKeys,ignoredKeys)
#    outputScanResults(scanData)
    t1 = time.time()
    
    if args.verbosity>2:
        print("{} seconds".format(t1-t0),file=sys.stderr)


            
