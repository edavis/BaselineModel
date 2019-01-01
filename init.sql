create table ratings (results text, date text, team text, rating real);

create table predictions (
  results text,
  date text,
  away text,
  ascore int,
  home text,
  hscore int,
  hmov_pred real,
  error real
);

create table stats (date text, game_count int, hca real);
