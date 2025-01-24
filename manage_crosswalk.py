import json
import pandas as pd

def convert_crosswalk_to_json(crosswalk_df):
    """Convert crosswalk DataFrame to primary JSON structure"""
    team_names = {}
    
    for _, row in crosswalk_df.iterrows():
        canonical = row['API']
        # Get all variations excluding null values
        variations = [val for val in row.values if pd.notna(val)]
        team_names[canonical] = {
            "variations": sorted(list(set(variations)))  # Remove duplicates
        }
    
    return team_names

def create_lookup_dict(team_names):
    """Create O(1) lookup dictionary where every variation maps to canonical name"""
    lookup = {}
    for canonical, data in team_names.items():
        for variation in data['variations']:
            lookup[variation.lower()] = canonical
    return lookup

# Read crosswalk and convert
crosswalk_df = pd.read_csv('crosswalk.csv')
team_names = convert_crosswalk_to_json(crosswalk_df)

# Create the O(1) lookup dictionary
lookup_dict = create_lookup_dict(team_names)

# Save both structures
with open('team_names.json', 'w') as f:
    json.dump(team_names, f, indent=2, sort_keys=True)
    
with open('team_lookup.json', 'w') as f:
    json.dump(lookup_dict, f, indent=2, sort_keys=True)