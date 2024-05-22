import requests
import datetime
import re
import airportsdata


def get_user_input():
    start_date_str = input("Enter the start date of your trip (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date_str = input("Enter the end date of your trip (YYYY-MM-DD): ")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    budget = float(input("Enter your total budget in USD for the trip: "))
    trip_type = input("Enter the type of trip (ski/beach/city): ").lower()
    return start_date, end_date, budget, trip_type


def get_trip_suggestions(trip_month, trip_type, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    messages = [
        {"role": "system", "content": "You are a travel guide."},
        {"role": "user",
         #Change to 5, 2 is just for test
         "content": f"List exactly 2 cities or regions ideal for a {trip_type} trip in July, focusing on the names of the cities or regions and countries only."}
    ]
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'max_tokens': 250
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        api_content = response.json()['choices'][0]['message']['content']
        suggestions = api_content.strip().split('\n')
        refined_suggestions = []
        for suggestion in suggestions:
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
    city_name = city_name.split('-')[0].strip()
    city_name = re.sub(r"\s*\([^)]*\)", "", city_name).strip()
    airports = airportsdata.load('IATA')
    for code, details in airports.items():
        if details['city'].lower() == city_name.lower():
            return code
    return None


def find_flights(serpapi_key, departure_date, return_date, destination):
    city_name, _ = destination.split(',', 1)
    print(f"Fetching airport code for {city_name}")
    airport_code = get_airport_code(city_name)

    if not airport_code:
        print(f"No valid airport code found for {city_name}, checked as: '{city_name}'")
        print("Unable to find a direct flight to this city. Consider alternative destinations or check nearby major airports.")
        return

    print(f"Found airport code: {airport_code} for {city_name}")
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "api_key": serpapi_key,
        "departure_id": "TLV",
        "arrival_id": airport_code,
        "outbound_date": departure_date,
        "type": 2
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'best_flights' in data and data['best_flights']:
            cheapest_flight = None
            lowest_price = float('inf')

            for flight in data['best_flights']:
                if flight['price'] < lowest_price:
                    cheapest_flight = flight
                    lowest_price = flight['price']

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


def find_cheapest_return_flight(serpapi_key, return_date, destination):
    city_name, _ = destination.split(',', 1)
    print(f"Fetching airport code for return flight from {city_name}")
    airport_code = get_airport_code(city_name)

    if not airport_code:
        print(f"No valid airport code found for {city_name}")
        return

    print(f"Found airport code: {airport_code} for {city_name}")
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "api_key": serpapi_key,
        "departure_id": airport_code,
        "arrival_id": "TLV",
        "outbound_date": return_date,
        "type": "2"  # For return flights
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        flights = data.get('best_flights', [])
        if flights:
            direct_flights = [flight for flight in flights if len(flight['flights']) == 1]
            if direct_flights:
                cheapest_direct_flight = sorted(direct_flights, key=lambda x: x['price'])[0]
            else:
                cheapest_direct_flight = sorted(flights, key=lambda x: x['price'])[0]  # fallback to connecting flights

            flight_details = cheapest_direct_flight['flights']
            total_price = cheapest_direct_flight['price']

            for leg in flight_details:
                departure = leg['departure_airport']['name']
                departure_time = leg['departure_airport']['time']
                arrival = leg['arrival_airport']['name']
                arrival_time = leg['arrival_airport']['time']
                print(f"Flight found: Departure {departure} at {departure_time} to {arrival} at {arrival_time} for ${total_price}")
        else:
            print("No return flight data available for", destination)
    else:
        print(f"Failed to fetch return flights: {response.status_code}, {response.text}")


def find_most_expensive_hotel_within_budget(location, budget, check_in_date, check_out_date, serpapi_key):
    num_nights = (check_out_date - check_in_date).days
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {location}",
        "check_in_date": check_in_date.strftime('%Y-%m-%d'),
        "check_out_date": check_out_date.strftime('%Y-%m-%d'),
        "adults": "1",
        "currency": "USD",
        "api_key": serpapi_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()

        if "properties" in results:
            properties = results["properties"]
            most_expensive_hotel = None
            highest_total_price = -1

            for property in properties:
                price_info = property.get('rate_per_night', {}).get('extracted_lowest', '0')
                nightly_price = float(price_info)

                total_price = nightly_price * num_nights

                if total_price > highest_total_price and total_price <= budget:
                    highest_total_price = total_price
                    most_expensive_hotel = (
                        f"Hotel Name: {property.get('name', 'Name not provided')}\n"
                        # f"Hotel Address: {property.get('address', 'Address not provided')}\n"
                        f"Price Per Night: ${nightly_price:.2f}\n"
                        f"Total Price: ${total_price:.2f}"
                    )

            return most_expensive_hotel if most_expensive_hotel else "No hotels found within budget."
        else:
            return "No properties found in the response."
    else:
        return f"Failed to fetch hotels: {response.status_code}, {response.text}"

def main():
    start_date, end_date, budget, trip_type = get_user_input()
    trip_month = start_date.month
    openai_api_key = 'sk-proj-xKbefkCYXVMRITYejkNmT3BlbkFJ00z2ZA8hwmnCqIBxL76q'
    serpapi_key = 'be2a08a90dda2768092654e8bdb0673c8a203c18e075f24db1f416ed8d157b27'

    if not openai_api_key or not serpapi_key:
        print("API keys are not set.")
        return

    suggestions = get_trip_suggestions(trip_month, trip_type, openai_api_key)
    if not suggestions or suggestions[0].startswith("No suggestions"):
        print("Failed to retrieve trip suggestions. Please try again later.")
        return

    print(f"\nSuggested destinations for a {trip_type} trip in month {trip_month}:")
    for place in suggestions:
        print("\n" + "-" * 40 + "\n")
        print(place)
        if ',' in place:
            remaining_budget = budget

            outbound_flight_cost = find_flights(serpapi_key, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), place)
            if outbound_flight_cost is not None:
                remaining_budget -= outbound_flight_cost

            return_flight_cost = find_cheapest_return_flight(serpapi_key, end_date.strftime('%Y-%m-%d'), place)
            if return_flight_cost is not None:
                remaining_budget -= return_flight_cost

            if remaining_budget > 0:
                hotel_info = find_most_expensive_hotel_within_budget(place, remaining_budget, start_date, end_date, serpapi_key)
                print(f"{hotel_info}")
            else:
                print(f"Remaining budget (${remaining_budget:.2f}) is not sufficient for accommodation.")
        else:
            print(f"Skipping {place} due to format issues.")

if __name__ == "__main__":
    main()