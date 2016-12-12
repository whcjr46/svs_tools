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
import json

#Build a list of keys whose values are to be logged
def loadLoggedKeys(args):
    try:
        with open(args.keys+'/'+args.type) as f:
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
        with open(args.keys+'/'+args.type,'w')as f:
            for key in loggedKeys:
                f.write("%s\n"%key)
    except IOError:
        print("Can't open loggedKeys file {} for write".format(args.keys+'/'+args.type),file=sys.stderr)
    
#Process a single svs file.
def scanSvsFile(args, loggedKeys, ignoredKeys):
    if args.verbosity>3 :
        print("Processing file: ", join(args.dir,args.file), file=sys.stderr)

    slide=openslide.OpenSlide(args.file)
    props=slide.properties
    updateLoggedKeys(args,props,loggedKeys)
    keyValues={}
    for key in loggedKeys:
        if key =='RootDir':
            #print("{}".format(args.dir),end="")
            keyValues['RootDir']=args.dir
        elif key =='SVSFileName':
            #print("\t{}".format(args.file),end="")
            keyValues['SVSFileName']=args.file
        elif key in props.keys():
            #print("\t{}".format(props[key]),end="")
            keyValues[key]=props[key]
        else:
            #print("\t{}".format(""),end="")
            keyValues[key]=""

    #Load any previously saved tags, add new tags, and save
    try:
        f=open("./results/"+args.type,'r+')
        allResults=json.load(f)
    except IOError:
        f=open("./results/"+args.type,'w')
        allResults=[]      
    allResults.append(keyValues)
    f.seek(0)
    json.dump(allResults,f)
    f.close()
    
    
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-d", "--dir", type=str, help="path to directory containing svs files", 
                          default='/users/bcliffor/svs/images1/TCGA')
    parser.add_argument ( "-f", "--file", type=str, help="file to process, assumed to be in .", 
                          default='t1.svs')
    parser.add_argument ( "-k", "--keys", type=str, help="path to file containing logged keys", 
                          default='./keys')
    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
                          default='./ignoredKeys.txt')
    parser.add_argument ( "-t", "--type", type=str, help="TCGA type name", 
                          default='TCGA_ACC')
    
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


            
