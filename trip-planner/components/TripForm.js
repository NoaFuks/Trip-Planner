import { useState } from 'react';
import axios from 'axios';
import TripOptions from './TripOptions';
import SelectedTrip from './SelectedTrip';  // New component for displaying the selected trip details
import styles from '../styles/TripForm.module.css'; // Assuming the CSS module is in the same directory for simplicity

const TripForm = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [budget, setBudget] = useState('');
  const [tripType, setTripType] = useState('');
  const [result, setResult] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);
  const [itinerary, setItinerary] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/plan-trip', {
        start_date: startDate,
        end_date: endDate,
        budget,
        trip_type: tripType,
      });
      setResult(response.data);
      setSelectedOption(null);
      setItinerary(null);
    } catch (error) {
      console.error('Error planning trip:', error);
      setResult(null);
    }
  };

  const handleSelectOption = async (option) => {
    try {
      const response = await axios.post('/api/select-trip', {
        start_date: startDate,
        end_date: endDate,
        trip_type: tripType,
        destination: option.destination,
      });
      setSelectedOption(option);
      setItinerary(response.data.itinerary);
    } catch (error) {
      console.error('Error selecting trip:', error);
      setSelectedOption(null);
      setItinerary(null);
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Start Date:</label>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required className={styles.input} />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>End Date:</label>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required className={styles.input} />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Budget (USD):</label>
          <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} required className={styles.input} />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Trip Type:</label>
          <select value={tripType} onChange={(e) => setTripType(e.target.value)} required className={styles.select}>
            <option value="">Select Trip Type</option>
            <option value="ski">Ski</option>
            <option value="beach">Beach</option>
            <option value="city">City</option>
          </select>
        </div>
        <button type="submit" className={styles.button}>Plan Trip</button>
      </form>
      {result && !selectedOption && (
        <TripOptions options={result.trip_options} onSelectOption={handleSelectOption} />
      )}
      {selectedOption && (
        <SelectedTrip option={selectedOption} itinerary={itinerary} />
      )}
    </div>
  );
};

export default TripForm;
