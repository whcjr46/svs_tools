#!/bin/bash
for f in `sudo /google/google-cloud-sdk/bin/gsutil ls gs://isb-cgc-open/NCI-GDC/legacy/TCGA/*ACC/Other/Tissue_slide_image/*/*.svs`
do
    #        echo $f
    sudo /google/google-cloud-sdk/bin/gsutil cp $f .
    g=$(basename $f)
    #echo "basename:",$g
    h=$(dirname $f)
    #echo "dirname:",$h
    python ./scan_svs_file_json.py --file $g -vvv
    rm -fr $g
done
