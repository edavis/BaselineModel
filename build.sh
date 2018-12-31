#!/usr/bin/env bash

# clear out ratings.db
rm -f ratings.db
sqlite3 ratings.db < init.sql

# re-download results of latest season only
rm -f results2019.csv && make results2019.csv

# make sure everything else has been built (previous seasons, teams, etc)
make

# add ratings to ratings.db
python updateRatings.py

# clear out content
( cd www/ && mkdir -p content/ratings/ content/predictions/ )
( cd www/ && rm -rf content/ratings/* content/predictions/* public/* )

# generate a new ratings/predictions post for each day in the database
python generatePages.py

# rebuild the site
( cd www/ && hugo --buildFuture )
