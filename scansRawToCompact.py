#!/usr/bin/env python3
import sys
#import os
from datetime import datetime
#variable_value = os.environ['VARIABLE_NAME']
#YEAR = os.environ['YEAR']
YEAR = "2023" 

try:
    print(f"Debug: julian_day received = {julian_day}")
    julian_int = int(julian_day)
    print(f"Debug: julian_int converted = {julian_int}")
    if not (1 <= julian_int <= 366):
        print("Debug: julian_int out of range (1-366)")
        return "Err"
    date = datetime.strptime(f"{YEAR}-{julian_int:03d}", "%Y-%j").date()
    print(f"Debug: date parsed = {date}")
    return date.strftime("%y%m%d")
except Exception as e:
    #print(f"Error converting julian day '{julian_day}': {e}", file=sys.stderr)
    return "Err"

#def julian_to_date(julian_day):
#    """Convert Julian day (DDD) to YYMMDD format"""
#    try:
#        julian_int = int(julian_day)
#        if not (1 <= julian_int <= 366):
#            return "Err"
#        date = date.strptime(f"{YEAR}-{julian_int:03d}", "%Y-%j").date()
#        return date.strftime("%y%m%d")
#    except Exception as e:
        # Uncomment below to debug
        # print(f"Error converting julian day '{julian_day}': {e}", file=sys.stderr)
#        return "Err"

def process_line(line):
    """Process one line of input data"""
    parts = line.split()
    if not parts:
        return "Err  |  Err  |  Err  |  Err  |  Err  |  Err  |  Err"

    # Initialize all fields
    c3 = c5 = c6 = c7 = c8 = c9 = "Err"

    # Extract C3 (name part after /)
    if "/" in parts[0]:
        split0 = parts[0].split("/")
        if len(split0) > 1:
            c3 = split0[1][:1].replace("C", "S")

    # Find 8-char airport code (take first one found)
    for part in parts:
        if len(part) == 8:
            c5 = part[:3]
            c6 = part[3:6]
            c7 = part[6:]
            break

    # Find C8 (first 4-digit number)
    for i, part in enumerate(parts):
        if part.isdigit() and len(part) == 4:
            c8 = part
            # C9 is next part (take first 3 digits if possible)
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Extract first 3 digits from next_part if available
                digits = ''.join(filter(str.isdigit, next_part))
                c9 = digits[:3] if len(digits) >= 3 else "Err"
            break

    # Convert Julian date
    ca = julian_to_date(c9) if c9.isdigit() else "Err"

    return f"{ca}  |  {c3}  |  {c5}  |  {c6}  |  {c7}  |  {c8}  |  {c9}"

def main():
    """Main processing function"""
    for line in sys.stdin:
        line = line.strip()
        if line:  # Only process non-empty lines
            result = process_line(line)
            print(result)

if __name__ == "__main__":
    main()
