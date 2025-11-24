const RECIPIENT_EMAIL = // internal recipient's email
const CALENDAR_ID = // Calendar ID for Google to reference

function onFormSubmit(e) {
  const data = e.namedValues;

  const responseHeader = 'Do you need lunch for your meeting?'; // must match column exactly
  const eventIdHeader = 'Event ID - DO NOT CHANGE';            // must match column exactly
  const restaurantHeader = 'What restaurant do you want food from?'
  const attendeesHeader = 'How many people will attend?'
  const restrictionsHeader = 'Are there any dietary restrictions/allergies to be aware of?'

  const response = data[responseHeader] ? data[responseHeader][0].toLowerCase() : '';
  const eventIdRaw = data[eventIdHeader] ? data[eventIdHeader][0] : '';
  const eventId = decodeURIComponent(eventIdRaw);

  const restaurant = data[restaurantHeader] ? data[restaurantHeader][0] : 'Not specified';
  const attendees = data[attendeesHeader] ? data[attendeesHeader][0] : 'Not specified';
  const restrictions = data[restrictionsHeader] ? data[restrictionsHeader][0] : 'None';
  

  if (response !== 'yes') return;

  // Look up the event in the calendar
  const calendar = CalendarApp.getCalendarById(CALENDAR_ID);
  const event = calendar.getEventById(eventId);

  let subject, body;

  if (event) {
    const startTime = Utilities.formatDate(event.getStartTime(), Session.getScriptTimeZone(), 'MMM dd, yyyy HH:mm');
    const organizer = event.getCreators()[0] || 'Unknown';
    const title = event.getTitle();

    subject = `Lunch requested for meeting: ${title} at ${startTime}`;
    body = `
Lunch has been requested for the following meeting:

Title: ${title}
Organizer: ${organizer}
Date & Time: ${startTime}

Preferred restaurant: ${restaurant}
Number of attendees: ${attendees}
Dietary restrictions/allergies: ${restrictions}

`;
  } else {
    subject = `Lunch requested (Event ID ${eventId})`;
    body = `
Lunch has been requested, but the event could not be found.

Event ID: ${eventId}
`;
  }

  MailApp.sendEmail(RECIPIENT_EMAIL, subject, body);
  Logger.log(`Email sent to RECIPIENT for event ID ${eventId}`);
}
