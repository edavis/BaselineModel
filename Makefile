all: results.csv teams.csv ratings.db

results.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=1"

teams.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=2"

ratings.db:
	sqlite3 $@ <<<'create table if not exists ratings (date text, team text, rating real)'
	sqlite3 $@ <<<'create table if not exists stats (date text, game_count int, hca real)'

clean:
	rm -f results.csv teams.csv

.PHONY: clean
