all: cb2020 cb2019
cb2020: results2020.csv teams2020.csv
cb2019: results2019.csv teams2019.csv

teams2017.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=292154&sub=11590&all=1&mode=3&format=2"
results2017.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=292154&sub=11590&all=1&mode=3&format=1&sch=on"

teams2018.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&format=2"
results2018.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=298892&sub=11590&all=1&mode=3&format=1&sch=on"

teams2019.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=2"
results2019.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=305972&sub=11590&all=1&mode=3&format=1&sch=on"

teams2020.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=cb2020&sub=11590&all=1&mode=2&format=2"
results2020.csv:
	wget -O $@ "https://www.masseyratings.com/scores.php?s=cb2020&sub=11590&all=1&mode=2&format=1&sch=on"

clean:
	rm -f results*.csv teams*.csv

.PHONY: clean
