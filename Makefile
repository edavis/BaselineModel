all: results2017.csv teams2017.csv results2018.csv teams2018.csv results2019.csv teams2019.csv

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

clean:
	rm -f results*.csv teams*.csv

.PHONY: clean
