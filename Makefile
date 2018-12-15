all: results.csv teams.csv

results.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=1"

teams.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=2"

clean:
	rm -f results.csv teams.csv

.PHONY: clean
