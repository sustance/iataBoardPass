import pandas as pd
from collections import Counter

# Sample data loading (replace with your actual data source)
data = """
241224|K|AKL|HKG|CX|0198|359
241224|S|AKL|HKG|CX|0198|359
241222|K|ZQN|AKL|NZ|0628|357
... [paste all your flight data here] ...
250102|S|HKG|PVG|CX|0380|002
"""

# Parse data into DataFrame
flights = pd.DataFrame([x.split('|') for x in data.strip().split('\n')],
                      columns=['date', 'pax', 'dep', 'arr', 'airline', 'flight', 'day_num'])

# 1. Airlines analysis
airline_counts = Counter(flights['airline'])
print("Top Airlines:")
print(airline_counts.most_common())

# 2. Airport analysis
airport_counts = Counter(flights['dep']) + Counter(flights['arr'])
print("\nBusiest Airports:")
print(airport_counts.most_common(5))

# 3. Travel patterns
flights['date'] = pd.to_datetime(flights['date'], format='%y%m%d')
flights['month'] = flights['date'].dt.month

print("\nMonthly Travel Frequency:")
print(flights['month'].value_counts().sort_index())

# Trip duration analysis (requires trip segmentation)
def analyze_trips(df):
    trips = []
    current_trip = []
    
    for _, row in df.sort_values('date').iterrows():
        if not current_trip or row['dep'] in ('HKG', 'SZX'):
            if current_trip:
                trips.append(current_trip)
            current_trip = [row]
        else:
            current_trip.append(row)
    
    if current_trip:
        trips.append(current_trip)
    
    trip_stats = []
    for trip in trips:
        if len(trip) > 1 and trip[-1]['arr'] in ('HKG', 'SZX'):
            duration = (pd.to_datetime(trip[-1]['date'], format='%y%m%d') - 
                       pd.to_datetime(trip[0]['date'], format='%y%m%d')).days
            airports = [trip[0]['dep']] + [x['arr'] for x in trip]
            trip_stats.append({
                'start': trip[0]['date'],
                'duration': duration,
                'route': '→'.join(airports),
                'stops': len(set(airports))-2
            })
    
    return pd.DataFrame(trip_stats)

trip_analysis = analyze_trips(flights)
print("\nTrip Duration Analysis:")
print(trip_analysis.describe())

# Visualization (requires matplotlib)
import matplotlib.pyplot as plt

plt.figure(figsize=(12,4))
flights['airline'].value_counts().plot(kind='bar', title='Airlines Used')
plt.show()
