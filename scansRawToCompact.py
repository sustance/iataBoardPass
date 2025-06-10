#!/usr/bin/env python3
import sys
from datetime import datetime
# Must launch this script as '$YEAR scansRawToCompact.py'
THIS_YEAR = "$YEAR"
LEAP_YEARS = {2012, 2016, 2020, 2024, 2028, 2032}

def julian_to_yyyymmdd(julian_day):
    try:
        year = int(THIS_YEAR)
        date = datetime.strptime(f"{year} {julian_day}", "%Y %j").date()
        return date.strftime("%y%m%d")
    except:
        return "Err"

def process_line(line):
    if not line.strip():
        return None
        
    parts = line.split()
    
    # Handle lines starting with M1 or __
    if line.startswith("M1") or line.startswith("__"):
        # Extract C3 (KYM/CHUN)
        c3 = "Err"
        if "/" in parts[0]:
            c3 = parts[0].split("/")[1]
            if c3 == "CHUN":
                c3 = "C2N"
        
        # Find airport pairs (C5, C6)
        c5, c6, c7 = "Err", "Err", "Err"
        for part in parts:
            if len(part) == 6 and part.isalpha():  # Airport code pattern
                c5 = part[:3]
                c6 = part[3:]
                break
        
        # Find airline (C7) - look for 2-letter codes after airport pair
        for i, part in enumerate(parts):
            if part in ["CX", "NZ", "MU", "BR", "EK", "KL", "OS", "HX", "CA"]:
                c7 = part
                break
        
        # Find C8 and C9
        c8, c9 = "Err", "Err"
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4:  # C8 pattern
                c8 = part
                if i+1 < len(parts) and (parts[i+1].isdigit() or parts[i+1][:-1].isdigit()):  # C9 pattern
                    c9 = parts[i+1].rstrip('z').rstrip('Y')  # Clean suffixes
                break
        
        # Generate output
        if c9 != "Err":
            ca = julian_to_yyyymmdd(int(c9))
        else:
            ca = "Err"
        
        return f"{ca}  |  {c3}  |  {c5}  |  {c6}  |  {c7}  |  {c8}  |  {c9}"
    
    return None

def main():
    # Read from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = f.read().splitlines()
    else:
        data = sys.stdin.read().splitlines()
    
    # Process each line
    for line in data:
        if line.strip():  # Only process non-empty lines
            processed = process_line(line)
            if processed:
                print(processed)
            else:
                print("Err  |  Err  |  Err  |  Err  |  Err  |  Err  |  Err")

if __name__ == "__main__":
    main()
