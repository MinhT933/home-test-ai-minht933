# Using the Flight Schedule App

Article URL: https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App

### In this article, we'll set up the Flight Schedule app so live departures or arrivals for your airport display on your OptiSigns screens.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#WhatYoullNeed)
* [Which Airports Are Covered](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#WhichAirportsAreCovered)
* [How It Works](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#HowItWorks)
* [Create a Flight Schedule App](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#CreateAFlightScheduleApp)
  + [Advanced Settings](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#AdvancedSettings)
* [Reading the Board](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#ReadingTheBoard)
* [Deploying a Flight Schedule App](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#DeployingAFlightScheduleApp)
* [Troubleshooting](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#Troubleshooting)
* [About the Flight Data](https://support.optisigns.com/hc/en-us/articles/55669121864979-Using-the-Flight-Schedule-App#AboutTheFlightData)

Guests in a hotel lobby, a conference center or an office near the airport may want to know if their flight is on time. The Flight Schedule app puts a live departures or arrivals board for your airport on your OptiSigns screens, with expected times, terminal, delays and cancellations.

Here's how to set it up.

---

## What You'll Need

* An OptiSigns account - [**Standard Plan or higher**](https://www.optisigns.com/pricing)
* An [OptiSigns-enabled device](https://support.optisigns.com/hc/en-us/articles/360021855653-What-hardware-and-devices-are-supported)
* A screen, [set up and paired with OptiSigns](https://support.optisigns.com/hc/en-us/articles/18823504383891-OptiSigns-Getting-Started-Guide)
* The airport you want to show. See the coverage note below

---

## Which Airports Are Covered

The app covers more than 300 airports worldwide. You pick one from a searchable list, and the search matches the city, the IATA code (ORD) or the ICAO code (KORD). Because of this, you don't need to know the airport's formal name.

|  |
| --- |
| **NOTE** |
| If your airport isn't in the list, it isn't available yet. There's no way to add one from the portal. |

---

## How It Works

Each Flight Schedule asset shows **one** airport and either Departures or Arrivals. To show both, create two assets and put them in a [Split Screen](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App) or a playlist.

The board covers flights from about 30 minutes ago to roughly 11 hours ahead, and a flight drops off 15 minutes after its time. There's always something on screen, without the board filling up with flights that have already gone. The large time on each row is what the airline currently **expects**, not the time originally published. The board refreshes itself every few minutes while it's playing.

---

## Create a Flight Schedule App

To set up a Flight Schedule app, go to the **Files/Assets** tab, then click **Apps** on the left side of the screen:

![Files/Assets sidebar with the Apps button highlighted](https://support.optisigns.com/hc/article_attachments/55670035900179)

Search then click **Flight Schedule**.

![App picker filtered to Flight, with the Flight Schedule app card highlighted](https://support.optisigns.com/hc/article_attachments/55669145937427)

Enter the details for your board. The panel on the right previews it as you work, so you can see each setting take effect straight away.

![Flight Schedule settings: Name, Airport and Direction, with Advanced collapsed below](https://support.optisigns.com/hc/article_attachments/55669735927059)

* **Name** - The name of your asset. It's for your own use inside OptiSigns and doesn't appear on the board.
* **Airport** - The airport whose flights you want to show. Start typing a city, an IATA code or an ICAO code and the list filters as you type.
* **Direction** - **Departures** or **Arrivals**. One asset shows one or the other, never both.

![Airport picker searched for ORD, with Chicago O'Hare highlighted in the results](https://support.optisigns.com/hc/article_attachments/55669981519635)

|  |
| --- |
| **IMPORTANT** |
| The preview in the settings dialog always shows **SAMPLE DATA.** These are all made-up flights, no matter the airport you pick. It's there to show you the layout, the theme and the pacing, not the flights. To see the real board, save the asset and use **Preview** on it in Files/Assets. |

### Advanced Settings

Everything else is optional and lives under **Advanced**:

![Advanced settings: Theme, Layout, Time format, Use screen's local time and Page speed](https://support.optisigns.com/hc/article_attachments/55669107975059)

* **Theme** - Navy Blue (the default, the classic airport board look), Light for a daylit concourse, Dark for a dim room, or Custom.
* **Board colors** *(Custom theme only)* - Set each part of the board yourself: header background, row background, alternating row, labels and accent, main text, secondary text, and the on-time, delayed and cancelled colors. Reset board colors puts them all back.
* **Layout** - Spacious shows 14 flights in the largest type, readable from further away. Compact shows 28 in two lists side by side. Spacious is the only layout with room for a separate airline column. Compact prints the airline under the flight number.
* **Time format** - 24-hour (14:30) or 12-hour (2:30 PM).
* **Use screen's local time** - On by default, so times follow the clock on the wall beside the screen. Turn it off to use the airport's own time zone - what you want inside the airport itself, or when the board shows a distant airport.
* **Page speed** - How long each page of flights stays on screen: Fast, Normal, Slow, or Custom for anything from 3 to 30 seconds. If every flight fits on one page, the board doesn't page at all and this has no effect.

To show arrivals instead, set **Direction** to **Arrivals**. The board then lists where each flight is coming from rather than where it's going:

![Direction selector open on Departures and Arrivals](https://support.optisigns.com/hc/article_attachments/55670027141907)

![Arrivals board listing origin, airline, flight, time, terminal and status](https://support.optisigns.com/hc/article_attachments/55670049727635)

The board also comes in portrait. Use the control at the top right of the dialog to switch between **Landscape (16:9)**, **Portrait (9:16)** and **Custom** - portrait fits 21 flights in a single list.

When you're happy with it, click **Save** at the bottom right of the dialog.

![Flight Schedule dialog footer with the Save button highlighted](https://support.optisigns.com/hc/article_attachments/55670027386643)

---

## Reading the Board

Once the asset is saved, hover it in **Files/Assets** and click **Preview** to see the real board - the airport's own name sits beside **DEPARTURES** or **ARRIVALS** in the header, with the current time on the right.

![Live departures board for Chicago O'Hare with real flights, terminals and statuses](https://support.optisigns.com/hc/article_attachments/55669115866515)

* **Destination / Origin** - Where the flight is going, or where it came from.
* **Airline** - The carrier's full name. Only displays on spacious landscape mode.
* **Flight** - The flight number.
* **Time** - The expected time. When a flight is delayed, the original time appears struck through.
* **Term** - The terminal. An em dash will display when no terminal has been published yet.
* **Status** - The flight status.
  + **On Time** - Running on schedule, confirmed by live information.
  + **Scheduled** - The published time, with no live update yet.
  + **Boarding** - Displays when flight is currently boarding (departures only).
  + **Gate Closed** - Displays when boarding is concluded, but flight  has yet to depart.
  + **Delayed** - More than 10 minutes behind, with the delay shown.
  + **Departed** - Flight has left.
  + **In Air** - Flight is en route.
  + **Landed** - Flight has arrived.
  + **Cancelled** - Flight has been cancelled.
  + **Diverted** - Flight has been diverted to another airport.

|  |
| --- |
| **NOTE** |
| **Scheduled** means live information hasn't been published for that flight yet - the time shown is still the airline's scheduled time. Some airports publish far less live data than others, so a board can be mostly **Scheduled** and still be correct. |

If flight information stops arriving, the board keeps showing the last update it received under an amber **Connection lost** banner rather than going blank, and reconnects on its own.

---

## Deploying a Flight Schedule App

You can deploy your Flight Schedule app as an individual asset, or as part of a [Split Screen](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App).

To get your new asset to a screen, go to the **Screens** tab, find the screen you want, and click **Edit**:

![Screens list with the Edit button on a screen's row highlighted](https://support.optisigns.com/hc/article_attachments/55674914699539)

The Edit Screen dialog opens:

![Edit Screen dialog showing Device Name, Content Type, Selected Asset and Orientation](https://support.optisigns.com/hc/article_attachments/55674331683731)

Set **Content Type** to **Asset**:

![Edit Screen dialog with the Content Type list open and Asset highlighted](https://support.optisigns.com/hc/article_attachments/55674126229523)

Click **Change**, search for your Flight Schedule asset, select it, then click **Select**:

![Select Asset dialog with the Flight Schedule asset chosen and Select highlighted](https://support.optisigns.com/hc/article_attachments/55674111008531)

Back on the Edit Screen dialog the asset you picked appears under **Selected Asset**. Click **Save** to commit it:

![Edit Screen dialog with the flight board as Selected Asset and Save enabled](https://support.optisigns.com/hc/article_attachments/55674903123987)

Your board will start playing on that screen.

It can also be shown in a Playlist or a Schedule - useful if you want the board up around check-out time and other content for the rest of the day.

---

## Troubleshooting

Here we'll cover some common issues you might find while setting up a Flight Schedule app.

#### The board is empty.

Check that the airport you picked is the one you meant. It's also normal for a board at a smaller airport to thin out overnight, when there genuinely are no flights in the next few hours.

#### The preview doesn't show my airport's flights.

The preview inside the settings dialog isn't meant to - it always shows sample flights, marked **SAMPLE DATA**. Save the asset, then use **Preview** on it in Files/Assets to see the real board.

#### Every row says Scheduled.

Live flight information isn't being published for that airport at the moment, so the board is showing scheduled times. Those times are still correct.

#### Times look an hour out.

Check **Use screen's local time** under **Advanced**. On, the board uses the clock where the screen is; off, it uses the airport's own time zone.

#### The Term column is empty.

Not every airport publishes terminal assignments, and those that do usually publish them only closer to the flight. An em dash means "not announced yet" - the same thing the airport's own board shows.

#### Flights page past too quickly, or sit too long.

Adjust **Page speed** under **Advanced**.

#### A banner says "Connection lost".

The board hasn't had an update for a while and is showing the last one it received. It reconnects by itself; if it stays up for more than a few hours, contact support.

---

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
