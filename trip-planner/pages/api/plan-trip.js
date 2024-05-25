import axios from 'axios';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { start_date, end_date, budget, trip_type } = req.body;

    try {
      // Call your FastAPI backend
      const response = await axios.post('http://127.0.0.1:8000/plan-trip', {
        start_date,
        end_date,
        budget,
        trip_type,
      });

      res.status(200).json(response.data);
    } catch (error) {
      console.error('Error planning trip:', error);
      res.status(500).json({ error: 'Error planning trip' });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}
