The HR team at my workplace brought me an interesting project based on a persistent issue they had with conference rooms being reserved via Google Calendar. Often, someone would schedule a meeting in a conference room and reserve the space via Calendar, but they wouldn't request food for the meeting from HR until the day of. This led to HR often being unable to get quality food or food at all for the meetings.

So, I figured, what if every time someone creates a calendar event around lunch time in a conference room, they're asked whether they need food for it via email automatically? Then, their response could be automatically recorded and emailed to the person responsible for ordering lunch.

The form response script triggers every few minutes, scanning for new events in the specified calendar. If it detects a new event, it checks whether it's scheduled between 11am and 1pm, and if it is, it sends the organizer a link to a Google Form. 

The form asks if the organizer needs food and, if so, where they want it from, how many people will be in attendance, and if there are any dietary restrictions.

Once the form is submitted, the next script triggers, reading each column of the new response. It uses the "EVENT ID" field to reference the calendar event itself to determine the time and organizer of the event. If the response answer to the question of whether food is needed is "yes," it formats the info (restaurant, attendees, etc) into an email which is sent to the person responsible for ordering food.

AI tools helped to template this project, as I didn't know previously how Google Apps Script could integrate with calendars and sheets. One key challenge of this project was the EVENT_ID and determining how to get it to integrate with the form so that the date/time/organizer info could be pulled from the event. I was able to create a form that pre-filled the EVENT ID field so that both scripts could understand which event was being referenced without that data being input manually at all.
