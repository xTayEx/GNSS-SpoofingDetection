#!/bin/bash

for i in {3..9}
do
    for j in {0..25}
    do
        python data_prepare.py --chunk_index $i --route_index $j
    done
done