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

prefices=['aperio.','openslide.','tiff.']
excludedKeys=['aperio.Originalheight']

#Build a list of keys whose values are to be logged
def loadLoggedKeys(file):
    try:
        with open(file) as f:
            loggedKeys = f.read().splitlines()
        for key in excludedKeys:
            loggedKeys.remove(key)
        return loggedKeys
    except IOError:
            exit()

def trimKey(key):
    for prefix in prefices:
        if key.find(prefix)==0:
            return key[len(prefix):]
    return key

def outputFieldNames(keys):
    print("{}".format(keys[0]),end="")
    for key in keys[1:]:
        if key not in excludedKeys:
            print("\t{}".format(trimKey(key)),end="")
    print("")

#Merge values for keys aperio.OriginalHeight and aperio.Originalheight
#Some files use one key, some the other
def mergedHeightValues(dict):
    height=''
    Height=''
    if 'aperio.OriginalHeight' in dict:
        Height = dict['aperio.OriginalHeight']
    if 'aperio.Originalheight' in dict:
        height = dict['aperio.Originalheight']
    if Height=='' and height=='':
        return ''
    elif Height!='' and height=='':
        return Height
    elif Height=='' and height!='':
        return height
    else:
        print('Multiple height values for {}/{}'.format(dict['RootDir'],dict['SVSFileName']),file=sys.stderr)
        return Height
    
def outputFileResults(tagValueList, mergedKeys):
    for tagValueDict in tagValueList:
        print('{}'.format(tagValueDict['RootDir']),end='')
        for key in mergedKeys[1:]:
            #Merge values for keys aperio.OriginalHeight and aperio.Originalheight
            if key=='aperio.OriginalHeight':
                print('\t{}'.format(mergedHeightValues(tagValueDict)),end='')
            elif key in tagValueDict:
                print('\t{}'.format(tagValueDict[key]),end='')
            else:
                print('\t{}'.format(''),end='')
        print('')
          
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
    outputAllResults(args,keys)
    

   

            
