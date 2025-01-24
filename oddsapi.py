import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

def get_odds_data(sport="basketball_ncaab", region="us", markets="h2h,spreads,totals"):
    """
    Fetches odds data from the API for specified sport and markets.
    
    Parameters:
    sport (str): Sport key (default: basketball_ncaab)
    region (str): Region for odds (default: us)
    markets (str): Comma-separated markets to fetch (default: h2h,spreads,totals)
    
    Returns:
    dict: Raw API response data
    """
    key = os.getenv("ODDS_API_KEY")
    if not key:
        raise ValueError("ODDSAPI key not found in environment variables.")
        
    base_url = "https://api.the-odds-api.com"
    odds_url = f"{base_url}/v4/sports/{sport}/odds/?apiKey={key}&regions={region}&markets={markets}&oddsFormat=american"
    
    try:
        response = requests.get(odds_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Error occurred: {err}")
        return None

def get_moneyline_odds(data):
    """
    Processes moneyline (h2h) odds data into a DataFrame.
    """
    h2h_records = []
    for game in data:
        game_time = game.get('commence_time')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        if not all([game_time, home_team, away_team]):
            continue
            
        for bookmaker in game.get('bookmakers', []):
            sportsbook = bookmaker.get('title')
            for market in bookmaker.get('markets', []):
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    home_ml = away_ml = None
                    for outcome in outcomes:
                        if outcome.get('name') == home_team:
                            home_ml = outcome.get('price')
                        elif outcome.get('name') == away_team:
                            away_ml = outcome.get('price')
                    
                    h2h_records.append({
                        'Game Time': game_time,
                        'Home Team': home_team,
                        'Away Team': away_team,
                        'Home Team Moneyline': home_ml,
                        'Away Team Moneyline': away_ml,
                        'Sportsbook': sportsbook
                    })
    
    return pd.DataFrame(h2h_records)

def get_spread_odds(data):
    """
    Processes spread odds data into a DataFrame.
    """
    spreads_records = []
    for game in data:
        game_time = game.get('commence_time')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        if not all([game_time, home_team, away_team]):
            continue
            
        for bookmaker in game.get('bookmakers', []):
            sportsbook = bookmaker.get('title')
            for market in bookmaker.get('markets', []):
                if market.get('key') == 'spreads':
                    outcomes = market.get('outcomes', [])
                    home_spread = away_spread = home_price = away_price = None
                    for outcome in outcomes:
                        if outcome.get('name') == home_team:
                            home_spread = outcome.get('point')
                            home_price = outcome.get('price')
                        elif outcome.get('name') == away_team:
                            away_spread = outcome.get('point')
                            away_price = outcome.get('price')
                            
                    spreads_records.append({
                        'Game Time': game_time,
                        'Home Team': home_team,
                        'Away Team': away_team,
                        'Home Team Spread': home_spread,
                        'Home Team Price': home_price,
                        'Away Team Spread': away_spread,
                        'Away Team Price': away_price,
                        'Sportsbook': sportsbook
                    })
    
    return pd.DataFrame(spreads_records)

def get_totals_odds(data):
    """
    Processes totals (over/under) odds data into a DataFrame.
    """
    totals_records = []
    for game in data:
        game_time = game.get('commence_time')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        if not all([game_time, home_team, away_team]):
            continue
            
        for bookmaker in game.get('bookmakers', []):
            sportsbook = bookmaker.get('title')
            for market in bookmaker.get('markets', []):
                if market.get('key') == 'totals':
                    outcomes = market.get('outcomes', [])
                    over = under = over_price = under_price = None
                    for outcome in outcomes:
                        if outcome.get('name') == 'Over':
                            over = outcome.get('point')
                            over_price = outcome.get('price')
                        elif outcome.get('name') == 'Under':
                            under = outcome.get('point')
                            under_price = outcome.get('price')
                            
                    projected_total = (over + under) / 2 if over and under else None
                    
                    totals_records.append({
                        'Game Time': game_time,
                        'Home Team': home_team,
                        'Away Team': away_team,
                        'Projected Total': projected_total,
                        'Over Point': over,
                        'Over Price': over_price,
                        'Under Point': under,
                        'Under Price': under_price,
                        'Sportsbook': sportsbook
                    })
    
    return pd.DataFrame(totals_records)