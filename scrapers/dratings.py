import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from io import StringIO

def fetch_dratings():
    """
    Fetches game data from dratings.com using BeautifulSoup
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://www.dratings.com/predictor/ncaa-basketball-predictions/"
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='tablesaw')
    
    if not table:
        print("No table found on the page.")
        return pd.DataFrame()
    
    # Parse table HTML with pandas using StringIO
    table_html = str(table)
    html_io = StringIO(table_html)
    
    try:
        tables = pd.read_html(html_io)
        if not tables:
            print("No data could be extracted from the table.")
            return pd.DataFrame()
            
        df = tables[0]
        # Print column names and types for debugging
        print("Column names:", df.columns.tolist())
        print("\nColumn types:\n", df.dtypes)
        return df
        
    except Exception as e:
        print(f"Error parsing table: {str(e)}")
        return pd.DataFrame()

def clean_dratings(df):
    """
    Cleans the DataFrame by processing team names, spreads, and probabilities
    """
    if df.empty:
        return df
    
    # Create a copy of the DataFrame
    df_clean = df.copy()
    
    # Clean column names and convert to string type where needed
    df_clean.columns = df_clean.columns.str.strip()
    df_clean.columns = df_clean.columns.str.replace(' ', '_').str.lower()
    
    # Convert columns to string type if they aren't already
    string_columns = ['teams', 'best_spread', 'win', 'total_points']
    for col in string_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
    
    # Extract team names
    team_pattern = r'(?P<AwayTeam>.+?)\s*\((?P<AwayRecord>\d+-\d+)\)\s*(?P<HomeTeam>.+?)\s*\((?P<HomeRecord>\d+-\d+)\)'
    teams_extracted = df_clean['teams'].str.extract(team_pattern)
    
    if teams_extracted.empty:
        print("Could not extract team names.")
        return pd.DataFrame()
    
    # Clean team names
    df_clean['Away Team'] = teams_extracted['AwayTeam'].str.strip()
    df_clean['Home Team'] = teams_extracted['HomeTeam'].str.strip()
    
    # Extract win probabilities
    win_pattern = r'(?P<AwayWinPct>\d+\.?\d*)%\s*(?P<HomeWinPct>\d+\.?\d*)%'
    win_extracted = df_clean['win'].str.extract(win_pattern)
    
    # Convert win probabilities to float
    df_clean['Away Team Win Probability'] = pd.to_numeric(win_extracted['AwayWinPct'], errors='coerce')
    df_clean['Home Team Win Probability'] = pd.to_numeric(win_extracted['HomeWinPct'], errors='coerce')
    
    # Extract spreads
    spread_pattern = r'(?P<AwaySpread>[+-]?\d+½?)\s*[-+]\d+\s*(?P<HomeSpread>[+-]?\d+½?)\s*[-+]\d+'
    try:
        spread_extracted = df_clean['best_spread'].str.extract(spread_pattern)
        
        # Convert spreads to float, handling '½' as 0.5
        def convert_spread(x):
            if pd.isnull(x):
                return np.nan
            return float(x.replace('½', '.5')) if '½' in x else float(x)
        
        df_clean['Away Team Spread'] = spread_extracted['AwaySpread'].apply(convert_spread)
        df_clean['Home Team Spread'] = spread_extracted['HomeSpread'].apply(convert_spread)
    except Exception as e:
        print(f"Error processing spreads: {str(e)}")
        df_clean['Away Team Spread'] = np.nan
        df_clean['Home Team Spread'] = np.nan
    
    # Convert projected total to numeric
    df_clean['Projected Total'] = pd.to_numeric(df_clean['total_points'], errors='coerce')
    
    # Select and order final columns
    columns = [
        'Away Team',
        'Home Team',
        'Away Team Spread',
        'Home Team Spread',
        'Away Team Win Probability',
        'Home Team Win Probability',
        'Projected Total'
    ]
    
    return df_clean[columns]