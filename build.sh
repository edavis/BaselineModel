#!/usr/bin/env bash

rm -f ratings.db
sqlite3 ratings.db < init.sql

( cd www/ && mkdir -p content/ratings/ content/predictions/ )

if [[ $NEWGAMES ]]; then
  rm -f results2019.csv
fi
make

if [[ $REBUILD ]]; then

( cd www/ && rm -rf content/ratings/* content/predictions/* )

# 2016-17
echo "Building 2016-17 season"
python updateRatings.py -r results2017.csv -t teams2017.csv -n 351
python generatePages.py -r results2017.csv

# 2017-18
echo "Building 2017-18 season"
python updateRatings.py -r results2018.csv -t teams2018.csv -n 351
python generatePages.py -r results2018.csv

fi

# 2018-19
echo "Building 2018-19 season"
python updateRatings.py -r results2019.csv -t teams2019.csv -n 353
python generatePages.py -r results2019.csv

( cd www/ && rm -rf public/* )
( cd www/ && hugo --buildFuture )

if [[ $UPLOAD ]]; then
  s3cmd -PM sync www/public/ s3://baseline-model/
fi
