#!/usr/bin/env bash

## 200M

#python -u generateCurves.py -b limitdb2 -t coord_tweets -f1 130000 -f2 135000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets -f1 500000 -f2 550000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets -f1 1000000 -f2 1250000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets -f1 5000000 -f2 10000000 |& tee -a generateCurves.log

#python -u generateCurves.py -b limitdb2 -t coord_tweets_sorted -f1 130000 -f2 135000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets_sorted -f1 500000 -f2 550000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets_sorted -f1 1000000 -f2 1250000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb2 -t coord_tweets_sorted -f1 5000000 -f2 10000000 |& tee -a generateCurves.log

## 10M

#python -u generateCurves.py -b limitdb -t coord_tweets -f1 130000 -f2 135000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets -f1 500000 -f2 550000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets -f1 1000000 -f2 1250000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets -f1 5000000 -f2 10000000 |& tee -a generateCurves.log

#python -u generateCurves.py -b limitdb -t coord_tweets_sorted -f1 130000 -f2 135000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets_sorted -f1 500000 -f2 550000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets_sorted -f1 1000000 -f2 1250000 |& tee -a generateCurves.log
#python -u generateCurves.py -b limitdb -t coord_tweets_sorted -f1 5000000 -f2 10000000 |& tee -a generateCurves.log

## 100M

python -u generateCurves.py -b limitdb1 -t coord_tweets -f1 130000 -f2 135000 |& tee -a generateCurves.log
python -u generateCurves.py -b limitdb1 -t coord_tweets -f1 500000 -f2 550000 |& tee -a generateCurves.log
python -u generateCurves.py -b limitdb1 -t coord_tweets -f1 1000000 -f2 1250000 |& tee -a generateCurves.log
python -u generateCurves.py -b limitdb1 -t coord_tweets -f1 5000000 -f2 10000000 |& tee -a generateCurves.log

