import React, { useEffect } from 'react';
import styles from '../styles/SelectedTrip.module.css';

const SelectedTrip = ({ option, itinerary, images }) => {
  useEffect(() => {
    console.log("Received itinerary:", itinerary);
    console.log("Received images:", images);
  }, [itinerary, images]);

  const formatItinerary = (itineraryText) => {
    if (!itineraryText) {
      return <p>No itinerary available.</p>;
    }

    const days = itineraryText.split(/(?=Day \d+: \d{4}-\d{2}-\d{2})/).filter(Boolean);
    return days.map((day, index) => (
      <div key={index} className={styles.daySection}>
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

  const displayImages = () => {
    if (!Array.isArray(images) || images.length === 0) {
      return <p>No images available.</p>;
    }

    return images.map((image, index) => (
      <img key={index} src={image} alt={`Trip Image ${index + 1}`} className={styles.tripImage} />
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

      <div className="box">
        <h3 className="title">Trip Images</h3>
        <div className={styles.imagesContainer}>
          {displayImages()}
        </div>
      </div>
    </div>
  );
};

export default SelectedTrip;




