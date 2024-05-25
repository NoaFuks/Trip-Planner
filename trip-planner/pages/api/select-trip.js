import axios from 'axios';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { start_date, end_date, trip_type, destination } = req.body;

    try {
      // Call your FastAPI backend
      const response = await axios.post('http://127.0.0.1:8000/select-trip', {
        start_date,
        end_date,
        trip_type,
        destination,
      });

      res.status(200).json(response.data);
    } catch (error) {
      console.error('Error fetching itinerary:', error);
      res.status(500).json({ error: 'Error fetching itinerary' });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}
