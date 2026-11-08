# How to Get a Microsoft Teams Webhook URL for OptiSigns Broadcast

Article URL: https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast

### In this article, we'll create a Microsoft Teams Workflows webhook URL and paste it into an OptiSigns Broadcast, so your scheduled snapshots post straight into a Teams channel.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast#WhatYoullNeed)
* [Create the Webhook in Teams](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast#CreateTheWebhookInTeams)
* [Add It to Your Broadcast](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast#AddItToYourBroadcast)
* [What Appears in Teams](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast#WhatAppearsInTeams)
* [Troubleshooting](https://support.optisigns.com/hc/en-us/articles/55416186918163-How-to-Get-a-Microsoft-Teams-Webhook-URL-for-OptiSigns-Broadcast#Troubleshooting)

To deliver an OptiSigns Broadcast to a Microsoft Teams channel, OptiSigns needs a Workflows webhook URL for that channel. You create it once in Teams using the built-in Workflows app, then paste it into your broadcast.

---

## What You'll Need

* Permission to add workflows to the Teams channel. If **Workflows** isn't available on the channel menu, ask your Microsoft 365 administrator.
* An OptiSigns account with Broadcast. See [Broadcast: Send Scheduled Snapshots of Your Dashboards](https://support.optisigns.com/hc/en-us/articles/55416185869331) for what Broadcast is and which plans include it.

|  |
| --- |
| **TIP** |
| The workflow runs under the account that creates it. For a broadcast you expect to keep running, create the workflow with an account that will keep access to the channel — a shared or service account rather than a personal one. |

---

## Create the Webhook in Teams

In Microsoft Teams, open the **channel** where you want snapshots to appear. Select **... (More options)** next to the channel name, then choose **Workflows**.

![Teams More options menu open with Workflows highlighted](https://support.optisigns.com/hc/article_attachments/55442604366611)

Search for the template **Send webhook alerts to a channel** and select it.

![Workflows template picker with Send webhook alerts to a channel highlighted](https://support.optisigns.com/hc/article_attachments/55442575138323)

The template opens its **Parameters**. Because you started from the channel, **Team the channel is in** and **Channel** are already filled in - check them, then select **Save**.

![Send webhook alerts to channel parameters: Team the channel is in, Channel, and Save](https://support.optisigns.com/hc/article_attachments/55442609134611)

When Teams confirms the workflow was created, select **Copy webhook link**.

![Created workflow showing the Copy webhook link button and Active status](https://support.optisigns.com/hc/article_attachments/55442587811091)

The URL starts with https:// and contains /workflows/.

|  |
| --- |
| **IMPORTANT** |
| Keep this URL private. Anyone who has it can post messages to your channel. To revoke it, delete the workflow in Teams and create a new one. |

---

## Add It to Your Broadcast

1. In OptiSigns, go to **Settings** > **Broadcast** and create or edit a broadcast.
2. Under **Send to**, add **Microsoft Teams**.
3. Paste the URL into the **Teams webhook URL** field, select **Done**, then save the broadcast.
4. Use **Run now** on the broadcast's **...** menu to confirm that a card appears in the channel.

---

## What Appears in Teams

Each run posts a card carrying the broadcast name, the snapshot images, and an **Update broadcast settings** button that opens that broadcast back in OptiSigns.

---

## Troubleshooting and FAQs

#### **It's saying "Enter a valid URL starting with https://".**

Paste the complete URL copied from Teams. A truncated copy, or the old outlook.office.com/webhook/... connector URL, will be rejected.

#### **Run history shows the Teams delivery failed.**

The workflow may have been turned off or deleted, or its owner may have lost access to the channel. Open **Workflows** in Teams, confirm the workflow is **On**, or create a new one and update the URL in the broadcast.

#### **No card appeared, but the run succeeded.**

Check that you're looking at the channel chosen when the workflow was created, and that the workflow wasn't later edited to post somewhere else.

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
