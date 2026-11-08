# Connect SharePoint News to OptiSigns Digital Signage

Article URL: https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage

### In this article, we'll connect a Microsoft SharePoint site so its news posts display on your OptiSigns screens.

* [What you'll need](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#WhatYoullNeed)
* [Which connection method to use](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#WhichConnectionMethodToUse)
* [How it works](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#HowItWorks)
* [Setting Up the App](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#Step1AddTheApp)
  + [If you chose Direct Login](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#IfYouChoseDirectLogin)
  + [If you chose Use Service Principal](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#IfYouChoseUseServicePrincipal)
* [(Optional) Set up a Service Principal, or reuse the one you have](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#Step4SetUpAServicePrincipalOrReuseTheOneYouHave)
* [Test the connection](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#Step6TestTheConnection)
* [Appearance settings](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#AppearanceSettings)
* [Post settings](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#PostSettings)
* [Licensing](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#Licensing)
* [Troubleshooting](https://support.optisigns.com/hc/en-us/articles/55450681344915-Connect-SharePoint-News-to-OptiSigns-Digital-Signage#Troubleshooting)

Put your intranet on the wall. SharePoint News reads the news posts already published on a Microsoft SharePoint site and displays them on your screens, refreshing on its own as your team publishes.

---

## What you'll need

* An OptiSigns account on the [**Standard** plan or above](https://www.optisigns.com/pricing).
* A Microsoft SharePoint site with news posts on it
* The **site URL**, in the form `https://yourtenant.sharepoint.com/sites/YourSite`
* **Service Principal method only:** An **Azure Service Principal** saved (or ability to be created) in OptiSigns, and administrator access to the Azure Portal to grant it permission to read SharePoint

---

## Which connection method to use

SharePoint News offers two ways to connect, and you choose between them in the app itself under **Choose Authentication Method**.

* **Direct Login Method** - This connects you through a single person's Microsoft Account. This is best for getting started quickly, or a single SharePoint site that one person owns.
* **Service Principal Method** - This connects you through a Service Principal, which is an application belonging to a larger organization. This is best for anything long-lived or needing security permissions, and allows your site to keep working even if staff change roles, change passwords, or leave.

|  |
| --- |
| **IMPORTANT** |
| **Direct Login** is selected by default. If you want the Service Principal method, you must switch to it — and setting it up is done by a Microsoft tenant administrator, not by an individual user. If you do not administer your organisation's Microsoft tenant, send this article to whoever does. |

---

## How it works

OptiSigns reads your SharePoint site through the Microsoft Graph API. With a Service Principal, it connects as a dedicated application identity in your Microsoft tenant rather than as any one person's account. With Direct Login, it connects as the person who signed in.

The permissions involved are **read-only** in both cases. OptiSigns never writes to SharePoint, never posts, and never changes a file. It just lets you display them on your digital signs.

---

## Setting Up the App

In OptiSigns, go to **Files/Assets**, select **Apps**:

![The Files/Assets page with the Apps button that opens the app picker](https://support.optisigns.com/hc/article_attachments/55453725559571)

Choose **SharePoint News**.

![Apps dialog searched for SharePoint, with the SharePoint News tile highlighted](https://support.optisigns.com/hc/article_attachments/55450681489939)

Give the news wall a **Name**, then paste the **SharePoint Site URL**. It must be the address of the site itself, not of a page or a post inside it:

https://yourtenant.sharepoint.com/sites/YourSite

To find it, open the site in your browser and copy the address up to and including the site name, discarding anything after it.

![Browser address bar showing a SharePoint site URL ending in /sites/Demo01](https://support.optisigns.com/hc/article_attachments/55450681586195)

![SharePoint News config with Name and SharePoint Site URL filled in, beside Test Connection](https://support.optisigns.com/hc/article_attachments/55450678578451)

|  |
| --- |
| **NOTE** |
| There is no site picker — the pasted URL is the only way to choose a site. This is deliberate: under the `Sites.Selected` permission most organizations use, the app is not allowed to list the sites in your tenant at all. |

Under **Choose Authentication Method**, pick **Direct Login** or **Use Service Principal**.

![Choose Authentication Method showing Use Service Principal and Direct Login options](https://support.optisigns.com/hc/article_attachments/55450681756691)

### If you chose Direct Login

Select **Sign in with Microsoft** and complete the Microsoft sign-in. Once connected, the button
changes to **Authorized with Microsoft as** .

The news wall then reads SharePoint as that person. It keeps working until that account's password or sign-in policy changes, at which point the app asks you to reconnect.

![Direct Login selected, showing the Sign in with Microsoft button](https://support.optisigns.com/hc/article_attachments/55451544297619)

|  |
| --- |
| **NOTE** |
| Sign in with an account that can already open the site. Direct Login grants OptiSigns no access the person does not already have. |

Skip to **Test the connection**.

### If you chose Use Service Principal

Continue reading.

---

## (Optional) Set up a Service Principal, or reuse one you have

A Service Principal is an Azure app registration saved to your OptiSigns account.

To create one:

* Copy its **Application (client) ID** and **Directory (tenant) ID.**
* Create a client secret
* Save it in OptiSigns under **Settings → Integrations → Power BI → Add Azure Service Principal**

This is the same for any OptiSigns Service Principal integration. See [How to Set Up a Power BI Service Principal for Use in OptiSigns](https://support.optisigns.com/hc/en-us/articles/32860569148819-How-to-Set-Up-a-Power-BI-Service-Principal-for-Use-in-OptiSigns) for more.

![The Integrations page, Power BI tab, with the Add Azure Service Principal button](https://support.optisigns.com/hc/article_attachments/55453742263699)

Follow the sections **Create an Entra App in Microsoft Azure** and **Authenticating OptiSigns via Service Principal** in that article, then return here.

![Which Azure value goes in which OptiSigns field: client ID, tenant ID, and the secret Value — not the Secret ID](https://support.optisigns.com/hc/article_attachments/55452331655955)

|  |
| --- |
| **TIP** |
| If your organization already uses a Service Principal for Power BI, **reuse it**. The integration list in SharePoint News offers every Azure Service Principal saved on the account, whatever it was originally created for. You only need to add the SharePoint permission below.  **NOTE:** Skip the Power BI article's **Enable Power BI Service Admin Settings** and **Add the Service Principal to a Workspace** sections. Those configure Power BI itself and are not needed for SharePoint. Note also that SharePoint News is available on **Standard** and above, not Enterprise only. |

Next, give that Service Principal permission to read SharePoint.

In the **Azure Portal**, open your app registration, go to **API permissions**, select **Add a permission**, choose **Microsoft Graph**, then **Application permissions**.

Add either of these, depending on what your organization's policy allows:

![The Azure permission-type choice: Delegated permissions versus Application permissions](https://support.optisigns.com/hc/article_attachments/55453742174611)

| Permission | What it grants |
| --- | --- |
| `Sites.Selected` | Read only the specific sites you later grant access to. The narrower option — prefer it if your policy allows. |
| `Sites.Read.All` | Read any SharePoint site in the tenant. |

![Azure API permissions with Microsoft Graph Sites.Read.All added as an application permission](https://support.optisigns.com/hc/article_attachments/55453702633107)

|  |
| --- |
| **NOTE** |
| If you choose `Sites.Selected`, the permission alone is not enough — the application must also be granted access to the particular site you want to display, which your Microsoft administrator does per site. Without it, **Test Connection** reports that the Service Principal authenticated but has no access to that site. |

Still on **API permissions**, select **Grant admin consent for <your organization>**. The **Status** column must read **Granted** before the connection will work.

![Azure API permissions showing the Status column reading Granted for the organisation](https://support.optisigns.com/hc/article_attachments/55450665542419)

Now pick your Service Principal from **Select the Service Principal Integration**.

![The Select the Service Principal Integration field with an integration chosen](https://support.optisigns.com/hc/article_attachments/55450695938195)

|  |
| --- |
| **NOTE** |
| Integrations belong to a **Teamspace**. The list shows the Service Principals saved on the team that owns this news wall — if yours is missing, check which team you created it on. When the team has none saved, the app shows **Set up a Service Principal integration for this team** instead of the list, and **Save** stays disabled. |

---

## Test the connection

Select **Test Connection**, beside the **SharePoint Site URL** field. A green tick on the button means OptiSigns reached the site and could read its posts; a warning triangle means it could not. Resolve any error before saving — the messages are listed under **Troubleshooting**.

![Success toast reading Connected to Demo01 after Test Connection](https://support.optisigns.com/hc/article_attachments/55453698231315)

**Save**, then add the news wall to a playlist or assign it to a screen as you would any other app.

![The configuration dialog footer with the Save button](https://support.optisigns.com/hc/article_attachments/55453742353811)

---

## Appearance settings

Open the **Appearance** section of the configuration dialog.

![The Appearance section expanded, showing Display Mode, Theme, Font Size and the toggles](https://support.optisigns.com/hc/article_attachments/55451529071507)

* **Display Mode** - Choose your display mode. Decide between Default, Single Post, or Modern layout.
* **Theme** - Choose between Light, Dark, or Custom themes. Choosing Custom will add numerous options that let you change the colors on your theme.
* **Font Size** - Choose your Font Size. Default is 20, Custom lets you choose.

  ![The Font Size dropdown open, showing the Default and Custom options](https://support.optisigns.com/hc/article_attachments/55451691334931)
* **Show QR Code** - When checked, will show a QR code linking to the full post on SharePoint.
* **Show Banner Image** - When checked, will show each post's banner image.
* **Company Logo** - Lets you upload your company logo to be shown alongside each post.

|  |
| --- |
| **NOTE** |
| Two of the color pickers depend on **Display Mode** as well as **Theme**. **Accent Colour** is hidden in **Single Post**, and **Secondary Color** is hidden in both **Single Post** and **Modern**. |

---

## Post settings

Open the **Post Settings** section.

![The Post Settings section showing Number of Posts, Max Age of Posts and Post Duration](https://support.optisigns.com/hc/article_attachments/55451529178771)

* **Number of Posts** - Choose how many total posts the asset will cycle through.
* **Max Age of Posts** - Choose how old the posts that can display will be.
* **Post Duration** - Shows how long each post will stay on the screen before cycling to another post.

Under **Advanced**, **Refresh Interval** sets how often OptiSigns checks SharePoint for new posts, in seconds (default 3600 — once an hour).

![The Advanced section showing Refresh Interval set to 3600 seconds](https://support.optisigns.com/hc/article_attachments/55451552534803)

---

## Troubleshooting and FAQs

Here, we'll go over error messages you might receive when trying to set up SharePoint on OptiSigns. What they mean, and how to solve them.

#### "Connected — no posts yet; new ones appear automatically."

The connection works, but the site has no news posts. Publish one in SharePoint and it will appear on the next refresh.

#### "Connected — all N posts are older than the 30-day Max Age; none will show. Raise Max Age of Posts."

The connection works, but every post is older than the **Max Age of Posts** setting. Raise it under **Post Settings**. On the screen itself this shows as "No SharePoint posts from the last 30 days are currently available."

#### "Connected — news list unavailable right now; it retries automatically."

A temporary SharePoint problem. No action needed.

#### "The Service Principal authenticated, but does not have access to that site. Ask your Microsoft admin to grant it access to this specific SharePoint site."

The application identity is valid but was never granted access to this particular site. This is the expected result of using `Sites.Selected` without also granting site access. Make sure your admin account within Azure has access to the requested SharePoint site.

#### "This Microsoft account does not have access to that SharePoint site."

The Direct Login equivalent of the message above. Sign in with an account that can open the site.

#### "An administrator has not granted this app permission to read SharePoint. Ask your Microsoft admin to grant consent."

Admin consent has not been completed. In Azure, open **API permissions**, select **Grant admin consent**, and confirm the **Status** column reads **Granted**.

#### "This app is not authorised in your Microsoft tenant. Ask your Microsoft admin to grant consent."

Same cause as above. The application has not been consented for your organization.

#### "That SharePoint site could not be found. Check the URL — it should look like https://yourtenant.sharepoint.com/sites/YourSite"

Check the URL. A link to a page or a post inside the site will not work.

#### "The Service Principal client secret is incorrect. Check the secret VALUE (not the secret ID) in the Integrations page."

Check that you entered the secret **Value** and not the **Secret ID**. If you no longer have the Value, create a new secret in Azure and update the integration.

#### "The Service Principal client secret has expired. Create a new secret in Azure and update the integration."

Azure client secrets expire on the date set when they were created. This means you need to refresh your client secret within the Service Principal.

#### "The Service Principal application was not found in this Microsoft tenant. Check the Client ID and Tenant ID."

Check both against the app registration's overview page in Azure.

#### "The Microsoft tenant ID is not valid. Check the Tenant ID in the Integrations page."

Check the **Tenant ID** on the integration.

#### "The Microsoft sign-in for this app has expired. Please reconnect the Microsoft account."

A Direct Login connection has lapsed. Microsoft refresh tokens expire after about 90 days idle, or sooner if the password or sign-in policy changed. Open the app and sign in again.

#### "Microsoft now requires multi-factor authentication for this account. Please reconnect the Microsoft account."

Your organization enabled MFA for the signed-in account. Reconnect it, or switch this news wall to a Service Principal, which is not subject to interactive MFA.

#### "Microsoft is rate-limiting requests for this tenant. This usually clears on its own."

This means that too many requests have been sent to the Microsoft tenant recently, and it is being overloaded. No action needed.

---

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
