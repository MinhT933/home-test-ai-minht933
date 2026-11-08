# Inbound Webhook DataSources in Designer

Article URL: https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer

### In this article, we'll create an Inbound Webhook DataSource in Designer, send data to it from your own app or automation, and show that data on your screens.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#WhatYoullNeed)
* [How It Works](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#HowItWorks)
* [Create an Inbound Webhook DataSource](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#CreateAnInboundWebhookDataSource)
  + [Open the DataSource panel](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step1OpenTheDataSourcePanel)
  + [Choose Inbound Webhook](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step2ChooseInboundWebhook)
  + [Name it and pick a display mode](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step3NameItAndPickADisplayMode)
  + [Copy your Webhook URL](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step4CopyYourWebhookURL)
  + [Detect your payload (optional)](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step5DetectYourPayloadOptional)
  + [Put the data on your design](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Step6PutTheDataOnYourDesign)
* [Send Data to Your Webhook](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#SendDataToYourWebhook)
  + [What POST and PUT do](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#WhatPOSTAndPUTDo)
  + [Set an expiry on individual rows](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#SetAnExpiryOnIndividualRows)
  + [Send the key in a header](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#SendTheKeyInAHeader)
  + [Limits](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Limits)
* [Change or Reopen a Webhook](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#ChangeOrReopenAWebhook)
* [Troubleshooting](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Troubleshooting)
* [Related Articles](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#RelatedArticles)

Most DataSources in Designer go out and fetch your data on a schedule. An **Inbound Webhook** works the other way round. Your own system sends data to a private URL the moment something happens, and your screens show it within seconds. You don't need a spreadsheet, a polling interval or a manual refresh.

This is the preferred option for people who want an immediate update. Simply set up a webhook that fires on your end, then any changes to your Data will refresh within OptiSigns and on your screens rapidly.

---

## What You'll Need

* An OptiSigns **Pro Plus** or **Enterprise** plan. Inbound Webhooks are part of [Dynamic Data Mapping](https://support.optisigns.com/hc/en-us/articles/29217646663187-How-to-Set-Up-Dynamic-Data-Mapping-with-OptiSync).
* A design open in [Designer](https://support.optisigns.com/hc/en-us/articles/42087942047379).
* A system that can send an HTTP POST or PUT API request with a JSON body

---

## How It Works

When you create an Inbound Webhook DataSource, Designer gives you a private **Webhook URL**. Anything that can send an HTTP POST request can use it: Zapier, Make, Shopify, a point-of-sale system, or a script you write yourself. Each request carries JSON, and that JSON becomes rows in the DataSource. You show those rows on screen with a Repeater, the same way you would with any other DataSource.

Each Inbound Webhook DataSource runs in one of two display modes. You choose the mode when you create the DataSource.

* **State** - Replace the whole value each time. Every request overwrites what was there before, and nothing expires on its own. Use it for things that have one current value, such as a KPI, a total, a menu, a roster or a scoreboard.
* **Event** - Append each row. Every request adds to the feed, and every row expires automatically after a set time. Use it for things that happen, such as new orders, alerts, check-ins or a "now serving" number.

|  |
| --- |
| **IMPORTANT** |
| Display mode is fixed once the DataSource exists. To use the other mode, create a new DataSource. |

---

## Creating an Inbound Webhook DataSource

### Open the DataSource Panel

In Designer, click **DataSource** in the left-side menu to open the **DataSources** panel, then click **Add DataSource**.

![DataSources panel in Designer with the Add DataSource button highlighted](https://support.optisigns.com/hc/article_attachments/55719323519763)

### Choose Inbound Webhook

Under **Nested, JSON format**, choose the **Inbound Webhook** card ("Push data in from any app or automation that can POST").

![Add DataSource picker with the Inbound Webhook card under Nested, JSON format highlighted](https://support.optisigns.com/hc/article_attachments/55747033217427)

### Name the DataSource and Pick a Display Mode

Enter a **DataSource Name**.

Under "Display Mode", choose **State** or **Event**.

If you chose **Event**, set how the feed behaves:

* **Keep at most** - The most rows the feed keeps, 20 by default. When a new row arrives and the feed is full, the oldest row is dropped. The limit is 200.
* **Default expire after** - How many minutes a row stays live before it expires, 30 by default. This can be anywhere from 1 minute to 24 hours. A single row can override it (see [Set an expiry on individual rows](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#SetAnExpiryOnIndividualRows)).

Then, click **Generate Webhook**.

![Add DataSource form with a name, Event mode, Keep at most and Default expire after, and the Generate Webhook button](https://support.optisigns.com/hc/article_attachments/55719323702163)

### Copy your Webhook URL

Designer creates the DataSource and shows the **Webhook URL (key included)** and the **Key**. Copy it with the copy icon and paste it into the system that will send the data. The URL will look like this:

```
https://smallapp.optisigns.com/api/request-apis/dataSourceDatas/<DataSource ID>/webhook?key=<your key>
```

![Generated Webhook URL and Key, blurred, with the URL copy icon highlighted](https://support.optisigns.com/hc/article_attachments/55719362187283)

|  |
| --- |
| **IMPORTANT** |
| Treat this URL like a password. Anyone who has it can send data to this DataSource. If it leaks, click the regenerate icon next to the **Key** and confirm **Regenerate**. The old link stops working immediately, and your column mapping and existing rows are kept. |

![Regenerate key confirmation dialog warning that the current link stops working, with the Regenerate button](https://support.optisigns.com/hc/article_attachments/55747023353875)

### Detect your Payload (optional)

Designer needs to know which fields your data contains before you can place them on the canvas. Under **Detect Payload (Optional)**, do one of these:

* **Listen for a delivery** - Click it, then send one real request from your system. Designer reads the fields from what arrives.
* **Paste sample JSON** - Click it, paste an example of your payload into the box, then click **Detect columns**.

Designer lists what it found under **Detected fields (example values)**. You can run either option again later (**Listen again to add fields** or **Re-detect columns**) to pick up new fields. New fields are added to the ones Designer has already seen, so your existing mapping stays in place.

![Detect Payload with sample JSON pasted and the detected fields order, customer and status listed](https://support.optisigns.com/hc/article_attachments/55719345210899)

Click **Save** to finish.

### Put the Data on your Design

Drag a field from the DataSource card onto the canvas. Designer asks whether to use the data in a Repeater or on its own. Choose **Use in a Repeater** so the design creates one item per row. **Use on its own** places a single value instead.

![Dialog asking whether to use the dragged field in a Repeater or on its own, with Use in a Repeater highlighted](https://support.optisigns.com/hc/article_attachments/55747002517139)

Save the design and push it to your screens. For more on laying out repeated data, see [How to Set Up Dynamic Data Mapping with OptiSync](https://support.optisigns.com/hc/en-us/articles/29217646663187).

---

## Send Data to Your Webhook

Send JSON to your Webhook URL with the `Content-Type: application/json` header. A screen picks up a change within about 20 seconds.

### What POST and PUT Do

What each request does depends on the display mode:

* **Event mode**
  + **POST** - Adds one row. Send a list (a JSON array) to add several rows at once.
  + **PUT** - Replaces every row with the rows you send.
  + PUT with an empty body - Removes every row. Send {}, [] or {"data": []}.
* **State mode**
  + **POST** or **PUT** - Either one replaces the current values. Any field you leave out is cleared.

For example, this request adds one order to an Event feed:

```
curl -X POST "https://smallapp.optisigns.com/api/request-apis/dataSourceDatas/<DataSource ID>/webhook?key=<your key>" \
  -H "Content-Type: application/json" \
  -d '{"order": "1042", "customer": "Sam", "status": "Ready"}'
```

To add several rows in one request, send a JSON array:

```
[
  {"order": "1042", "status": "Ready"},
  {"order": "1043", "status": "Preparing"}
]
```

To replace every row with `PUT`, you can send an array like the one above, or wrap it as `{"data": [ ... ]}`.

|  |
| --- |
| **NOTE** |
| With `POST`, a body shaped `{"data": [ ... ]}` is treated as one row with a field called `data`. To send several rows with `POST`, send a plain array. |

### Set an expiry on individual rows

In Event mode, each row expires after the DataSource's **Default expire after** time. To give one row its own lifetime, add `__opti_ttl` with a number of seconds:

```
{"alert": "Lane 3 closed", "__opti_ttl": 300}
```

This row expires after 5 minutes, whatever the default is. The shortest expiry is 60 seconds. `__opti_ttl` is used to work out the expiry and isn't stored as a column.

Expired rows stop showing on your screens. In Designer they stay on the DataSource card, marked **(expired)**. To check which rows are live, open the DataSource's **⋮** menu and choose **Edit Data**. The **Status** column shows **Live** or **Expired** for each row. This view is read-only, because the data comes from your sender.

![Edit Data grid for a webhook DataSource with a Status column showing one Expired row and one Live row](https://support.optisigns.com/hc/article_attachments/55747013126419) When a feed has no live rows left, your screens follow the DataSource's **Empty Data Handling** setting.

|  |
| --- |
| **TIP** |
| Avoid naming your own fields with the `__opti_` prefix. That prefix is reserved for OptiSigns, so fields that use it are not shown in Designer. |

### Send the key in a header

The URL Designer gives you carries the key in the query string (`?key=...`). If your sender lets you set custom headers, you can remove `?key=...` from the URL and send the key in an `X-Webhook-Key` header instead. Web servers and tools often log full URLs, so keeping the key out of the URL means it won't end up in those logs.

```
curl -X POST "https://smallapp.optisigns.com/api/request-apis/dataSourceDatas/<DataSource ID>/webhook" \
  -H "X-Webhook-Key: <your key>" \
  -H "Content-Type: application/json" \
  -d '{"order": "1042", "status": "Ready"}'
```

### Limits

Your webhook checks every request against these limits. They aren't shown in Designer.

* **Rows** - A feed holds up to 200 rows, or fewer if you set a lower **Keep at most**.
* **Request size in Event mode**
  + **One row** - Up to 64 KB per request.
  + **A list of rows, or any PUT** - Up to 256 KB per request, with each row still up to 64 KB.
* **Request size in State mode** - Up to 256 KB per request.
* **Rate** - Up to 120 requests per minute for each webhook.

For scale, a typical e-commerce order notification is 10 to 40 KB, so one order fits comfortably in a single row.

A request over a limit is rejected as a whole, and nothing from it is saved. Rows are never cut off partway.

|  |
| --- |
| **IMPORTANT** |
| A payload that passes **Detect columns** or **Listen for a delivery** can still be too large to deliver. Check your real payload size against the limits above, especially for large records such as full e-commerce orders. |

---

## Change or Reopen a Webhook

To see your Webhook URL again, change the name, or change Event settings, open the **DataSources** panel and click your DataSource to open its card. Click the **⋮** menu on the card and choose **Edit Settings**.

![Inbound Webhook DataSource card with its menu open and Edit Settings highlighted](https://support.optisigns.com/hc/article_attachments/55719345281811)

---

## Troubleshooting

In this section, we'll address some of the more common issues you might run into when using Inbound Webhooks in Designer.

#### My system got a success response, but nothing changed in Designer.

Designer doesn't refresh its view of a DataSource on its own. Open the DataSource's **⋮** menu and choose **Refresh data (in Design Mode only)**, or reload the page. Your screens update on their own.

#### The DataSource says "This feed is empty. Send a POST to this webhook URL to fill it."

Nothing has arrived yet, or the feed was cleared by a `PUT` with an empty body. Check that your sender is using the current Webhook URL.

#### Rows are listed in Designer but don't show on the screen.

The rows have expired. Check **Default expire after** and any `__opti_ttl` values you send. If a value like a menu or a KPI keeps disappearing, it was probably built in Event mode, where every row expires by design. Create a new DataSource in **State** mode for it.

#### I see duplicate rows.

When a sender retries a request, each retry adds a row. To prevent duplicates, send a unique `X-Request-Id` header with each request. Shopify webhooks are recognized automatically by their `X-Shopify-Webhook-Id` header.

#### My sender gets an error.

The status code will you why:

* **401 Unauthorized** - The key is wrong, or it was regenerated. Copy the current URL from **Edit Settings**.
* **404 Not found** - The DataSource ID in the URL is wrong, or the DataSource was deleted.
* **413 Payload too large** - The request is over the size limit for its type. See [Limits](https://support.optisigns.com/hc/en-us/articles/55719322614803-Inbound-Webhook-DataSources-in-Designer#Limits).
* **429 Too many requests** - You sent more than 120 requests in a minute. Slow down, or send several rows in one request instead.
* **400** - The body isn't valid JSON, isn't a shape the webhook accepts, or has more rows than the feed can hold.
* **503 Inbound Webhook is temporarily disabled** - The service is paused on our side. Try again later, and contact support if it continues.

---

## Related Articles

* [Widgets in Designer](https://support.optisigns.com/hc/en-us/articles/42436941395475)
* [How to Set Up Dynamic Data Mapping with OptiSync](https://support.optisigns.com/hc/en-us/articles/29217646663187)
* [How to add Google Sheets as a DataSource for OptiSync](https://support.optisigns.com/hc/en-us/articles/29838866920211)

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
