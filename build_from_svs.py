# -*- coding: utf-8 -*-
"""
Walk a directory tree starting at the --dir paramenter. Build a TSV table 
of tag values in each svs file. Specific tags to collect 
are listed in tags file.

Output result to standard out.
"""
from __future__ import print_function
from process_svs import loadIgnoredKeys, initScanData, collectSvsTags
import os,sys
import argparse
from os.path import join
import time

def scanSvsFiles(args,scanData):
    svsFileCount = 0
#    scanData={}

#    loggedKeys=loadLoggedKeys(args)
    ignoredKeys=loadIgnoredKeys(args)

    initScanData(scanData)
    
    for svsroot, svsdirs, svsfiles in os.walk(args.dir):
#        zip_file=svsroot.rpartition('/')[2]+'.zip'
        for svsfile in svsfiles:
            filename, extension = os.path.splitext(svsfile)
            if extension == '.svs':
                svsFileCount+=1
                
                collectSvsTags(args,ignoredKeys,svsroot,svsfile,scanData, svsFileCount)
    return svsFileCount
def outputScanResults(scanData,fileCount):
    #Output keys as the the first row
    keys=[]
    for key in scanData:
        if key != 'RootDir' and key != 'SVSFileName':
            keys.append(key)
    keys.sort()
    
    print('RootDir\tSVSFileName',end="")
    for key in keys:
        print("\t{}".format(key.replace(" ","_")),end="")
    print("")
    for i in range(fileCount):
        print('{}\t{}'.format(scanData['RootDir'][i],scanData['SVSFileName'][i]),end="")
        for key in keys:
            print("\t{}".format(scanData[key][i]),end="")
        print("")
        
if __name__ == '__main__':  
    scanData={}  
    parser = argparse.ArgumentParser(description="Build svs image metadata table")
    parser.add_argument ( "-v", "--verbosity", action="count",default=0,help="increase output verbosity" )
    parser.add_argument ( "-d", "--dir", type=str, help="path to directory containing DICOM files", 
                          default='/users/bcliffor/svs/images1/TCGA')
#    parser.add_argument ( "-k", "--keys", type=str, help="path to file containing logged keys", 
#                          default='./loggedKeys.txt')
    parser.add_argument ( "-i", "--ignore", type=str, help="path to file containing ignored keys", 
                          default='./ignoredKeys.txt')
#    parser.add_argument ( "-s", "--scratch", type=str, help="path to scratch directory", 
#                          default='./scratch')
    args = parser.parse_args()
    
    t0 = time.time()
    fileCount = scanSvsFiles(args,scanData)
    outputScanResults(scanData,fileCount)
    t1 = time.time()
    
    if args.verbosity>0:
        print("{} files processed in {} seconds".format(fileCount,t1-t0),file=sys.stderr)

   

            
