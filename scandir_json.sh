#!/bin/bash
#$1 is a directory
#$2 is percent of files to scan
d=$(basename $1)
filecount=$(gsutil ls $1Other/*/*/*.svs|wc -l)
scancount=$((($filecount*$2/100)>1?$filecount*$2/100:1))

mkdir -p progress results errors keys
rm -f progress/$d results/$d errors/$d keys/$d
echo "Scanning "$scancount" of "$filecount" files" >> progress/$d

for f in $(gsutil ls $1Other/*/*/*.svs|sort -R|tail -$scancount)
#for f in `sudo /google/google-cloud-sdk/bin/gsutil ls $1/Other/Tissue_slide_image/*/*.svs`
do
    echo $f >> progress/$d
    sudo gsutil cp $f .
    g=$(basename $f)
    #echo "basename:",$g
    h=$(dirname $f)
    #echo "dirname:",$h
    python ./scan_svs_file_json.py --dir $h --file $g --type $d --keys keys -vvv 2>> errors/$d
    rm -fr $g
done
