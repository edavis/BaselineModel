#!/usr/bin/env bash

# clear out ratings.db
sqlite3 ratings.db 'delete from ratings'
sqlite3 ratings.db 'delete from predictions'
sqlite3 ratings.db 'delete from stats'

# download latest games
rm -f results.csv && make results.csv

# add ratings to ratings.db
python updateRatings.py

# generate a new ratings post for each day in the database
python generatePages.py

# rebuild the site
( cd www/ && rm -rf public/* && hugo --buildFuture )
