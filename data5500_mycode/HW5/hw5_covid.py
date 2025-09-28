"""
HW5 - COVID Data Analysis
"""

import cloudscraper
import json
from datetime import datetime
from collections import defaultdict

# Fetch data for a single state

def fetch_state_data(state_code):
    scraper = cloudscraper.create_scraper()
    url = f"https://api.covidtracking.com/v1/states/{state_code}/daily.json"
    response = scraper.get(url)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch data for {state_code}")
        return []

    data = response.json()

    # Save JSON to file
    with open(f"{state_code}.json", "w") as f:
        json.dump(data, f, indent=4)

    return data



# Analyze a state's COVID data

def analyze_state_data(state_code, data):
    if not data:
        return

    # Extract positive increase values
    positive_increase = [day.get("positiveIncrease", 0) for day in data if day.get("positiveIncrease") is not None]

    if not positive_increase:
        print(f"No data available for {state_code}")
        return

    # Average daily new cases
    avg_new_cases = sum(positive_increase) / len(positive_increase)

    # Highest daily cases
    max_day = max(data, key=lambda x: x.get("positiveIncrease", 0))
    max_date = datetime.strptime(str(max_day["date"]), "%Y%m%d").strftime("%Y-%m-%d")

    # Most recent date with no new cases
    no_case_days = [day for day in data if day.get("positiveIncrease", -1) == 0]
    recent_no_case = None
    if no_case_days:
        recent_no_case = datetime.strptime(str(no_case_days[0]["date"]), "%Y%m%d").strftime("%Y-%m-%d")

    # Monthly aggregation
    monthly_cases = defaultdict(int)
    for day in data:
        date = datetime.strptime(str(day["date"]), "%Y%m%d")
        ym = (date.year, date.month)
        monthly_cases[ym] += day.get("positiveIncrease", 0)

    # Highest and lowest month
    highest_month = max(monthly_cases, key=monthly_cases.get)
    lowest_month = min(monthly_cases, key=monthly_cases.get)

    highest_month_str = f"{datetime(highest_month[0], highest_month[1], 1).strftime('%B %Y')}"
    lowest_month_str = f"{datetime(lowest_month[0], lowest_month[1], 1).strftime('%B %Y')}"

    # Print results

    print("\nCovid confirmed cases statistics")
    print(f"State code: {state_code.upper()}")
    print(f"Average number of new daily confirmed cases: {avg_new_cases:.2f}")
    print(f"Date with the highest new number of covid cases: {max_date}")
    print(f"Most recent date with no new covid cases: {recent_no_case}")
    print(f"Month and Year with the highest new number of covid cases: {highest_month_str}")
    print(f"Month and Year with the lowest new number of covid cases: {lowest_month_str}")

# Main driver
def main():
    # Read state codes
    with open("states_territories.txt") as f:
        state_codes = [line.strip().lower() for line in f if line.strip()]

    # Loop through states/territories
    for code in state_codes:
        data = fetch_state_data(code)
        analyze_state_data(code, data)


if __name__ == "__main__":
    main()
