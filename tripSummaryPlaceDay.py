import pandas as pd
from datetime import datetime

def parse_date(yymmdd):
    year = 2000 + int(yymmdd[:2])
    month = int(yymmdd[2:4])
    day = int(yymmdd[4:6])
    return datetime(year, month, day).strftime('%Y-%m-%d')

def extract_trips(data):
    df = pd.DataFrame([x.split('|') for x in data.strip().split('\n')], 
                     columns=['date', 'pax', 'dep', 'arr', 'airline', 'flight', 'day_num'])
    df['greg_date'] = df['date'].apply(parse_date)
    df = df.sort_values('date')
    
    trips = []
    current_trip = None
    in_trip = False
    
    for i, row in df.iterrows():
        if not in_trip and row['dep'] in ('HKG', 'SZX'):
            # Start new trip
            current_trip = {
                'start_date': row['greg_date'],
                'itinerary': [row['dep'], row['arr']],
                'dates': [row['greg_date']],
                'day_nums': [int(row['day_num'])]
            }
            in_trip = True
        elif in_trip:
            current_trip['itinerary'].append(row['arr'])
            current_trip['dates'].append(row['greg_date'])
            current_trip['day_nums'].append(int(row['day_num']))
            
            if row['arr'] in ('HKG', 'SZX'):
                # End trip
                trip_duration = (datetime.strptime(row['greg_date'], '%Y-%m-%d') - 
                                datetime.strptime(current_trip['start_date'], '%Y-%m-%d')).days
                
                # Calculate days at each location
                locations = {}
                for j in range(1, len(current_trip['itinerary'])):
                    loc = current_trip['itinerary'][j]
                    if loc not in ('HKG', 'SZX'):
                        stay = current_trip['day_nums'][j] - current_trip['day_nums'][j-1]
                        locations[loc] = locations.get(loc, 0) + stay
                
                trips.append({
                    'Start Date': current_trip['start_date'],
                    'End Date': row['greg_date'],
                    'Itinerary': '→'.join(current_trip['itinerary']),
                    'Duration': f"{trip_duration} days",
                    'Days at Locations': ', '.join(f"{k}:{v}" for k,v in locations.items())
                })
                
                in_trip = False
                current_trip = None
    
    return pd.DataFrame(trips)

# Example usage with your data:
data = """
241224|K|AKL|HKG|CX|0198|359
241224|S|AKL|HKG|CX|0198|359
...
250102|S|HKG|PVG|CX|0380|002
"""

trips_df = extract_trips(data)
print(trips_df.to_markdown(index=False))
