#!/usr/bin/env bash

sqlite3 ratings.db <<<'delete from ratings'
rm -f results.csv && make results.csv
python updateRatings.py
( cd www/ && hugo )
