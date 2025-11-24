const CALENDAR_ID = // Google calendar ID
const FORM_BASE_URL = // Form prefill URL

function checkUpcomingMeetings() {
  const calendar = CalendarApp.getCalendarById(CALENDAR_ID);
  const now = new Date();
  const fourWeeksLater = new Date(now.getTime() + 28 * 24 * 60 * 60 * 1000); // 28 days ahead
  const events = calendar.getEvents(now, fourWeeksLater);

  const timeZone = Session.getScriptTimeZone(); // ensures correct time zone

  Logger.log(`Found ${events.length} events`);

  events.forEach(event => {
    const start = event.getStartTime();
    const hour = parseInt(Utilities.formatDate(start, timeZone, 'HH')); // hour in 24h format in correct time zone

    // Only consider meetings between 11:00 and 12:59
    if (hour >= 11 && hour < 13) {
      Logger.log(`Checking event: ${event.getTitle()} at ${formatTime(start, timeZone)}`);

      // Attempt to find a human organizer (first guest who is not the room)
      const organizerEmail = event.getGuestList().find(g => !g.getEmail().includes('resource.calendar.google.com'))?.getEmail()
                             || event.getCreators()[0]
      Logger.log(`Organizer email: ${organizerEmail}`);

      if (!PropertiesService.getScriptProperties().getProperty(event.getId())) {
        sendLunchEmail(event, organizerEmail, timeZone);
        PropertiesService.getScriptProperties().setProperty(event.getId(), 'sent');
      }
    }
  });
}

function sendLunchEmail(event, organizerEmail, timeZone) {
  const subject = `Lunch for your Fenton meeting at ${formatTime(event.getStartTime(), timeZone)}`;
  const formLink = FORM_BASE_URL + '&entry.1419951487=' + encodeURIComponent(event.getId());


  const body = `
Hi ${event.getCreators()[0] || 'Organizer'},

Your meeting "${event.getTitle()}" in Fenton is scheduled for ${formatTime(event.getStartTime(), timeZone)}.

Do you need lunch for this meeting? Please respond here: ${formLink}

Thank you!
`;

  Logger.log(`Sending email to: ${organizerEmail}`);
  MailApp.sendEmail(organizerEmail, subject, body);
}

function formatTime(date, timeZone) {
  return Utilities.formatDate(date, timeZone, 'MMM dd, yyyy HH:mm');
}
