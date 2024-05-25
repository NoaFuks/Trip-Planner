import React from 'react';
import styles from '../styles/SelectedTrip.module.css';

const SelectedTrip = ({ option, itinerary }) => {
  // Formats the itinerary based on the detailed function provided earlier
  const formatItinerary = (itineraryText) => {
    const days = itineraryText.split(/(?=Day \d+: \d{4}-\d{2}-\d{2})/).filter(Boolean);
    return days.map((day, index) => (
      <div key={index} className={styles.daySection}>
        <img 
          src={option.images[index]} 
          alt={`Day ${index + 1}`} 
          style={{ width: '200px', height: 'auto' }} // Adjust width as needed for smaller display
        />
        {day.split('\n').map((item, idx) => {
          if (idx === 0) {
            return <h4 key={idx} className={styles.dayHeader}>{item.trim()}</h4>;
          } else {
            const timePattern = /\d{1,2}:\d{2} [AP]M:/;
            if (item.trim().match(timePattern)) {
              return <p key={idx} className={styles.timeEntry}><strong>{item.trim()}</strong></p>;
            }
            return <p key={idx} className={styles.generalEntry}>{item.trim()}</p>;
          }
        })}
      </div>
    ));
  };

  return (
    <div>
      <div className="box">
        <h2 className="title">Selected Trip:</h2>
        <p className="content">Destination: {option.destination}</p>
        <p className="content">Total Cost: ${option.total_cost}</p>
      </div>

      <div className="box">
        <h3 className="title">Flights</h3>
        <div className="content">
          <h4>Outbound Flight:</h4>
          <p>Cost: ${option.flight_info.outbound.price}</p>
          <p>Departure: {option.flight_info.outbound.departure_airport} at {option.flight_info.outbound.departure_time}</p>
          <p>Arrival: {option.flight_info.outbound.arrival_airport} at {option.flight_info.outbound.arrival_time}</p>
          <h4>Return Flight:</h4>
          <p>Cost: ${option.flight_info.return.price}</p>
          <p>Departure: {option.flight_info.return.departure_airport} at {option.flight_info.return.departure_time}</p>
          <p>Arrival: {option.flight_info.return.arrival_airport} at {option.flight_info.return.arrival_time}</p>
        </div>
      </div>

      <div className={styles.box}>
        <h3 className={styles.title}>Hotel Information</h3>
        <p className={styles.content}>{option.hotel_info}</p>
      </div>

      <div className="box">
        <h3 className="title">Daily Itinerary</h3>
        <div className="content">
          {formatItinerary(itinerary)}
        </div>
      </div>
    </div>
  );
};

export default SelectedTrip;

