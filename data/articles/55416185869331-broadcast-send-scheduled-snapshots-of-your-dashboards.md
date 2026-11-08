# Broadcast: Send Scheduled Snapshots of Your Dashboards

Article URL: https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards

### In this article, we'll set up a Broadcast that captures a snapshot of your dashboards on a schedule and delivers it by email, to Microsoft Teams, to a webhook, or as a PDF.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#WhatYoullNeed)
* [How It Works](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#HowItWorks)
* [Where to Find Broadcast](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#WhereToFindBroadcast)
* [Create a Broadcast](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#CreateABroadcast)
* [Destinations](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#Destinations)
* [Manage Your Broadcasts](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#ManageYourBroadcasts)
  + [Run History](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#RunHistory)
* [Snapshots](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#Snapshots)
* [Troubleshooting and FAQs](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#Troubleshooting)
* [For Developers: Webhook Payload](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#ForDevelopersWebhookPayload)

Broadcast takes a picture of a dashboard on a schedule you choose and delivers it to the people who need it. It can be sent by email, to a Microsoft Teams channel, to your own system through a webhook, or as a PDF saved in OptiSigns.

Use it to send the weekly KPI dashboard to leadership every Monday morning, post the daily production board to a Teams channel before stand-up, or keep a PDF record of what a screen showed each day. The people receiving it never need an OptiSigns login.

---

## What You'll Need

* An OptiSigns account on the [**Pro Plus**, **Engage** or **Enterprise**](https://www.optisigns.com/pricing) plan.
* An **account admin** role - Owner, Admin or Super Admin.
* At least one asset worth capturing. This is usually a BI dashboard such as Power BI, Tableau, Grafana or Looker Studio, but can be anything you wish.

|  |
| --- |
| **NOTE** |
| If you have just upgraded your plan, Broadcast can take up to 15 minutes to appear. Signing out and back in applies it immediately. |

---

## How It Works

On each scheduled run OptiSigns opens each asset, waits for it to render, captures it, and delivers the images to every destination you listed.

You will provide:

* Which asset(s) to capture
* Where to send them
* How often (scheduled, just once, etc.)

Creating a broadcast does not run it. Use **Run now** when you want to see the result immediately. Every snapshot sent is filed under the **Snapshots** tab so you can see it again when you want.

---

## Where to Find Broadcast

* **Settings** > **Data & Monitoring** > **Broadcast** - the main page, with two tabs: **Broadcasts** and **Snapshots**.
* **Files/Assets** - an asset's three-dot menu has **Add to Broadcast**, and **Show Broadcasts Using This** to see which broadcasts already include it.

![Broadcast page with the Broadcasts and Snapshots tabs and the New broadcast button](https://support.optisigns.com/hc/article_attachments/55416153771283)

---

## Create a Broadcast

Go to **Settings** > **Broadcast** and select **New broadcast**.

Enter a **Broadcast name**. This is what recipients see as the title of the message.

![New broadcast dialog showing name, Send to, Selected assets and schedule fields](https://support.optisigns.com/hc/article_attachments/55416180665363)

Under **Send to**, select a destination icon. For more information on these, see [Destinations](https://support.optisigns.com/hc/en-us/articles/55416185869331-Broadcast-Send-Scheduled-Snapshots-of-Your-Dashboards#Destinations) below. Each one opens as a card you fill in and then select **Done** on. Once you have added one, the remaining destinations appear under **Add more:**

![Email destination expanded showing Recipients, Subject and the Needs setup badge](https://support.optisigns.com/hc/article_attachments/55416167605779)

Next to **Selected assets**, select **Change** and choose one or more assets.

|  |
| --- |
| **NOTE** |
| Broadcast captures a single still image, so only content that renders as one is offered. Video, audio, live streams, split screens, folders, kiosk and Engage content are not in the picker. Dashboards, clocks, tickers, calendars, news and social assets are. Screens themselves cannot be broadcast - pick the asset the screen plays instead. |

When you select more than one asset, a **Delivery mode** option appears:

* **One message with all items** - a single message containing every snapshot. This is the default.
* **One message per item** - a separate message for each asset.
* **Combined PDF** - one PDF containing all the snapshots.

With a single asset the option is hidden.

Choose a **Frequency**: **Daily**, **Weekdays**, **Weekly**, **Monthly** or **Custom**.

Then set the **Run window** - the hour the snapshot is taken in, for example **09:00 - 10:00** - and the **Time Zone** the schedule follows. The capture fires at the start of that hour. A **Custom** schedule sets its own time, so the run window does not apply to it.

Select **Create**. The broadcast is saved and scheduled, but does not run until its first scheduled time - or until you use **Run now**.

---

## Destinations

The following are the destinations you can send a Broadcast to:

* **Email -** Input several email addresses. These addresses will receive an email containing the snapshot(s) you've set the Broadcast up to take.
* **Microsoft Teams -** Input a Teams webhook URL. This will create a card in your Teams channel with the snapshots. For more on this, see [How to Get a Microsoft Teams Webhook URL for OptiSigns Broadcast](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast).
* **Webhook** - A generic Webhook URL. This will send a JSON POST request to the webhook containing links to the snapshots.
* **PDF** - For this, input nothing. A PDF will be filed under the Snapshots tab each run, and can be disseminated however you wish.

Every delivered message carries a link back to that broadcast's settings in OptiSigns.

---

## Manage Your Broadcasts

The **Broadcasts** tab lists every broadcast with its **Name**, **Send to**, **Content**, **Schedule**, **Last run** and **Active** state.

Use the **Active** switch to pause a broadcast without deleting it. A paused broadcast is badged **Paused** and resumes when you switch it back on.

From a broadcast's **...** menu:

* **Run now** - capture and deliver immediately, outside the schedule. Unavailable while a run is already in progress.
* **Edit** - change the name, assets, destinations or schedule.
* **Duplicate** - create a paused copy, ready to adjust.
* **View run history** - every run with its status and per-destination result.
* **Delete**.

### Run History

**View run history** shows each run's **Scheduled for** time, **Status**, **Deliveries** and **Files**. A delivery that failed is listed with the error returned by the receiving service and carries a **Retry** button, so you can re-send it without waiting for the next run.

A run can also succeed partially - the history shows how many of the selected assets were captured.

---

## Snapshots

The **Snapshots** tab is the archive of every snapshot taken for your account. Search it, or filter by date, broadcast, destination and status, then download or delete snapshots - individually or in bulk. Runs you triggered yourself are tagged **Manual**.

|  |
| --- |
| **IMPORTANT** |
| Snapshots are kept for **30 days**. Download links - including the links inside delivered messages - expire after **7 days**. Save anything you need to keep. |

---

## Troubleshooting and FAQs

#### **A destination says "Needs setup"**

A required field is empty or invalid. Teams and webhook URLs must start with `https://`; email recipients must be valid addresses separated by `;`.

#### **Nothing arrived.**

Open **View run history** for that broadcast. It shows whether the snapshot was captured and which destination failed, with the error returned by the receiving service. Fix the destination, then use **Retry** on the failed delivery, or **Run now**.

#### **Run now is greyed out.**

A run is already queued or capturing for that broadcast. Only one run at a time is allowed - wait for it to finish.

#### **The Teams card never appeared.**

Check that the Teams workflow is still **On** and that its owner still has access to the channel. See the Teams article above.

#### **I can't find Broadcast.**

Broadcast needs an account admin on the Pro Plus, Engage or Enterprise plan. If you have just upgraded, allow up to 15 minutes or sign out and back in.

#### **The asset I want isn't in the picker.**

Broadcast captures a single still image, so video, audio, live streams, split screens and kiosk content are excluded by design. Screens cannot be broadcast - choose the asset the screen plays.

---

## For Developers: Webhook Payload

Each run sends a POST request with a JSON body like this:

```
{
  "broadcastId": "...",
  "title": "Weekly KPIs",
  "runId": "...",
  "scheduledFor": "2026-09-14T09:00:00.000Z",
  "artifacts": [
    { "url": "https://...", "contentType": "image/png", "filename": "..." }
  ],
  "linkBack": "https://app.optisigns.com/app/s/broadcasts?broadcastId=...&view=edit"
}
```

* artifacts[].url are signed links that expire after 7 days - download them if you need to keep them.
* reportId (the same value as broadcastId) and artifactUrl / artifactContentType (the first artifact) are also sent, for older integrations.
* For a run you started with Run now, scheduledFor is sent as manual: followed by a timestamp rather than an ISO date.
* Respond with a 2xx status. Any other response is recorded as a failed delivery in the run history, where it can be retried.

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
