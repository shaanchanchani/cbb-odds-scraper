import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from datetime import datetime, timedelta

def fetch_barttorvik():
    """
    Fetches game data from barttorvik.com using BeautifulSoup
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://www.barttorvik.com/schedule.php"
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    games = []
    for row in rows:
        teams = row.find_all('a', href=lambda x: x and 'team.php' in x)
        if len(teams) != 2:
            continue
            
        line = row.find('a', href=lambda x: x and 'trank.php' in x)
        if not line:
            continue
        
        # Extract game time from the span with class="gametime"
        time_span = row.find('span', class_='gametime')
        if time_span:
            local_time = time_span.text.strip()  # e.g., "06:00 PM"
            
            # Convert to 24-hour format and add 5 hours for UTC
            dt = datetime.strptime(f"2025-01-22 {local_time}", "%Y-%m-%d %I:%M %p")
            utc_time = dt + timedelta(hours=5)
            game_time = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            game_time = None
            
        games.append({
            'Game Time': game_time,
            'Away Team': teams[0].text.strip(),
            'Home Team': teams[1].text.strip(),
            'T-Rank Line': line.text.strip()
        })
    
    return pd.DataFrame(games)
def clean_barttorvik(df):
    """
    Cleans the DataFrame by processing T-Rank Line information and extracting betting data
    """
    # Create a copy of the DataFrame
    df_final = df.copy()

    # Define regex pattern for parsing T-Rank Line
    pattern = r"^\s*(?P<TeamName>.+?)(?:\s+(?P<Spread>-\d+\.?\d*))?(?:,\s*(?P<ProjectedScore>\d+-\d+))?\s*\((?P<WinProb>\d+)%\)\s*$"

    # Apply regex to extract components
    extracted = df_final['T-Rank Line'].str.extract(pattern)

    # Initialize new columns
    df_final['Home Team Spread'] = np.nan
    df_final['Away Team Spread'] = np.nan
    df_final['Home Team Win Probability'] = np.nan
    df_final['Away Team Win Probability'] = np.nan
    df_final['Projected Total'] = np.nan

    # Process each row to assign spreads, win probabilities, and projected total
    for idx in df_final.index:
        team_name = extracted.at[idx, 'TeamName']
        spread = extracted.at[idx, 'Spread']
        projected_score = extracted.at[idx, 'ProjectedScore']
        win_prob = extracted.at[idx, 'WinProb']
        
        if pd.isna(team_name):
            continue

        # Determine if TeamName matches Home or Away team
        if team_name.strip() == df_final.at[idx, 'Home Team']:
            # Process Home Team data
            if pd.notna(spread):
                df_final.at[idx, 'Home Team Spread'] = float(spread)
                df_final.at[idx, 'Away Team Spread'] = -float(spread)
                
            if pd.notna(win_prob):
                home_win_prob = float(win_prob)
                df_final.at[idx, 'Home Team Win Probability'] = home_win_prob
                df_final.at[idx, 'Away Team Win Probability'] = 100 - home_win_prob
                
        elif team_name.strip() == df_final.at[idx, 'Away Team']:
            # Process Away Team data
            if pd.notna(spread):
                df_final.at[idx, 'Away Team Spread'] = float(spread)
                df_final.at[idx, 'Home Team Spread'] = -float(spread)
                
            if pd.notna(win_prob):
                away_win_prob = float(win_prob)
                df_final.at[idx, 'Away Team Win Probability'] = away_win_prob
                df_final.at[idx, 'Home Team Win Probability'] = 100 - away_win_prob

        # Process Projected Total regardless of team match
        if pd.notna(projected_score):
            scores = projected_score.split('-')
            if len(scores) == 2:
                try:
                    total = int(scores[0]) + int(scores[1])
                    df_final.at[idx, 'Projected Total'] = total
                except ValueError:
                    continue

    # Reorder columns
    columns = [
        'Game Time',
        'Home Team', 'Away Team',
        'Home Team Spread', 'Away Team Spread',
        'Home Team Win Probability', 'Away Team Win Probability',
        'Projected Total'
    ]
    
    df_final = df_final[columns]
    
    return df_final
