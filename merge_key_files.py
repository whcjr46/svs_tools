 # -*- coding: utf-8 -*-
"""
Walk a directory tree starting at the --dir paramenter. Build a TSV table 
of tag values in each svs file. Specific tags to collect 
are listed in tags file.

Output result to standard out.
"""
from __future__ import print_function
import os,sys
import argparse
from os.path import join
import time

#Build a list of keys whose values are to be logged
def loadLoggedKeys(file):
    try:
        with open(file) as f:
            loggedKeys = f.read().splitlines()
    except IOError:
            loggedKeys=[]
    return loggedKeys

def scanKeyFiles(args):
    mergedKeys=[]
    for root, dirs, files in os.walk(args.keys):
        for file in files:
            loggedKeys = loadLoggedKeys(join(root,file))
            for key in loggedKeys:
                if key not in mergedKeys:
                    mergedKeys.append(key)

    return mergedKeys

def outputMergedKeys(args,mergedKeys):
    try:
        with open(args.merged+"/keys",'w') as f:
            #Assume first two keys are RootDir and SVSFileName
            f.write("%s\n"%mergedKeys.pop(0))
            f.write("%s\n"%mergedKeys.pop(0))
            mergedKeys.sort()
            for key in mergedKeys:
                f.write("%s\n"%key)
    except IOError:
        print("Can't open loggedKeys file for write")
        
if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-r", "--results", type=str, help="path to directory containing results files", 
                          default='./results')
    parser.add_argument ( "-k", "--keys", type=str, help="path to directory of key files", 
                          default='./keys')
    parser.add_argument ( "-m", "--merged", type=str, help="path to directory of merged results", 
                          default='./merged')
#    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
#                          default='./ignoredKeys.txt')
    args = parser.parse_args()
    
    mergedKeys=scanKeyFiles(args)
    outputMergedKeys(args,mergedKeys)
    

   

            
