#!/bin/bash
for d in `sudo /google/google-cloud-sdk/bin/gsutil ls gs://isb-cgc-open/NCI-GDC/legacy/TCGA`
do
    bash ./scandir.sh $d 1
done
