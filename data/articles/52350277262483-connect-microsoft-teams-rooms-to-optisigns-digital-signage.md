# Connect Microsoft Teams Rooms to OptiSigns Digital Signage

Article URL: https://support.optisigns.com/hc/en-us/articles/52350277262483-Connect-Microsoft-Teams-Rooms-to-OptiSigns-Digital-Signage

Turn idle Microsoft Teams Rooms into digital signage. When a room is between meetings, OptiSigns plays your assigned content — announcements, dashboards, branding, menus — right on the room display, and clears it the instant a meeting starts.

This guide covers the **two ways to connect a Teams Room to OptiSigns**, so you can pick the one that fits how your organization works.

---

## Two ways to connect

|  | **Signage URL**  ·  *Recommended, fastest start* | **Service Principal** |
| --- | --- | --- |
| **What it gives you** | Get content on a room in minutes — no app registration. | OptiSigns **discovers and lists all your Teams Rooms** (model, online/offline, health) in one place. |
| **Microsoft setup** | None in Azure. You paste a URL in the Teams Rooms portal. | An Entra admin registers a read-only app and grants two permissions. |
| **Best for** | Getting started, a few rooms, or when you can't register an Azure app. | Managing a fleet of rooms and seeing their status alongside your other screens. |
| **Who can set it up** | A Teams Rooms admin. | A Microsoft **Entra (Azure AD) admin**, one time. |

> **Important — read this first.** Microsoft does **not** offer a way for apps to push content to Teams Rooms automatically. So with **either** method, the final step is a **one-time manual paste** of an OptiSigns signage URL into the Teams Rooms portal. The **Service Principal** method doesn't push content for you — it gives OptiSigns *visibility* into your rooms. Many teams use **both**: Service Principal to see every room, and Signage URLs to deliver the content.

---

## What you'll need

* **An OptiSigns account** on a plan that includes device management (MDM / room integrations), with the **Owner** or **Super Admin** role. [Start a free trial](https://www.optisigns.com/free-trial) — you only pay for rooms you activate signage on.
* **Microsoft Teams Rooms Pro.** Digital signage is a **Teams Rooms Pro** capability — rooms on Teams Rooms **Basic** can't display signage.
* At least one **Teams Room that's online and signed in**.
* **For the Service Principal method only:** a Microsoft **Entra (Azure AD) Global Administrator** who can register an app and grant admin consent.

---

## How it works

OptiSigns generates a secure **signage URL** for each screen you want to show on a room. Microsoft's Teams Rooms Pro platform has a built-in **Digital signage** feature that can display a custom URL while the room is idle. You paste the OptiSigns URL there once; from then on the room plays whatever you assign in OptiSigns, and updates are live.

When a meeting starts — or someone wakes the room — the display returns to the normal Teams Rooms UI automatically, and signage resumes when the room goes idle again. There's no impact on meeting quality, audio/video, or scheduled meetings.

---

## Open the Teams Rooms page

In OptiSigns, open **Devices** in the top navigation, then in the left sidebar under **Room Integrations**, click **Teams Rooms**. If you haven't connected yet, you'll see the two methods side by side.

![OptiSigns Teams Rooms — the two ways to connect: Signage URL (recommended) and Service Principal](https://support.optisigns.com/hc/article_attachments/54863307377299)

Pick your method below.

---

# Method 1 — Connect with a Signage URL (recommended)

No Azure setup. You'll mint a URL in OptiSigns, give it content, and paste it into the Teams Rooms portal.

### Step 1 — Mint a Signage URL

On the **Signage URL** card, click **Mint URLs** (shown above).

In the **New Signage URL** dialog, give the URL a **Name** (for example, your room or location — `Atlanta Lobby`). The optional **Target label** is just a note to help you remember where you'll paste it; it doesn't control anything. Click **Next**.

![The New Signage URL dialog — name the URL, then click Next](https://support.optisigns.com/hc/article_attachments/54863298194195)

### Step 2 — Assign content

Clicking **Next** creates the URL and opens the **Signage URLs** tab (the page now shows **Connected · Signage URLs only**). On the new row, click **+ Assign content**.

In the **Assign content** dialog, choose a **Content Type** — **Asset**, **Playlist**, or **Schedule** — then pick the specific item to play. Click **Save**.

![The Assign content dialog — pick a Content Type, choose the item, then Save](https://support.optisigns.com/hc/article_attachments/54863350797331)

OptiSigns copies the new signage URL to your clipboard and shows the paste instructions. (You can reopen them any time with **Show me how to paste** on the Signage URLs tab.)

### Step 3 — Paste the URL into the Teams Rooms portal

In the **Paste your Signage URL in Teams Rooms portal** dialog, click **Open Teams Admin Portal**. Then, in Microsoft's portal:

1. Sign in and open **Digital signage**.
2. Click **Add source** and give it a clear name (matching your room or group).
3. Choose **Custom URL**, paste the OptiSigns URL, then **Review → Finish**.
4. Select the new source → **Assign to devices** → pick your Teams Room(s) → **Apply**.

![The paste-instructions dialog — copy the URL, then click Open Teams Admin Portal](https://support.optisigns.com/hc/article_attachments/54863314048403)

Within about 30 seconds the room fetches the URL and your content appears during idle. Start a test meeting — content should clear instantly when the meeting connects.

> Repeat Steps 1–3 to mint a URL for each room or room group. You manage all minted URLs (and reassign their content any time) under the **Signage URLs** tab.

---

# Method 2 — Connect with a Service Principal

This connects a **read-only** Microsoft Entra app so OptiSigns can discover and list all your Teams Rooms automatically — model, online/offline status, and device health — alongside your other screens. (You'll still deliver content with a signage URL — see "Put content on a room" below.)

> **Do it in this order: register the app → grant admin consent → *then* connect OptiSigns.** That isn't the intuitive order, and it matters. **Test Connection** validates your credentials, not your permissions, so it can pass on an app that hasn't been consented yet. On top of that, Microsoft caches access tokens for about an hour — connect before consenting and the cached token stays permission-less, so syncing keeps failing for up to an hour after you've actually fixed it. Consent first and you avoid both traps.

### Step 1 — Register the application

Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com) as a **Global Administrator** and go to **Identity → Applications → App registrations → + New registration**.

![Register an application — name the app, choose Single tenant, leave Redirect URI blank, then Register](https://support.optisigns.com/hc/article_attachments/54863314201107)

* **Name** — anything you like; pick something a future admin will recognise, for example `OptiSigns Teams Rooms`.
* **Supported account types** — **Single tenant**. Your rooms live in your own tenant.
* **Redirect URI** — **leave it blank.** This app authenticates service-to-service, so there's no browser redirect.

Click **Register**.

### Step 2 — Copy the two IDs

You land on the app's **Overview** page. Copy these two values — you'll paste them into OptiSigns at the end:

![The app Overview page with Application (client) ID and Directory (tenant) ID highlighted](https://support.optisigns.com/hc/article_attachments/54863351234835)

* **Application (client) ID**
* **Directory (tenant) ID**

Ignore the **Object ID**. OptiSigns doesn't use it, and it's easy to grab by mistake because it sits between the two you do need.

### Step 3 — Add a permission

In the app's left menu, open **API permissions → + Add a permission**. In the panel that opens, choose **Microsoft Graph**.

![The Request API permissions panel with Microsoft Graph selected](https://support.optisigns.com/hc/article_attachments/54863351394707)

### Step 4 — Application permissions, then TeamworkDevice.Read.All

![Choosing Application permissions, then searching for and ticking TeamworkDevice.Read.All](https://support.optisigns.com/hc/article_attachments/54863299150099)

1. When Microsoft asks **"What type of permissions does your application require?"**, choose **Application permissions** — **not** Delegated permissions. Delegated means "act as the signed-in user", and there is no signed-in user here: OptiSigns reads your inventory as a background service. Choosing Delegated is the most common mistake, and it fails silently later.
2. In the search box, type **`TeamworkDevice.Read.All`**.
3. Tick its checkbox. The description reads *Read Teams devices*, and **Admin consent required** says **Yes** — that matters in the next step.
4. Click **Add permissions**.

> `TeamworkDevice.Read.All` is the only required permission. You can optionally add `CrossTenantInformation.ReadBasic.All`, which lets OptiSigns display your tenant's name in the console — everything works without it.

### Step 5 — Adding a permission is not the same as granting it

Your permission is now listed, but look at the **Status** column:

![The permission list showing TeamworkDevice.Read.All with the status Not granted](https://support.optisigns.com/hc/article_attachments/54863338686867)

**⚠ Not granted for <your tenant>.**

The permission has been *requested*, not *approved*. In this state Microsoft still issues OptiSigns an access token — it simply carries no privileges, so every attempt to read your rooms returns **403 Forbidden**. Nothing about the app registration looks broken; it just doesn't work.

Click **✓ Grant admin consent for <your tenant>** and confirm.

> If that button is greyed out, your account isn't a **Global Administrator** or **Privileged Role Administrator**. You'll need someone who is — an app can't consent to itself.

### Step 6 — Confirm the consent took

Give it a moment, then check the **Status** column again. This is what correct looks like:

![The permission list showing Granted for the tenant, with green check marks](https://support.optisigns.com/hc/article_attachments/54863338849811)

A green banner reading **"Successfully granted admin consent for the requested permissions"**, and `TeamworkDevice.Read.All` showing **Granted for <your tenant>**.

Don't move on until you see it. Consent takes about a minute to propagate.

### Step 7 — Create a client secret

Open **Certificates & secrets → Client secrets → + New client secret**. Give it a description and an expiry, then **Add**.

![The client secret row, with the Value column highlighted next to the Secret ID](https://support.optisigns.com/hc/article_attachments/54863322414227)

Copy the **Value** — the long string in the *Value* column. **Not** the *Secret ID* beside it. The two sit side by side and look equally cryptic, and pasting the Secret ID is the second most common mistake here.

> **Microsoft shows the Value once.** Navigate away without copying it and it's gone for good — you'll have to delete the secret and create a new one. Note the expiry date too: when a secret expires the connection stops working, and the fix is a new secret plus a reconnect.

### Step 8 — Connect it in OptiSigns

Back on the OptiSigns **Teams Rooms** page, on the **Service Principal** card, click **Add Service Principal**.

![The Add Microsoft Service Principal dialog filled in, showing Connection successful](https://support.optisigns.com/hc/article_attachments/54863315258387)

Fill in four fields:

* **Name** — any label you'll recognise (for example, `Contoso Teams SP`)
* **Application (client) ID** — from Step 2
* **Directory (tenant) ID** — from Step 2
* **Client Secret** — the **Value** from Step 7

Click **Test Connection**. OptiSigns validates the credentials against Microsoft Graph and shows **Connection successful** — then **Save** lights up. Click **Save**.

Within a few minutes your Teams Rooms appear in the **Devices** tab, each with its model and live online/offline status.

### Put content on a room

Discovering rooms doesn't put content on them — that still uses a signage URL. From the **Signage URLs** tab, click **New Signage URL** and follow **Method 1, Steps 1–3** above to mint a URL, assign content, and paste it into the Teams Rooms portal for that room.

---

## Licensing

Activating signage on a Teams Room uses **one screen license** from your OptiSigns pool — the same licenses you use for any other screen. Discovered rooms that you haven't activated are free; you're only billed for rooms you turn signage on for. [See full pricing →](https://www.optisigns.com/pricing)

---

## Troubleshooting

**My rooms show signage, but OptiSigns lists no devices.** Expected — and it tells you exactly where the problem is. Signage delivery uses the signage URL and never touches Microsoft Graph; device inventory uses the Service Principal and does. Signage working proves nothing about the Service Principal. Go to **Step 5** above and check the **Status** column on the app's API permissions page.

**The sync failed, or the connection shows "Reconnect required".** Behind the scenes Microsoft is returning:

```
403 Forbidden — Missing role permissions on the request.
API requires one of 'TeamworkDevice.Read.All, TeamworkDevice.ReadWrite.All'.
Roles on the request ''.
```

Read that last part — `Roles on the request ''` — as: *the token is valid and it carries no permissions.* Your client ID, tenant ID and secret are all fine. Either admin consent is missing, or the permission was added under **Delegated** instead of **Application**. Fix it in three steps, and do all three:

1. In Entra, confirm `TeamworkDevice.Read.All` sits under **Application permissions**, then click **Grant admin consent** and wait for the green check.
2. In OptiSigns, click **Disconnect** on the Teams Rooms page.
3. Click **Add Service Principal** again and re-enter the same three values.

Step 3 isn't optional: a connection that has failed is parked in an errored state, and fixing the permission in Entra doesn't reach back and revive it. Reconnecting is what puts it back to work.

**"Test Connection" passed, but the sync still fails.** Two possibilities. Either consent came *after* the connection — access tokens are cached for about an hour, so a token minted before consent stays permission-less until it expires; grant consent, reconnect, and if it still fails wait an hour and retry. Or the permission is **Delegated** rather than **Application** — check the **Type** column on the API permissions page; it must read *Application*.

**"Test Connection" fails with "Invalid client credentials."** Re-check the Application (client) ID, Directory (tenant) ID, and Client Secret — copy them exactly from the Entra app, and make sure you copied the secret's **Value**, not its **Secret ID**. If the secret has expired, create a new one in **Certificates & secrets** and paste the new value.

**"No Teams Rooms found in your tenant."** If the connection is healthy — no "Reconnect required" badge and the **Sync now** button is clickable — this means what it says: Microsoft Graph returned zero signage-eligible rooms. In the Teams admin center, confirm you have Teams Rooms devices enrolled and that they carry a **Teams Rooms Pro** license. If the connection shows **Reconnect required** and **Sync now** is greyed out, ignore this message — the sync never ran; see the entry above.

**I pasted the URL but nothing shows on the room.** Confirm the room is **online** and licensed for **Teams Rooms Pro** (Basic doesn't include digital signage). Make sure you pasted the full URL (it begins with `https://`) as a **Custom URL** source, and that the source is **assigned to that device** in the Teams Rooms portal.

**Content shows but doesn't clear when a meeting starts.** This is controlled by the Teams Rooms digital-signage setting in Microsoft's portal — confirm signage is set to display only while the room is idle.

**The Teams Rooms portal says the URL is invalid.** The URL may have been truncated on copy. Return to the OptiSigns **Signage URLs** tab, click **Copy** on that URL again, and re-paste.

---

## Need help?

* Email: [support@optisigns.com](mailto:support@optisigns.com)
* More guides: [support.optisigns.com](https://support.optisigns.com)
* Related: [Connect Zoom Rooms to OptiSigns](https://support.optisigns.com/hc/en-us/articles/52069065128723-Connect-Zoom-Rooms-to-OptiSigns-Digital-Signage) · [Connect Cisco Webex Rooms to OptiSigns](https://support.optisigns.com/hc/en-us/articles/51343184586643-Connect-Cisco-Webex-Rooms-to-OptiSigns-Digital-Signage)
