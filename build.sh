#!/usr/bin/env bash

rm -f ratings.db
sqlite3 ratings.db < init.sql

( cd www/ && mkdir -p content/ratings/ content/predictions/ )
( cd www/ && rm -rf public/* )

rm -f results2019.csv
make

python updateRatings.py
python generatePages.py

( cd www/ && hugo --buildFuture )

s3cmd -PM sync www/public/ s3://baseline-model/
