#!/usr/bin/env python

import math
import sqlite3
from itertools import groupby
from operator import itemgetter
from collections import namedtuple

Row = namedtuple('Row', 'date away ascore home hscore hmov_actual hmov_pred error')

def calc_mae(errors):
    a = sum(map(abs, errors))
    b = float(len(errors))
    return a / b

def calc_mse(errors):
    a = sum([error ** 2 for error in errors])
    b = float(len(errors))
    return a / b

def calc_rmse(errors):
    return math.sqrt(calc_mse(errors))

def main(results_fname):
    conn = sqlite3.connect('ratings.db')
    cursor = conn.cursor()

    ratings = cursor.execute('select date, team, rating from ratings where results = ? order by date asc', (results_fname,))
    daily_ratings = groupby(ratings.fetchall(), key=itemgetter(0))

    for date, ratings in daily_ratings:
        cursor.execute('select game_count, hca from stats where date = ?', (date,))
        (game_count, hca) = cursor.fetchone()

        page = open('www/content/ratings/ratings-%s.md' % date, 'w')
        page.write('---\n')
        page.write('Title: Daily Ratings Update\n')
        page.write('Date: %s-%s-%s\n' % (date[:4], date[4:6], date[6:]))
        page.write('GameCount: %d\n' % game_count)
        page.write('HCA: %.2f\n' % hca)
        page.write('---\n\n')
        page.write('<table class=ratings>\n')

        page.write('<tr>')
        page.write('<th class=rank>Rnk</th>')
        page.write('<th class=team>Team</th>')
        page.write('<th class=numeric>Rating</th>')
        page.write('</tr>\n')

        sorted_ratings = sorted(ratings, key=itemgetter(2), reverse=True)
        for (date, team_name, team_rating) in sorted_ratings:
            team_name = team_name.replace('_', ' ')
            page.write('<tr><td class=rank></td><td class=team>%s</td><td class="rating numeric">%.2f</td></tr>\n' % (team_name, team_rating))

        page.write('</table>\n')
        page.close()

    total_errors = []
    predictions = cursor.execute('select date, away, ascore, home, hscore, (hscore-ascore) as hmov_actual, hmov_pred, error from predictions where results = ? order by date asc, home asc', (results_fname,))
    daily_predictions = groupby(predictions.fetchall(), key=itemgetter(0))

    for date, predictions in daily_predictions:
        # calculate error metrics if games have occured
        rows = map(Row._make, predictions)
        have_played = sum([int(row.hscore) + int(row.ascore) for row in rows]) > 0
        if have_played:
            today_errors = [float(row.error) for row in rows]
            total_errors.extend(today_errors)

        page = open('www/content/predictions/predictions-%s.md' % date, 'w')
        page.write('---\n')
        page.write('Title: Daily Predictions Update\n')
        page.write('Date: %s-%s-%s\n' % (date[:4], date[4:6], date[6:]))
        page.write('TotalMAE: %.2f\n' % calc_mae(total_errors))
        page.write('TotalMSE: %.2f\n' % calc_mse(total_errors))
        page.write('TotalRMSE: %.2f\n' % calc_rmse(total_errors))
        if have_played:
            page.write('TodayMAE: %.2f\n' % calc_mae(today_errors))
            page.write('TodayMSE: %.2f\n' % calc_mse(today_errors))
            page.write('TodayRMSE: %.2f\n' % calc_rmse(today_errors))
            page.write('HavePlayed: %d\n' % have_played)
        page.write('---\n\n')

        page.write('<table class="predictions %s">' % ('haveplayed' if have_played else ''))
        page.write('<tr>')

        if have_played:
            page.write('<th class=team>Away</th>')
            page.write('<th class=score>Pts</th>')
            page.write('<th class=team>Home</th>')
            page.write('<th class=score>Pts</th>')
            page.write('<th class="numeric mov">Mov</th>')
            page.write('<th class="numeric prd">Pred</th>')
            page.write('<th class="numeric err">Err</th>')
        else:
            page.write('<th class=team>Away</th>')
            page.write('<th class=team>Home</th>')
            page.write('<th class=numeric>Prediction</th>')

        page.write('</tr>\n')

        for row in rows:
            away = row.away.replace('_', ' ')
            home = row.home.replace('_', ' ')
            page.write('<tr>')

            if have_played:
                page.write('<td class=team>%s</td>' % away)
                page.write('<td class=score>%d</td>' % row.ascore)
                page.write('<td class=team>%s</td>' % home)
                page.write('<td class=score>%d</td>' % row.hscore)
                page.write('<td class=numeric>%d</td>' % row.hmov_actual)
                page.write('<td class=numeric>%.2f</td>' % row.hmov_pred)
                page.write('<td class=numeric>%.2f</td>' % row.error)
            else:
                page.write('<td class=team>%s</td>' % away)
                page.write('<td class=team>%s</td>' % home)
                page.write('<td class=numeric>%.2f</td>' % row.hmov_pred)

            page.write('</tr>\n')

        page.write('</table>')
        page.close()

if __name__ == '__main__':
    main('results2017.csv')
    main('results2018.csv')
    main('results2019.csv')
