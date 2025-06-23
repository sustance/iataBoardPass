#!/usr/bin/env python3
import sys
import os
import csv
from datetime import datetime, timedelta
from pathlib import Path

def get_year():
    """Prompt user for year and validate input"""
    while True:
        try:
            year_input = input("Enter year (YYYY): ").strip()
            year = int(year_input)
            if 1900 <= year <= 2100:  # Reasonable year range
                return str(year)
            else:
                print("Please enter a valid year between 1900 and 2100")
        except ValueError:
            print("Please enter a valid 4-digit year")

def julian_to_date(julian_day, year):
    """Convert Julian day (DDD) to YYMMDD format"""
    try:
        #print(f"Debug: julian_day received = {julian_day}, year = {year}")
        julian_int = int(julian_day)
        #print(f"Debug: julian_int converted = {julian_int}")
        if not (1 <= julian_int <= 366):
            #print("Debug: julian_int out of range (1-366)")
            return "Err"
        date = datetime.strptime(f"{year}-{julian_int:03d}", "%Y-%j").date()
        #print(f"Debug: date parsed = {date}")
        return date.strftime("%y%m%d")
    except Exception as e:
        print(f"Error converting julian day '{julian_day}': {e}", file=sys.stderr)
        return "Err"

def parse_date(date_str):
    """Parse date string in YYMMDD format to datetime object"""
    try:
        # Handle both YYMMDD (6 chars) and YYYYMMDD (8 chars) formats
        if len(date_str) == 6:
            return datetime.strptime(date_str, "%y%m%d").date()
        elif len(date_str) == 8:
            return datetime.strptime(date_str, "%Y%m%d").date()
        else:
            return None
    except ValueError:
        return None

def load_points_data(points_file_path):
    """Load and parse the airline points CSV file"""
    points_data = []
    
    if not os.path.exists(points_file_path):
        print(f"Warning: Points file not found at {points_file_path}")
        return points_data
    
    try:
        with open(points_file_path, 'r', encoding='utf-8') as f:
            # Skip header line
            next(f)
            csv_reader = csv.reader(f)
            
            for row_num, row in enumerate(csv_reader, start=2):
                if len(row) >= 5:  # Ensure we have enough columns
                    # Clean and extract data
                    date_paid = row[0].strip()
                    person = row[1].strip()
                    airline = row[3].strip()
                    flight_num = row[4].strip()
                    
                    points_data.append({
                        'date_paid': date_paid,
                        'person': person,
                        'airline': airline,
                        'flight_num': flight_num
                    })
                    #print(f"Debug: Loaded points record - Date: {date_paid}, Person: {person}, Airline: {airline}, Flight: {flight_num}")
                else:
                    print(f"Warning: Skipping malformed row {row_num} in points file")
    
    except Exception as e:
        print(f"Error reading points file: {e}", file=sys.stderr)
    
    print(f"Debug: Loaded {len(points_data)} points records")
    return points_data

def check_points_match(flight_date, person, airline, flight_num, points_data):
    """
    Check if flight matches any entry in points data with 2-day tolerance
    Returns 'Y' if match found, '-' otherwise
    """
    # Parse the flight date
    flight_date_obj = parse_date(flight_date)
    if not flight_date_obj:
        #print(f"Debug: Could not parse flight date: {flight_date}")
        return "-"
    
    #print(f"Debug: Checking match for - Date: {flight_date}, Person: {person}, Airline: {airline}, Flight: {flight_num}")
    
    for points_record in points_data:
        # Check person match (case insensitive)
        if points_record['person'].upper() != person.upper():
            continue
            
        # Check airline match (case insensitive)  
        if points_record['airline'].upper() != airline.upper():
            continue
            
        # Check flight number match (remove leading zeros for comparison)
        points_flight = points_record['flight_num'].lstrip('0')
        flight_flight = flight_num.lstrip('0')
        if points_flight != flight_flight:
            continue
        
        # Check date match with 2-day tolerance
        points_date_obj = parse_date(points_record['date_paid'])
        if points_date_obj:
            date_diff = abs((flight_date_obj - points_date_obj).days)
            #print(f"Debug: Date comparison - Flight: {flight_date_obj}, Points: {points_date_obj}, Diff: {date_diff} days")
            if date_diff <= 2:
                #print(f"Debug: Match found! Flight matches points record")
                return "Y"
    
    #print(f"Debug: No match found for flight")
    return "-"

def process_line(line, points_data, year):
    """Process one line of input data"""
    parts = line.split()
    if not parts:
        return "Err, Err, Err, Err,Err, Err,Err,Err"

    # Initialize all fields
    c3 = c5 = c6 = c7 = c8 = c9 = "Err"

    # Extract C3 (name part after /, first character, replace C with S)
    if "/" in parts[0]:
        split0 = parts[0].split("/")
        if len(split0) > 1:
            c3 = split0[1][:1].replace("C", "S")

    # Find 8-char airport code (take first one found)
    for part in parts:
        if len(part) == 8:
            c5 = part[:3]  # From Airport
            c6 = part[3:6]  # To Airport  
            c7 = part[6:]   # Airline
            break

    # Find C8 (first 4-digit number - flight number)
    for i, part in enumerate(parts):
        if part.isdigit() and len(part) == 4:
            c8 = part
            # C9 is next part (take first 3 digits if possible - Julian date)
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Extract first 3 digits from next_part if available
                digits = ''.join(filter(str.isdigit, next_part))
                c9 = digits[:3] if len(digits) >= 3 else "Err"
            break

    # Convert Julian date to YYMMDD format
    ca = julian_to_date(c9, year) if c9.isdigit() else "Err"

    # Check for points match
    c10 = check_points_match(ca, c3, c7, c8, points_data)

    return f"{ca}, {c3}, {c5}, {c6}, {c7},{c8}, {c9},{c10}"

def main():
    """Main processing function"""
    # Get year from user input
    YEAR = get_year()
    print(f"Using year: {YEAR}")
    
    # Define file paths
    home_dir = os.path.expanduser("~")
    iata_file_path = os.path.join(home_dir, "tmp", "pdata", "IATA_BP_Scans_2025")
    points_file_path = os.path.join(home_dir, "tmp", "pdata", "Airline_Points_Paid.csv")
    
    # Load points data
    print(f"Loading points data from: {points_file_path}")
    points_data = load_points_data(points_file_path)
    
    # Check if IATA file exists
    if not os.path.exists(iata_file_path):
        print(f"Error: IATA file not found at {iata_file_path}")
        sys.exit(1)
    
    # Print header
    print("Date,Person, From Airport, To Airport, Airline, Flight num, Julian Date, Points Paid")
    
    # Process IATA file
    print(f"Processing IATA data from: {iata_file_path}")
    try:
        with open(iata_file_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                line = line.strip()
                if line:  # Only process non-empty lines
                    line_count += 1
                    #print(f"Debug: Processing line {line_count}: {line[:50]}...")
                    result = process_line(line, points_data, YEAR)
                    print(result)
            print(f"Debug: Processed {line_count} lines from IATA file")
                    
    except FileNotFoundError:
        print(f"Error: Could not find file {iata_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading IATA file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
