#!/bin/bash
rm errors/* keys/* progress/* results/*
for d in `gsutil ls gs://isb-cgc-open/NCI-GDC/legacy/TCGA`
do
    bash ./scandir_json.sh $d 1&
done
