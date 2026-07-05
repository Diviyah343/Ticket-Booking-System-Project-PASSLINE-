import { useEffect, useState } from 'react'
import axios from 'axios'

function Events() {
  const [events, setEvents] = useState([])

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/events')
        setEvents(response.data.events || [])
      } catch (error) {
        console.error('Failed to fetch events', error)
      }
    }

    fetchEvents()
  }, [])

  return (
    <div>
      <h1>Events</h1>
      {events.length === 0 ? (
        <p>No events found.</p>
      ) : (
        <ul>
          {events.map((event) => (
            <li key={event.id}>
              <strong>{event.title}</strong>
              <div>Venue: {event.venue}</div>
              <div>Date: {event.event_date}</div>
              <div>Available seats: {event.available_seats}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Events
