import requests
import datetime
import re
import os
import airportsdata


def get_user_input():
    # Get the start date
    start_date_str = input("Enter the start date of your trip (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")

    # Get the end date
    end_date_str = input("Enter the end date of your trip (YYYY-MM-DD): ")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

    # Get the total budget
    budget = float(input("Enter your total budget in USD for the trip: "))

    # Get the type of trip
    trip_type = input("Enter the type of trip (ski/beach/city): ").lower()

    return start_date, end_date, budget, trip_type

def get_trip_suggestions(trip_month, trip_type, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Modified the prompt to explicitly ask for cities and countries
    messages = [
        {"role": "system", "content": "You are a travel guide."},
        {"role": "user",
         "content": f"List exactly 5 cities or regions ideal for a {trip_type} trip in July, focusing on the names of the cities or regions and countries only."}
    ]

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'max_tokens': 250  # Adjusted token limit
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        api_content = response.json()['choices'][0]['message']['content']
        suggestions = api_content.strip().split('\n')  # Adjusted to split by single newline
        refined_suggestions = []
        for suggestion in suggestions:
            # Regex to extract city/region and country
            match = re.search(r"^\d+\.\s*([^,]+),\s*([^,]+)$", suggestion)
            if match:
                city_region = match.group(1).strip()
                country = match.group(2).strip()
                refined_suggestions.append(f"{city_region}, {country}")
        return refined_suggestions
    else:
        print("Failed to fetch data from OpenAI API:", response.text)
        return ["No suggestions available due to API error"]


def get_airport_code(city_name):
    # Normalize the input to improve matching accuracy
    city_name = city_name.split('-')[0].strip()  # Strip extra descriptors
    city_name = re.sub(r"\s*\([^)]*\)", "", city_name).strip()  # Remove any parenthetical remarks

    airports = airportsdata.load('IATA')
    for code, details in airports.items():
        if details['city'].lower() == city_name.lower():
            return code
    return None


def find_flights(serpapi_key, departure_date, return_date, destination):
    # Splitting destination to extract the city name
    city_name, _ = destination.split(',', 1)  # Correctly split and ignore the country part
    print(f"Fetching airport code for {city_name}")

    airport_code = get_airport_code(city_name)

    if not airport_code:
        print(f"No valid airport code found for {city_name}, checked as: '{city_name}'")
        print("Unable to find a direct flight to this city. Consider alternative destinations or check nearby major airports.")
        return  # Skip this destination if no airport code found

    print(f"Found airport code: {airport_code} for {city_name}")
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "api_key": serpapi_key,
        "departure_id": "TLV",
        "arrival_id": airport_code,
        "outbound_date": departure_date,
        "type": 2  # Assuming type 2 is round trip (check API documentation)
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'best_flights' in data and data['best_flights']:
            # Initialize variables to find the cheapest flight
            cheapest_flight = None
            lowest_price = float('inf')

            # Iterate through all flights to find the cheapest one
            for flight in data['best_flights']:
                if flight['price'] < lowest_price:
                    cheapest_flight = flight
                    lowest_price = flight['price']

            # Output the cheapest flight details
            if cheapest_flight:
                departure_name = cheapest_flight['flights'][0]['departure_airport']['name']
                departure_time = cheapest_flight['flights'][0]['departure_airport']['time']
                arrival_name = cheapest_flight['flights'][0]['arrival_airport']['name']
                arrival_time = cheapest_flight['flights'][0]['arrival_airport']['time']
                price = cheapest_flight['price']
                print(f"Cheapest Flight: {departure_name} at {departure_time} to {arrival_name} at {arrival_time}")
                print(f"Price: ${price}\n")
            else:
                print("No flight data available for", destination)
        else:
            print("No flight data available for", destination)
    else:
        print(f"Failed to fetch flights: {response.status_code}, {response.text}")



def main():
    start_date, end_date, budget, trip_type = get_user_input()
    trip_month = start_date.month
    openai_api_key = 'sk-proj-xKbefkCYXVMRITYejkNmT3BlbkFJ00z2ZA8hwmnCqIBxL76q'  # OpenAI API key
    serpapi_key = 'c65b12dd2015470dfa0b15d95df58a8dfd892659553ce90568e80d9645b06e34' # SerpAPI key

    if not openai_api_key or not serpapi_key:
        print("API keys are not set in environment variables.")
        return

    suggestions = get_trip_suggestions(trip_month, trip_type, openai_api_key)
    print(f"\nSuggested destinations for a {trip_type} trip in month {trip_month}:")
    first = True
    for place in suggestions:
        if not first:
            print("\n" + "-" * 40 + "\n")  # This adds a divider line between destinations
        else:
            first = False
        print(place)
        find_flights(serpapi_key, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), place)


if __name__ == "__main__":
    main()

