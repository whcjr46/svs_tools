#!/bin/bash
#$1 is a directory
#$2 is percent of files to scan
d=$(basename $1)
filecount=$(sudo /google/google-cloud-sdk/bin/gsutil ls $1Other/*/*/*.svs|wc -l)
scancount=$((($filecount*$2/100)>1?$filecount*$2/100:1))

mkdir -p progress results errors keys
rm -f progress/$d results/$d errors/$d keys/$d
echo "Scanning "$scancount" of "$filecount" files" >> progress/$d

for f in $(sudo /google/google-cloud-sdk/bin/gsutil ls $1Other/*/*/*.svs|sort -R|tail -$scancount)
#for f in `sudo /google/google-cloud-sdk/bin/gsutil ls $1/Other/Tissue_slide_image/*/*.svs`
do
    echo $f >> progress/$d
    sudo /google/google-cloud-sdk/bin/gsutil cp $f .
    g=$(basename $f)
    #echo "basename:",$g
    h=$(dirname $f)
    #echo "dirname:",$h
    python ./scan_svs_file.py --dir $h --file $g --keys keys/$d -vvv 1>> results/$d 2>> errors/$d
    rm -fr $g
done
