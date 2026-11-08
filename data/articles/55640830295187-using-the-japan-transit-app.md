# Using the Japan Transit App

Article URL: https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App

### In this article, we'll set up the Japan Transit app so live Toei train or bus departures display on your OptiSigns screens.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#WhatYoullNeed)
* [Which Stations and Stops Are Covered](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#WhichStationsAndStopsAreCovered)
* [How It Works](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#HowItWorks)
* [Create a Japan Transit App](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#CreateAJapanTransitApp)
* [Reading the Board](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#ReadingTheBoard)
* [Deploying a Japan Transit App](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#DeployingAJapanTransitApp)
* [Troubleshooting](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#Troubleshooting)
* [Data Source and Attribution](https://support.optisigns.com/hc/en-us/articles/55640830295187-Using-the-Japan-Transit-App#DataSourceAndAttribution)

If your venue is in Tokyo, a departure board in the lobby answers the question every visitor is already asking: when is the next one? The Japan Transit app pulls live Toei subway and Toei bus departures from the Public Transportation Open Data Center (ODPT) and puts them on your screens in Japanese, English, or both.

Here's how to set it up.

---

## What You'll Need

* An OptiSigns account - [**Standard Plan or higher**](https://www.optisigns.com/pricing)
* An [OptiSigns-enabled device](https://support.optisigns.com/hc/en-us/articles/360021855653-What-hardware-and-devices-are-supported)
* A screen, [set up and paired with OptiSigns](https://support.optisigns.com/hc/en-us/articles/18823504383891-OptiSigns-Getting-Started-Guide)
* A venue near a **Toei** station or bus stop - see the coverage note below

---

## Which Stations and Stops Are Covered

The app covers the **Toei** network operated by the Tokyo Metropolitan Bureau of Transportation:

* **Subway Services**: Asakusa Line, Mita Line, Shinjuku Line, Oedo Line
* **Bus Services:** All Toei-operated routes and stops

|  |
| --- |
| **IMPORTANT** |
| Tokyo Metro, JR East, and private railways are **not** included. If your nearest station is served by both Toei and another operator, the board shows only the Toei lines at that station. Choosing a station with no Toei service leaves the board empty. We intend to add additional operators as time goes on. |

---

## How It Works

Each Japan Transit asset shows a single station or bus stop, and lists every Toei line or route that serves it. Departure times come from the published Toei timetable, refreshed daily, with live running information layered on top so a train that is late shows as delayed rather than on time. When a station has more departures than fit on one page, the board pages through them at the speed you choose.

---

## Create a Japan Transit App

To set up a Japan Transit app, go to the **Files/Assets** tab, then click **Apps** on the left side of the screen:

| English / 英語 | Japanese / 日本語 |
| --- | --- |
| Files/Assets sidebar with the Apps button highlighted | Japanese portal sidebar with the Apps button highlighted |

Search for `Japan`, then click **周辺交通情報 / Japan Transit**.

| English / 英語 | Japanese / 日本語 |
| --- | --- |
| App picker filtered to Japan, with the Japan Transit card highlighted | Japanese app picker with the Japan Transit card highlighted |

Enter the details for your Transit app. The panel on the right previews the board as you work - before you pick a station it shows sample data, so you can see the layout immediately.

![Japan Transit settings in Train mode: Name, Transit Type, Station and Language](https://support.optisigns.com/hc/article_attachments/55640851939987)

* **Name** - This is the name of your asset. It is for internal OptiSigns use and will not display on your screens.
* **Transit Type** - Choose whether this screen shows **Train** departures or **Bus** departures. One asset shows one or the other, never both. To show both, create two assets and put them in a [Split Screen](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App) or a playlist.
* **Station** *(Train)* - The station whose departures you want to show. Every Toei line serving that station appears on the board.
* **Bus Stop** *(Bus)* - The stop whose arrivals you want to show. Every Toei route serving that stop appears on the board.
* **Language** - **Japanese**, **English**, or **Bilingual**. Bilingual shows Japanese first with English underneath, which is the usual choice for hotels and offices with international visitors.

The station and bus stop lists are long, so both fields are searchable - start typing and the list filters as you go.

![Station picker open, listing Toei stations in Japanese and English with a search box](https://support.optisigns.com/hc/article_attachments/55640852149523)

Under **Display Options** you'll find two more settings:

![Display Options expanded, showing the Theme and Speed settings](https://support.optisigns.com/hc/article_attachments/55640852252179)

* **Theme** - **Light** or **Dark**. Dark reads better on a screen in a dim lobby or at night.
* **Speed** - How long each page of departures stays on screen, from 3 to 30 seconds (**Fast** 6s, **Normal** 10s, **Slow** 20s). If all the departures fit on one page, the board doesn't page at all and this setting has no effect.

To show bus arrivals instead, set **Transit Type** to **Bus** and pick a **Bus Stop**:

![Japan Transit settings in Bus mode, with the Bus Stop field in place of Station](https://support.optisigns.com/hc/article_attachments/55640859143059)

When you're happy with the preview, click **Save**.

---

## Reading the Board

The train and bus boards use standard Japanese departure-board wording, with English alongside it in Bilingual mode. The two boards show different columns.

![Train departure board showing line, destination, next stop, train type, time and status](https://support.optisigns.com/hc/article_attachments/55640859207315)

* **Line / Service (路線・種別)** - The line, with its official Toei line color.
* **Destination (行き先)** - Where the service terminates.
* **Next Stop (次の停車駅)** - The next station it calls at. If the line ends, it will read 終点 / Terminus.
* **Train Type (種別)** - Local, express, etc.
* **Departure (発車時刻)** - Scheduled departure time, in a 24-hour format.
* **Status (状況)** - Shows the train status, which will read one of the following:
  + **On Time (定刻)** - Running on schedule.
  + **Delayed (遅延 +X分)** - Running late, by the number of minutes shown.
  + **Cancelled (運休)** - This service was scheduled, but is no longer running.
  + **Schedule Only (時刻表のみ)** - The timetable entry, with no live running information available yet.

|  |
| --- |
| **NOTE** |
| **Schedule only** is normal, not an error. Live running information isn't published for every service at every moment, and the board falls back to the published timetable rather than showing nothing. |

The bus board shows different columns:

![Bus arrival board showing route, destination, next stop, boarding stand and arrival time](https://support.optisigns.com/hc/article_attachments/55640859292051)

* **Route (系統)** - The Toei route number.
* **Destination (行き先)** - Where the route terminates.
* **Next Stop (次の停留所)** - The next stop it calls at.
* **Boarding (のりば)** - Which stand the bus leaves from.
* **Arrival (到着予定)** - Expected arrival time.

The bus board has no separate status column. The expected arrival time carries the status by its colour, and when a bus is running late the original scheduled time appears struck through just beneath it, so you can see both what was planned and what to expect. A row marked **翌日 / Tomorrow** is the first service of the next day, shown once the current day's timetable for that route has run out.

Times follow the Japanese convention of counting past midnight, so a 12:10 am departure appears as `24:10` on the last trains of the day.

---

## Deploying a Japan Transit App

You can deploy your new Japan Transit app as an individual asset, or as part of a [Split Screen](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App).

To get your new asset to a screen, go to the **Screens** tab, find the screen you want, and click **Edit**. Set **Content Type** to **Asset**, then browse or search for your Japan Transit asset and click **Select**.

| English / 英語 | Japanese / 日本語 |
| --- | --- |
| Select Asset dialog with a Japan Transit board previewed and Select highlighted | Japanese Select Asset dialog with a Japan Transit board and Select highlighted |

Back on the Edit Screen dialog, click **Save**. Your transit board will now display on screen.

It can also be shown in a Playlist or a Schedule - handy if you want the board up during commuting hours and other content the rest of the day.

---

## Troubleshooting

**The board is empty.**

Check that the station or stop you picked is actually served by Toei - Tokyo Metro and JR stations have no Toei departures to show. It's also normal for a train board to be empty overnight, between the last train and the first one of the next morning.

**A new board takes a few seconds to fill.**

The first time you select a station or stop, the departures for it are prepared in the background. The board shows **運行情報を取得しています / Loading departures…** while that happens, and fills in within a few seconds.

**Every row says 時刻表のみ / Schedule only.**

Live running information isn't available for that station or stop at the moment, so the board is showing the published timetable. Departure times are still correct.

**Only some of the lines at my station appear.**

Only the Toei lines are shown. Lines run by other operators at the same station are outside the app's coverage.

**Departures scroll past too quickly, or sit too long.**

Adjust **Speed** under **Display Options** in the asset's settings.

---

## Data Source and Attribution

Departure information comes from the Public Transportation Open Data Center (ODPT). The board shows the required source and licence attribution on screen. The data is provided by the transport operators and ODPT, and is not guaranteed to be accurate or complete.

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
