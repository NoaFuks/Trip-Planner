
# Trip Planner

This is a full-stack **Trip Planner** application built using **Next.js** for the frontend and **FastAPI** for the backend. The app helps users plan their trips by providing trip suggestions, flight and hotel options, and detailed itineraries for their selected trips.

## Features

- **Frontend (Next.js)**: 
  - Plan a trip by entering the start date, end date, budget, and trip type.
  - View trip suggestions with detailed flight and hotel information.
  - Select a trip to view a detailed itinerary and associated images.

- **Backend (FastAPI)**: 
  - Integrates with external APIs such as OpenAI and SerpAPI to fetch trip suggestions, flights, hotels, and generate itineraries.
  - Handles user requests for planning and selecting trips.

## Technologies Used

- **Frontend**: Next.js, React, Axios
- **Backend**: FastAPI, Pydantic, Requests
- **APIs**: OpenAI, SerpAPI, Google Flights API, Google Hotels API

## Folder Structure

```
├── trip-planner
│   ├── components
│   │   ├── SelectedTrip.js       # Displays selected trip details
│   │   ├── TripForm.js           # Handles trip form and trip planning
│   │   └── TripOptions.js        # Displays trip options after form submission
│   ├── pages
│   │   ├── api
│   │   │   ├── hello.js          # Sample API route
│   │   │   ├── plan-trip.js      # Handles trip planning (calls FastAPI backend)
│   │   │   └── select-trip.js    # Handles trip selection (calls FastAPI backend)
│   ├── _app.js                   # App-wide configuration
│   └── index.js                  # Main entry point for the frontend
└── tripPlanner.py                # FastAPI backend
```

## Backend Setup (FastAPI)

### Prerequisites

- **Python 3.8+**
- Install FastAPI and Uvicorn using pip:
  ```bash
  pip install fastapi uvicorn pydantic requests airportsdata
  ```

- You will also need API keys for:
  - **OpenAI API**: For generating trip suggestions and itineraries.
  - **SerpAPI**: For fetching flights and hotels information from Google Flights and Google Hotels.

### Backend Setup

1. **Clone the repository** and navigate to the backend folder:
   ```bash
   git clone https://github.com/your-username/trip-planner.git
   cd trip-planner
   ```

2. **Set up environment variables** for API keys:
   You can either export the API keys in your environment or directly modify the `tripPlanner.py` file to include your API keys.

   Example of setting API keys:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export SERPAPI_KEY="your-serpapi-key"
   ```

3. **Run the FastAPI server**:
   ```bash
   uvicorn tripPlanner:app --reload
   ```

   The server will be available at `http://127.0.0.1:8000`.

4. **Test the backend** using tools like Postman or curl:
   - **Trip Planning API**:
     ```bash
     POST http://127.0.0.1:8000/plan-trip
     {
       "start_date": "2024-12-01",
       "end_date": "2024-12-10",
       "budget": 1500,
       "trip_type": "beach"
     }
     ```

   - **Trip Selection API**:
     ```bash
     POST http://127.0.0.1:8000/select-trip
     {
       "start_date": "2024-12-01",
       "end_date": "2024-12-10",
       "trip_type": "beach",
       "destination": "Barcelona, Spain"
     }
     ```

## Frontend Setup (Next.js)

### Prerequisites

- **Node.js** (version 12 or higher)
- **npm** or **yarn** installed on your machine.

### Installation

1. Navigate to the `trip-planner` directory:
   ```bash
   cd trip-planner
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app should now be running at `http://localhost:3000`.

## API Routes (Frontend)

### `/api/plan-trip`

- **Method**: `POST`
- **Description**: Sends the user's trip details (start date, end date, budget, trip type) to the FastAPI backend to get trip options.
- **Request Body**:
  ```json
  {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "budget": "number",
    "trip_type": "string"
  }
  ```
- **Response**: A list of trip options with flight and hotel details.

### `/api/select-trip`

- **Method**: `POST`
- **Description**: Sends the selected trip option to the FastAPI backend to fetch itinerary and images.
- **Request Body**:
  ```json
  {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "trip_type": "string",
    "destination": "string"
  }
  ```
- **Response**: Detailed itinerary and images for the selected trip.

## Future Improvements

- Add user authentication to save trips and user preferences.
- Improve error handling for API requests.
- Deploy the app using a cloud service such as Vercel or Heroku.



