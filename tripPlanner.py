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
    # print(f"Fetching airport code for {city_name}")
    airport_code = get_airport_code(city_name)

    if not airport_code:
        # print(f"No valid airport code found for {city_name}, checked as: '{city_name}'")
        # print("Unable to find a direct flight to this city. Consider alternative destinations or check nearby major airports.")
        return None

    # print(f"Found airport code: {airport_code} for {city_name}")
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
            cheapest_flight = min(data['best_flights'], key=lambda f: f['price'])
            price = cheapest_flight['price']
            print(f"Cheapest Flight: {cheapest_flight['flights'][0]['departure_airport']['name']} at {cheapest_flight['flights'][0]['departure_airport']['time']} to {cheapest_flight['flights'][0]['arrival_airport']['name']} at {cheapest_flight['flights'][0]['arrival_airport']['time']}")
            print(f"Price: ${price}\n")
            return price
        else:
            # print("No flight data available for", destination)
            return None
    else:
        # print(f"Failed to fetch flights: {response.status_code}, {response.text}")
        return None


def find_cheapest_return_flight(serpapi_key, return_date, destination):
    city_name, _ = destination.split(',', 1)
    # print(f"Fetching airport code for return flight from {city_name}")
    airport_code = get_airport_code(city_name)

    if not airport_code:
        # print(f"No valid airport code found for {city_name}")
        return None

    # print(f"Found airport code: {airport_code} for {city_name}")
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
            cheapest_direct_flight = min(flights, key=lambda x: x['price'])
            total_price = cheapest_direct_flight['price']
            print(f"Flight found: Departure {cheapest_direct_flight['flights'][0]['departure_airport']['name']} at {cheapest_direct_flight['flights'][0]['departure_airport']['time']} to {cheapest_direct_flight['flights'][0]['arrival_airport']['name']} at {cheapest_direct_flight['flights'][0]['arrival_airport']['time']} for ${total_price}")
            return total_price
        else:
            # print("No return flight data available for", destination)
            return None
    else:
        # print(f"Failed to fetch return flights: {response.status_code}, {response.text}")
        return None



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

                if total_price > highest_total_price:
                    highest_total_price = total_price
                    most_expensive_hotel = (
                        f"Hotel Name: {property.get('name', 'Name not provided')}\n"
                        f"Price Per Night: ${nightly_price:.2f}\n"
                        f"Total Price for {num_nights} nights: ${total_price:.2f}"
                    )

            return most_expensive_hotel if most_expensive_hotel else "No hotels found."
        else:
            return "No properties found in the response."
    else:
        return f"Failed to fetch hotels: {response.status_code}, {response.text}"


def get_daily_itinerary(api_key, location, start_date, end_date, trip_type):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # Constructing the prompt for the travel guide
    user_prompt = f"Create a detailed daily itinerary for a {trip_type} trip to {location} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. Include activities, meal suggestions, and local travel tips."

    # Ensuring the messages are correctly formed
    messages = [
        {"role": "system", "content": "You are a travel guide."},
        {"role": "user", "content": user_prompt}
    ]

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'max_tokens': 1500,
        'temperature': 0.7
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        # Extracting the content of the latest message from the chat
        chat_response = response.json()
        latest_message = chat_response['choices'][0]['message']['content']
        return latest_message.strip()
    else:
        error_message = f"Failed to fetch itinerary: {response.status_code} {response.text}"
        print(error_message)
        return error_message



def main():
    start_date, end_date, budget, trip_type = get_user_input()
    trip_month = start_date.month
    openai_api_key = 'sk-proj-xKbefkCYXVMRITYejkNmT3BlbkFJ00z2ZA8hwmnCqIBxL76q'
    serpapi_key = 'a90447a1febd5d186512a7ba703b9cb1c5b09db7c486ff38c1596501b05f771d'

    if not openai_api_key or not serpapi_key:
        # print("API keys are not set.")
        return

    suggestions = get_trip_suggestions(trip_month, trip_type, openai_api_key)
    if not suggestions or suggestions[0].startswith("No suggestions"):
        # print("Failed to retrieve trip suggestions. Please try again later.")
        return

    trip_options = []

    # print(f"\nSuggested destinations for a {trip_type} trip in month {trip_month}:")
    for place in suggestions:
        # print("\n" + "-" * 40 + "\n")
        # print(place)
        if ',' in place:
            # print("Fetching flight and hotel information...")
            remaining_budget = budget
            total_trip_cost = 0

            outbound_flight_cost = find_flights(serpapi_key, start_date.strftime('%Y-%m-%d'),
                                                end_date.strftime('%Y-%m-%d'), place)
            return_flight_cost = find_cheapest_return_flight(serpapi_key, end_date.strftime('%Y-%m-%d'), place)

            if outbound_flight_cost is None or return_flight_cost is None:
                # print(f"Skipping {place} as complete flight data is not available.")
                continue

            remaining_budget -= (outbound_flight_cost + return_flight_cost)
            total_trip_cost += (outbound_flight_cost + return_flight_cost)

            hotel_info = find_most_expensive_hotel_within_budget(place, remaining_budget, start_date, end_date,
                                                                 serpapi_key)
            if "Total Price" in hotel_info:
                hotel_total_price = float(hotel_info.split('$')[-1])
                remaining_budget -= hotel_total_price
                total_trip_cost += hotel_total_price
                trip_options.append((place, total_trip_cost, hotel_info))

    print("\nAll available trip options with total costs:\n")
    for idx, option in enumerate(trip_options, 1):
        print(f"Option {idx}:")
        print(f"Destination: {option[0]}")
        print(f"Total Trip Cost: ${option[1]:.2f}")
        print(option[2])
        print("-" * 40)

    if trip_options:
        choice = input("Please enter the option number you would like to choose (e.g., 1, 2, ...): ")
        try:
            selected_option = trip_options[int(choice) - 1]
            print(f"\nYou have selected:\nDestination: {selected_option[0]}")
            print(f"Total Trip Cost: ${selected_option[1]:.2f}")
            print(selected_option[2])

            # Fetch daily itinerary from OpenAI
            itinerary = get_daily_itinerary(openai_api_key, selected_option[0].split(",")[0], start_date, end_date,
                                            trip_type)
            print("\nSuggested Daily Itinerary:")
            print(itinerary)
        except (IndexError, ValueError):
            print("Invalid option selected. Please run the program again and select a valid option.")
    else:
        print("No valid trip options are available.")

if __name__ == "__main__":
    main()