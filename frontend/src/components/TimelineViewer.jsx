import React, { useMemo } from 'react';
import { FaCircle } from 'react-icons/fa';

const TimelineViewer = ({ content }) => {
  // Parse timeline events from content
  const events = useMemo(() => {
    try {
      const data = JSON.parse(content);
      return Array.isArray(data) ? data : [];
    } catch {
      return parseTextTimeline(content);
    }
  }, [content]);

  if (events.length === 0) {
    return (
      <div className="timeline-viewer">
        <div className="timeline-empty">No timeline events available</div>
      </div>
    );
  }

  return (
    <div className="timeline-viewer">
      <div className="timeline-container">
        {events.map((event, index) => (
          <div key={index} className="timeline-event">
            <div className="timeline-marker">
              <FaCircle className="timeline-dot" />
              {index < events.length - 1 && <div className="timeline-line"></div>}
            </div>
            <div className="timeline-content">
              <div className="timeline-date">{event.date}</div>
              <div className="timeline-title">{event.title}</div>
              {event.description && (
                <div className="timeline-description">{event.description}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Parse text-based timeline
const parseTextTimeline = (text) => {
  const events = [];
  const lines = text.split('\n').filter((l) => l.trim());

  let currentEvent = null;

  lines.forEach((line) => {
    const trimmed = line.trim();

    // Look for date patterns (YYYY, MM/DD/YYYY, etc.)
    const dateMatch = trimmed.match(/^(\d{4}|\d{1,2}\/\d{1,2}\/\d{2,4}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4})/);

    if (dateMatch) {
      // New event with date
      if (currentEvent) {
        events.push(currentEvent);
      }
      currentEvent = {
        date: dateMatch[1],
        title: trimmed.replace(dateMatch[0], '').replace(/^[\s:-]+/, ''),
        description: '',
      };
    } else if (currentEvent) {
      // Add to description
      if (currentEvent.title && !currentEvent.description) {
        currentEvent.description = trimmed;
      } else if (currentEvent.description) {
        currentEvent.description += ' ' + trimmed;
      } else {
        currentEvent.title += ' ' + trimmed;
      }
    }
  });

  // Add last event
  if (currentEvent) {
    events.push(currentEvent);
  }

  // If no events with dates, try bullet point format
  if (events.length === 0) {
    let currentDate = '';
    lines.forEach((line) => {
      const trimmed = line.trim();
      if (trimmed.match(/^#+\s*/)) {
        // Heading as date
        currentDate = trimmed.replace(/^#+\s*/, '');
      } else if (trimmed.match(/^[-*•]\s*/)) {
        // Bullet point as event
        const text = trimmed.replace(/^[-*•]\s*/, '');
        events.push({
          date: currentDate || 'Unknown',
          title: text,
          description: '',
        });
      }
    });
  }

  return events.length > 0
    ? events
    : [
        {
          date: 'Sample Date',
          title: 'Sample Event',
          description: 'Sample Description',
        },
      ];
};

export default TimelineViewer;
