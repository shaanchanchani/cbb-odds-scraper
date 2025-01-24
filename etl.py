from scrapers import (
    get_barttorvik_df,
    get_dratings_df,
    get_evanmiya_df,
    get_kenpom_df,
    get_massey_df
)
from oddsapi import get_odds_data, get_moneyline_odds, get_spread_odds, get_totals_odds
import pandas as pd

odds_data = get_odds_data()

moneyline_odds = get_moneyline_odds(odds_data)
spread_odds = get_spread_odds(odds_data)
totals_odds = get_totals_odds(odds_data)

massey_df = get_massey_df(odds_data)


barttorvik_df = get_barttorvik_df()
dratings_df = get_dratings_df()
evanmiya_df = get_evanmiya_df()
kenpom_df = get_kenpom_df()





crosswalk_df = pd.read_csv('crosswalk.csv')


I have a problem with my Massey scraper. The problem is that no matter what it will also scrape Womens CBB and NBA data.

Therefore we need to mitigate this by leveraging the schedule in Odds Data.

