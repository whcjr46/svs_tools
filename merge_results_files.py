 # -*- coding: utf-8 -*-
"""
Merge separate json encoded  metadata files. Each file is a list of dictionaries. Each dictionary is keyed by svs tags.
Output result as a tsv file to standard out.
"""
from __future__ import print_function
import os,sys
import argparse
from os.path import join
import time
import json

#Build a list of keys whose values are to be logged
def loadLoggedKeys(file):
    try:
        with open(file) as f:
            loggedKeys = f.read().splitlines()
    except IOError:
            exit()
    return loggedKeys

def outputFieldNames(keys):
    print("{}".format(keys[0]),end="")
    for key in keys[1:]:
        print("\t{}".format(key),end="")
    print("")
          
def outputFileResults(tagValueList, mergedKeys):
    for tagValueDict in tagValueList:
        print('{}'.format(tagValueDict['RootDir']),end="")
        for key in mergedKeys[1:]:
            if key in tagValueDict:
                print('\t{}'.format(tagValueDict[key]),end="")
            else:
                print('\t{}'.format(''),end="")
        print("")
          
def outputAllResults(args,mergedKeys):
    outputFieldNames(mergedKeys)
    for root, dirs, files in os.walk(args.results):
        for file in files:
            with open(join(root,file)) as f:
                tagValueList=json.load(f)
                outputFileResults(tagValueList, mergedKeys)

    return mergedKeys

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-r", "--results", type=str, help="path to directory containing results files", 
                          default='./results')
    parser.add_argument ( "-k", "--keys", type=str, help="path to directory of key files", 
                          default='keys')
    parser.add_argument ( "-m", "--merged", type=str, help="path to directory of merged results", 
                          default='./merged')
#    parser.add_argument ( "-m", "--file", type=str, help="name of merged results file", 
#                          default='results')
#    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
#                          default='./ignoredKeys.txt')
    args = parser.parse_args()

    keys=loadLoggedKeys(args.merged+'/'+args.keys)
    print("{}".format(keys),file=sys.stderr)
    outputAllResults(args,keys)
    

   

            
