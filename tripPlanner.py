from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import requests
import re
import airportsdata

app = FastAPI()

class TripRequest(BaseModel):
    start_date: str
    end_date: str
    budget: float
    trip_type: str

class TripSelection(BaseModel):
    start_date: str
    end_date: str
    trip_type: str
    destination: str

def generate_images(openai_api_key, prompts):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    # Assuming 'prompts' is a list of string prompts and each prompt will generate one image.
    images_urls = []
    for prompt in prompts:
        data = {
            "prompt": prompt,
            "n": 1,  # Number of images to generate per prompt
            "size": "1024x1024"  # Image size
        }
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json()['data'][0]['url']  # Assuming the first image's URL is what we need
            images_urls.append(image_url)
        else:
            images_urls.append("Error generating image: " + response.text)
    return images_urls



def get_trip_suggestions(trip_month, trip_type, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    messages = [
        {"role": "system", "content": "You are a travel guide."},
        {"role": "user",
        "content": f"List exactly 2 cities or regions ideal for a {trip_type} trip in {trip_month}, focusing on the names of the cities or regions and countries only."}
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
    airport_code = get_airport_code(city_name)

    if not airport_code:
        return None

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
            return {
                "price": cheapest_flight['price'],
                "departure_airport": cheapest_flight['flights'][0]['departure_airport']['name'],
                "departure_time": cheapest_flight['flights'][0]['departure_airport']['time'],
                "arrival_airport": cheapest_flight['flights'][0]['arrival_airport']['name'],
                "arrival_time": cheapest_flight['flights'][0]['arrival_airport']['time']
            }
        else:
            return None
    else:
        return None

def find_cheapest_return_flight(serpapi_key, return_date, destination):
    city_name, _ = destination.split(',', 1)
    airport_code = get_airport_code(city_name)

    if not airport_code:
        return None

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "api_key": serpapi_key,
        "departure_id": airport_code,
        "arrival_id": "TLV",
        "outbound_date": return_date,
        "type": "2"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        flights = data.get('best_flights', [])
        if flights:
            cheapest_direct_flight = min(flights, key=lambda x: x['price'])
            return {
                "price": cheapest_direct_flight['price'],
                "departure_airport": cheapest_direct_flight['flights'][0]['departure_airport']['name'],
                "departure_time": cheapest_direct_flight['flights'][0]['departure_airport']['time'],
                "arrival_airport": cheapest_direct_flight['flights'][0]['arrival_airport']['name'],
                "arrival_time": cheapest_direct_flight['flights'][0]['arrival_airport']['time']
            }
        else:
            return None
    else:
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
                        f"Name: {property.get('name', 'Name not provided')}\n"
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
    user_prompt = f"Create a detailed daily itinerary for a {trip_type} trip to {location} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. Include activities, meal suggestions, and local travel tips."

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
        chat_response = response.json()
        latest_message = chat_response['choices'][0]['message']['content']
        return latest_message.strip()
    else:
        error_message = f"Failed to fetch itinerary: {response.status_code} {response.text}"
        return error_message


def extract_image_prompts(itinerary):
    """
    Extracts key phrases from a trip itinerary to be used as image generation prompts.
    This function assumes that the itinerary is a detailed textual description of each day's activities.
    """
    prompts = []
    lines = itinerary.split('\n')

    for line in lines:
        if "visit" in line.lower() or "explore" in line.lower() or "enjoy" in line.lower():
            # Clean and simplify the line to create a more focused prompt
            line = re.sub(r'\s+', ' ', line)  # Remove excess whitespace
            line = re.sub(r'[^\w\s,]', '', line)  # Remove special characters
            # Extract the main activity
            activity_match = re.search(r"(visit|explore|enjoy)\s+([\w\s,]+)", line, re.IGNORECASE)
            if activity_match:
                activity = activity_match.group(2).strip()
                # Convert activity description into a visual prompt
                if "visit" in activity_match.group(1).lower():
                    prompts.append(f"Visiting {activity}, a scenic view of the main attractions.")
                elif "explore" in activity_match.group(1).lower():
                    prompts.append(f"Exploring {activity}, showcasing the bustling local life and unique architecture.")
                elif "enjoy" in activity_match.group(1).lower():
                    prompts.append(f"Enjoying a day at {activity}, with a focus on leisure and recreation activities.")
    return prompts


def plan_trip(start_date, end_date, budget, trip_type, openai_api_key, serpapi_key):
    trip_month = start_date.month
    suggestions = get_trip_suggestions(trip_month, trip_type, openai_api_key)
    if not suggestions or suggestions[0].startswith("No suggestions"):
        return "Failed to retrieve trip suggestions. Please try again later."

    trip_options = []
    for place in suggestions:
        if ',' in place:
            remaining_budget = budget
            total_trip_cost = 0

            # Find flights
            outbound_flight_info = find_flights(serpapi_key, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), place)
            return_flight_info = find_cheapest_return_flight(serpapi_key, end_date.strftime('%Y-%m-%d'), place)
            if outbound_flight_info is None or return_flight_info is None:
                continue

            remaining_budget -= (outbound_flight_info['price'] + return_flight_info['price'])
            total_trip_cost += (outbound_flight_info['price'] + return_flight_info['price'])

            # Find hotel
            hotel_info = find_most_expensive_hotel_within_budget(place, remaining_budget, start_date, end_date, serpapi_key)
            if "Total Price" in hotel_info:
                hotel_total_price = float(hotel_info.split('$')[-1])
                remaining_budget -= hotel_total_price
                total_trip_cost += hotel_total_price

                itinerary = get_daily_itinerary(openai_api_key, place, start_date, end_date, trip_type)
                image_prompts = extract_image_prompts(itinerary)  # Implement this function based on itinerary details
                images = generate_images(openai_api_key, image_prompts)

                trip_options.append({
                    "destination": place,
                    "total_cost": total_trip_cost,
                    "hotel_info": hotel_info,
                    "flight_info": {"outbound": outbound_flight_info, "return": return_flight_info},
                    "itinerary": itinerary,
                    "images": images
                })

    if trip_options:
        return {"trip_options": trip_options}
    else:
        return {"error": "No valid trip options are available."}

@app.post("/plan-trip")
async def plan_trip_endpoint(trip_request: TripRequest):
    start_date = datetime.datetime.strptime(trip_request.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(trip_request.end_date, "%Y-%m-%d")
    budget = trip_request.budget
    trip_type = trip_request.trip_type

    openai_api_key = 'sk-proj-7WG5ayqN95xQWSP7V6XMT3BlbkFJLMYtP0g6vnwzGQhKBMTF'
    serpapi_key = '56d732025933b92fbe6b89b9b413177ce1034d8e5f8cfbd460fb46c8fe4d34b3'

    result = plan_trip(start_date, end_date, budget, trip_type, openai_api_key, serpapi_key)
    return result


@app.post("/select-trip")
async def select_trip_endpoint(selection: TripSelection):
    start_date = datetime.datetime.strptime(selection.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(selection.end_date, "%Y-%m-%d")
    trip_type = selection.trip_type
    destination = selection.destination

    openai_api_key = 'sk-proj-7WG5ayqN95xQWSP7V6XMT3BlbkFJLMYtP0g6vnwzGQhKBMTF'

    itinerary = get_daily_itinerary(openai_api_key, destination.split(",")[0], start_date, end_date, trip_type)
    return {"destination": destination, "itinerary": itinerary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)