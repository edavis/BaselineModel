#!/usr/bin/env python

import csv
import pprint
import sqlite3
import numpy as np
from itertools import groupby
from operator import attrgetter
from collections import namedtuple

TEAM_COUNT = 353

Game = namedtuple('Game', 'dayCount date team1 homefield1 score1 team2 homefield2 score2')
Team = namedtuple('Team', 'name rating')

def build_matrices(count):
    count += 1 # expand to track HCA
    M = np.zeros((count, count), int)
    N = np.zeros(count, int)
    return M, N

def solve(M, N):
    rv = np.linalg.lstsq(M, N, rcond=0)
    return rv[0]

def update_ratings(M, N, games):
    for game in games:
        neutral = (game.homefield1 == game.homefield2 == 0)

        if game.homefield1 in (0, 1): # 0 = neutral, so just pick this one
            home_idx = game.team1 - 1
            home_pts = game.score1
            away_idx = game.team2 - 1
            away_pts = game.score2
        elif game.homefield2 == 1:
            home_idx = game.team2 - 1
            home_pts = game.score2
            away_idx = game.team1 - 1
            away_pts = game.score1

        M[home_idx, home_idx] += 1
        M[away_idx, away_idx] += 1

        M[home_idx, away_idx] -= 1
        M[away_idx, home_idx] -= 1

        N[home_idx] += (home_pts - away_pts)
        N[away_idx] += (away_pts - home_pts)

        if not neutral:
            M[home_idx, -1] += 1
            M[-1, home_idx] += 1
            M[away_idx, -1] -= 1
            M[-1, away_idx] -= 1
            M[-1, -1] += 1
            N[-1] += (home_pts - away_pts)

    return M, N

def build_teams(fname):
    teams = [name.strip() for (_, name) in csv.reader(open(fname))]
    assert len(teams) == TEAM_COUNT, 'incorrect number of teams'
    return teams

def build_games(fname):
    raw_results = csv.reader(open(fname))
    return map(Game._make, [map(int, row) for row in raw_results])

def combine(teams, ratings):
    return map(Team._make, [(team, round(rating, 2)) for (team, rating) in zip(teams, ratings)])

def main():
    conn = sqlite3.connect('ratings.db')
    teams = build_teams('teams.csv')
    game_results = build_games('results.csv')
    daily_games = groupby(game_results, key=attrgetter('date'))
    M, N = build_matrices(TEAM_COUNT)

    for date, games in daily_games:
        print 'Date: %s' % date
        M, N = update_ratings(M, N, games)
        ratings = solve(M, N)
        team_ratings = combine(teams, ratings)
        values = [(date, team.name, team.rating) for team in team_ratings]
        conn.executemany("insert into ratings (date, team, rating) values (?, ?, ?)", values)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
