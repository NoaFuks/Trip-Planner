import { useState } from 'react';
import styles from '../styles/TripOptions.module.css';

const TripOptions = ({ options, onSelectOption }) => {
  const [selectedOptionIndex, setSelectedOptionIndex] = useState(null);

  const handleSelectOption = (option, index) => {
    onSelectOption(option);
    setSelectedOptionIndex(index);
  };

  // Check if options is defined and has length before trying to render it
  if (!options || options.length === 0) {
    return <p>No options available</p>;
  }

  return (
    <div className={styles.tripOptions}>
      <h2>Trip Suggestions:</h2>
      {options.map((option, index) => {
        // Only render the selected option or all options if none is selected
        if (selectedOptionIndex === null || selectedOptionIndex === index) {
          return (
            <div key={index} className={styles.tripOption}>
              <h3>Option {index + 1}</h3>
              <p>Destination: {option.destination}</p>
              <p>Total Cost: ${option.total_cost}</p>
              {option.flight_info ? (
                <>
                  <h4>Outbound Flight:</h4>
                  <p>Cost: ${option.flight_info.outbound.price}</p>
                  <p>Departure: {option.flight_info.outbound.departure_airport} at {option.flight_info.outbound.departure_time}</p>
                  <p>Arrival: {option.flight_info.outbound.arrival_airport} at {option.flight_info.outbound.arrival_time}</p>
                  <h4>Return Flight:</h4>
                  <p>Cost: ${option.flight_info.return.price}</p>
                  <p>Departure: {option.flight_info.return.departure_airport} at {option.flight_info.return.departure_time}</p>
                  <p>Arrival: {option.flight_info.return.arrival_airport} at {option.flight_info.return.arrival_time}</p>
                </>
              ) : (
                <p>No flight information available</p>
              )}
              <div className={styles.hotelInfo}>
                <h4>Hotel Information:</h4>
                <p>{option.hotel_info}</p>
              </div>
              <button onClick={() => handleSelectOption(option, index)} className={styles.button}>
                Select this option
              </button>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
};

export default TripOptions;