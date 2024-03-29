#!/usr/bin/env python

import csv
import sqlite3
import numpy as np
from itertools import groupby
from operator import attrgetter
from collections import namedtuple

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

        mov = home_pts - away_pts

        # Halve the excess beyond the mpd when calculating the mov
        mpd = 14
        if mov > 0 and abs(mov) > mpd:
            mov = mpd + (mov - mpd) / 2.0
        elif mov < 0 and abs(mov) > mpd:
            mov = -mpd - (abs(mov) - mpd) / 2.0

        mov = int(round(mov, 0))
        N[home_idx] += mov
        N[away_idx] += -mov

        neutral = (game.homefield1 == game.homefield2 == 0)
        if not neutral:
            M[home_idx, -1] += 1
            M[-1, home_idx] += 1
            M[away_idx, -1] -= 1
            M[-1, away_idx] -= 1
            M[-1, -1] += 1
            N[-1] += mov

    return M, N

def build_predictions(lookup, ratings, hca, games):
    for game in games:
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

        neutral = (game.homefield1 == game.homefield2 == 0)

        if not neutral:
            hmov_pred = (ratings[home_idx] + hca) - ratings[away_idx]
        else:
            hmov_pred = ratings[home_idx] - ratings[away_idx]

        if home_pts + away_pts > 0:
            error = hmov_pred - (home_pts - away_pts)
        else:
            error = 0

        yield (lookup[away_idx], away_pts, lookup[home_idx], home_pts, hmov_pred, error)

def build_teams(fname):
    teams = [name.strip() for (_, name) in csv.reader(open(fname))]
    return teams

def parse_results(fname):
    raw_results = csv.reader(open(fname))
    return map(Game._make, [map(int, row) for row in raw_results])

def build_team_ratings(teams, ratings):
    return map(Team._make, [(team, round(rating, 2)) for (team, rating) in zip(teams, ratings)])

def main(results_fname, teams_fname, team_count):
    conn = sqlite3.connect('ratings.db')

    teams = build_teams(teams_fname)
    assert len(teams) == team_count, 'incorrect number of teams'

    game_results = parse_results(results_fname)
    daily_games = groupby(game_results, key=attrgetter('date'))
    M, N = build_matrices(team_count)
    game_count = 0

    ratings = None
    hca = None

    # map each team idx to a team name
    teams_lookup = {idx: name for (idx, name) in zip(xrange(team_count), teams)}

    for date, games in daily_games:
        games = list(games)

        # wait until ratings and HCA stablize
        if game_count >= 1200:
            preds = build_predictions(teams_lookup, ratings, hca, games)
            values = [(results_fname, date, away, ascore, home, hscore, hmov_pred, error) for (away, ascore, home, hscore, hmov_pred, error) in preds]
            conn.executemany('insert into predictions (results, date, away, ascore, home, hscore, hmov_pred, error) values (?, ?, ?, ?, ?, ?, ?, ?)', values)

        if sum([g.score1 + g.score2 for g in games]) > 0:
            M, N = update_ratings(M, N, games)
            ratings = solve(M, N)
            team_ratings = build_team_ratings(teams, ratings)
            values = [(results_fname, date, team.name, team.rating) for team in team_ratings]
            conn.executemany('insert into ratings (results, date, team, rating) values (?, ?, ?, ?)', values)

            game_count += len(games)
            hca = max(3.5, ratings[-1])
            conn.execute('insert into stats (date, game_count, hca) values (?, ?, ?)', (date, game_count, hca))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--results')
    parser.add_argument('-t', '--teams')
    parser.add_argument('-n', '--num', type=int)
    args = parser.parse_args()

    main(args.results, args.teams, args.num)
