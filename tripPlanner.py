import requests
import datetime
import re  # Import the regular expression library

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


def get_trip_suggestions(trip_month, trip_type):
    api_key = 'sk-proj-xKbefkCYXVMRITYejkNmT3BlbkFJ00z2ZA8hwmnCqIBxL76q'  # Replace with your actual API key
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    messages = [
        {"role": "system", "content": "You are a travel guide."},
        {"role": "user",
         "content": f"List exactly 5 places ideal for a {trip_type} trip in July, focusing on the names of the places and countries only."}
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
            # Update regex to capture place and country without additional formatting
            match = re.search(r"^\d+\.\s*(.+)$", suggestion)  # Simplified to capture the rest of the line
            if match:
                refined_suggestions.append(match.group(1).strip())
        return refined_suggestions
    else:
        print("Failed to fetch data from OpenAI API:", response.text)
        return ["No suggestions available due to API error"]


def main():
    start_date, end_date, budget, trip_type = get_user_input()

    # Extract the month from the start date
    trip_month = start_date.month

    # Get trip suggestions
    suggestions = get_trip_suggestions(trip_month, trip_type)

    # Display suggestions
    print(f"\nSuggested destinations for a {trip_type} trip in month {trip_month}:")
    for place in suggestions:
        print(place)


if __name__ == "__main__":
    main()