#!/usr/bin/env python

import sqlite3
from itertools import groupby
from operator import itemgetter
from collections import namedtuple

Row = namedtuple('Row', 'date away ascore home hscore hmov')

def main():
    conn = sqlite3.connect('ratings.db')
    cursor = conn.cursor()

    ratings = cursor.execute('select date, team, rating from ratings order by date asc')
    daily_ratings = groupby(ratings.fetchall(), key=itemgetter(0))

    for date, ratings in daily_ratings:
        cursor.execute('select game_count, hca from stats where date = ?', (date,))
        (game_count, hca) = cursor.fetchone()

        page = open('www/content/ratings/ratings-%s.md' % date, 'w')
        page.write('---\n')
        page.write('title: Daily Ratings Update\n')
        page.write('date: %s-%s-%s\n' % (date[:4], date[4:6], date[6:]))
        page.write('GameCount: %d\n' % game_count)
        page.write('HCA: %.2f\n' % hca)
        page.write('---\n\n')
        page.write('<table class=ratings>\n')

        sorted_ratings = sorted(ratings, key=itemgetter(2), reverse=True)
        for (date, team_name, team_rating) in sorted_ratings:
            team_name = team_name.replace('_', ' ')
            page.write('<tr><td class=rank></td><td class=team>%s</td><td class=rating>%.2f</td></tr>\n' % (team_name, team_rating))

        page.write('</table>\n')
        page.close()

    predictions = cursor.execute('select date, away, ascore, home, hscore, hmov from predictions order by date asc')
    daily_predictions = groupby(predictions.fetchall(), key=itemgetter(0))

    for date, predictions in daily_predictions:
        page = open('www/content/predictions/predictions-%s.md' % date, 'w')
        page.write('---\n')
        page.write('title: Daily Predictions Update\n')
        page.write('date: %s-%s-%s\n' % (date[:4], date[4:6], date[6:]))
        page.write('---\n\n')

        page.write('<table class=predictions>')
        page.write('<tr><th colspan=2>Away</th> <th colspan=2>Home</th> <th class=prediction>Prediction</th></tr>\n')
        for prediction in predictions:
            row = Row._make(prediction)
            page.write('<tr>')
            page.write('<td>%s</td>' % row.away.replace('_', ' '))
            page.write('<td>%d</td>' % row.ascore)
            page.write('<td>%s</td>' % row.home.replace('_', ' '))
            page.write('<td>%d</td>' % row.hscore)
            page.write('<td class=prediction>%.2f</td>' % row.hmov)
            page.write('</tr>\n')
        page.write('</table>')

        page.close()

if __name__ == '__main__':
    main()
