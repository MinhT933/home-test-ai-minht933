# How to Display Databricks Dashboards on OptiSigns

Article URL: https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns

### In this article, we'll walk you through setting up Databricks to display on your OptiSigns digital signs.

* [What You'll Need](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#WhatYouNeed)
* [Create a Service Principal Connection](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#CreateConnection)
  + [In Databricks](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#InDatabricks)
  + [In OptiSigns](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#InOptiSigns)
* [Prepare Your Databricks Dashboard](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#PrepareDashboard)
  + [Enable Dashboard Embed](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#EnableEmbedding)
  + [Publish Dashboard](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#PublishDashboard)
  + [Share Dashboard with Service Principal](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#ShareDashboard)
  + [Grant the Service Principal Access to the Data (Unity Catalog)](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#GrantAccessToData)
    - [Granting at the Catalog Level Instead](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#CatalogLevel)
* [Create a Databricks App in OptiSigns](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#CreateDatabricksApp)
* [Deploying a Databricks App](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#DeployingDatabricks)
* [Frequently Asked Questions](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#FAQs)

With the Databricks app, you can display a live **Databricks AI/BI dashboard** on any OptiSigns screen.

Once set up, the dashboard renders automatically. It does not require a login on the screen, and it refreshes on a schedule you choose.

---

## What You'll Need

* An OptiSigns account - [**Pro Plus Plan or higher**](https://www.optisigns.com/pricing)
* A Databricks workspace (any tier), with Workspace admin access
* A published AI/BI dashboard
* An [OptiSigns-enabled device](https://support.optisigns.com/hc/en-us/articles/360021855653-What-hardware-and-devices-are-supported)
* A screen, [set up and paired with OptiSigns](https://support.optisigns.com/hc/en-us/articles/18823504383891-OptiSigns-Getting-Started-Guide)

Within Databricks, you'll also need these four values:

* **Workspace URL**
* **Workspace ID**
* **Service Principal Client ID**
* **Service Principal OAuth Secret**

We will show how to find them in the article below.

---

## Create a Service Principal Connection

A service principal (SP) is what OptiSigns uses to render the dashboard. This securely grants OptiSigns access to your published Dashboards without exposing any endpoints.

### In Databricks

Create it in Databricks by clicking the workspace menu in the top right, then clicking **Settings:**

![Databricks workspace menu open with Settings highlighted](https://support.optisigns.com/hc/article_attachments/54089526933395)

Open **Identity and access**, then find **Service principals** and hit **Manage**.

![Databricks Identity and access settings with Manage beside Service principals](https://support.optisigns.com/hc/article_attachments/54089511420947)

Click Add service principal, then Add new service principal to account and workspace:

![Add service principal dialog with Add new service principal to account and workspace selected](https://support.optisigns.com/hc/article_attachments/54089526939667)

Keep the default entitlements (**Consumer**, **Databricks SQL**, **Workspace** = On; **Admin** = Off) → **Add service principal:**

![Add service principal dialog with the name and entitlements set and Admin access off](https://support.optisigns.com/hc/article_attachments/54089526941331)

Next, open the service principal. Your **Client ID** and **Secret** will show. Copy these values. You'll need them.

|  |
| --- |
| **NOTE** |
| These secrets are shown only once. Store them safely. If you lose the secret, you'll need to update your connection. |

The last two values you need are your **Workspace URL** and **Workspace ID.** These are both visible in your Databricks browser address bar (the ID is the `?o=` value).

[![Databricks home page with the browser address bar labelled Workspace URL and Workspace ID](https://support.optisigns.com/hc/article_attachments/54089511430547)](https://support.optisigns.com/optisigns/optisigns-smallapp/optisigns-smallapp-databricks/-/raw/feature/danling/databricks/docs/images/03-databricks-workspace-url-id.png)

You can also find the Workspace ID in your workspace menu.

![Databricks workspace menu showing the Workspace ID with its copy button](https://support.optisigns.com/hc/article_attachments/54089526942995)

You now have all **four values** the connection needs: Workspace URL, Workspace ID, Client ID, Secret.

### In OptiSigns

Go to **Integrations** under your main menu:

![OptiSigns account menu expanded to More with Integrations highlighted](https://support.optisigns.com/hc/article_attachments/54089511434643)

Then, click the **Databricks tab** → **Add Databricks Connection**.

![OptiSigns Integrations page on the Databricks tab with the Add Databricks Connection button](https://support.optisigns.com/hc/article_attachments/54089511435539)

Fill in the form:

![Add Databricks Connection form with fields for workspace URL, ID, client ID and OAuth secret](https://support.optisigns.com/hc/article_attachments/54089526946323)

These values correspond [to the In DataBricks section](https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns#InDatabricks) of this article.

* **Name** — The name of the asset as displayed in OptiSigns. This will not display on your screen.
* **Workspace URL** — The URL of the Workspace.
* **Workspace ID** — The ID of the Workspace.
* **Service principal client ID** — The client ID of your created service principal.
* **Service principal OAuth secret** — The OAuth secret for your service principal.

Click **Add** to save the connection.

|  |
| --- |
| **NOTE** |
| One connection is equal to one Databricks workspace.  If you have more than one workspace, add a separate connection for each. |

---

## Prepare Your Databricks Dashboard

Now that we've set up a Databricks connection, it's time to set up your Dashboard. This will grant the necessary permissions to OptiSigns, allowing you to display your Dashboard on a digital sign.

### Enable Dashboard Embed

Go to **Settings,** then **Security**.

Under **External access**, find **Embed dashboards and Genie Agents**.

Set it to Allow (embed on any domain), or Allow approved domains and add the OptiSigns player host: social-player.optisigns.com. Allow approved domains allows you to keep your embed private while still allowing OptiSigns to access it.

![Databricks Security settings with the Embed dashboards dropdown open on Allow](https://support.optisigns.com/hc/article_attachments/54089511438611)

Do **not** set it to **Deny** — that blocks embedding. On the Free Edition, this may be locked to Allow. This is fine, that's what we want.

### Publish Dashboard

Open the dashboard → **Publish** it (it must be Published, not a draft).

Choose a **data-permission mode**. Both options work with OptiSigns — pick the one that fits your needs:

* **Share data permission (default)** — viewers run queries using the **publisher's credentials**, which enables a **shared cache** for performance.
* **Individual data permission** — each viewer uses their **own data permission** to run queries, which can lead to **more frequent refresh operations**.

![Databricks publish dialog showing Share data permission selected and the Publish button](https://support.optisigns.com/hc/article_attachments/54089511440019)

Note that publishing is not the same as sharing. You will still need to share this Dashboard with our previously created service principal.

### Share Dashboard with Service Principal

Now we'll get the published dashboard shared with our service principal.

On the dashboard, click **Share**. Add the **service principal your connection uses** with **CAN RUN** (or CAN MANAGE).

[![Databricks sharing dialog with the optisigns-embed service principal found and Can Manage set](https://support.optisigns.com/hc/article_attachments/54089511441811)](https://support.optisigns.com/optisigns/optisigns-smallapp/optisigns-smallapp-databricks/-/raw/feature/danling/databricks/docs/images/05-databricks-share-service-principal.png)

Make sure the service principal can access the **data** the dashboard uses.

Back in OptiSigns, **reopen the app config** (or re-select the connection) so the dashboard list refreshes.

### Grant the Service Principal Access to the Data (Unity Catalog)

**Only needed if you published with** ***Individual data permission***. With *Share data permission*, queries run on the publisher's credentials and you can skip this step.

|  |
| --- |
| **NOTE** |
| Sharing the dashboard is not the same as granting access to its data. Sharing lets the service principal OPEN the dashboard. Reading the tables behind it needs separate Unity Catalog privileges. Without them, the dashboard loads with all its titles and layout, but every tile will show "Unable to render visualization." |

Click Catalog in the sidebar and select the schema your dashboard's tables live in. Then go to the Permissions tab and click Grant.

![Databricks Catalog Explorer on the signage_demo Permissions tab with Grant highlighted](https://support.optisigns.com/hc/article_attachments/54312955352723)

Now navigate to **Principals** and find your service principal (e.g. `optisigns-embed`).

Tick **USE SCHEMA** (under *Prerequisite*) and **SELECT** (under *Read*). Leave everything else unticked. The screens only need to read.

[![Grant dialog for the optisigns_embed principal with USE SCHEMA and SELECT ticked](https://support.optisigns.com/hc/article_attachments/54312987805715)](https://support.optisigns.com/optisigns/optisigns-smallapp/optisigns-smallapp-databricks/-/raw/feature/danling/databricks/docs/images/10-databricks-grant-sp-privileges.png)

Click **Confirm**.

Privileges are inherited by all tables and views in the schema, so you don't need to repeat this per table. Do repeat it for **each schema the dashboard reads**, including any lookup or dimension tables it joins to.

### Granting at the catalog level instead

You can grant the same privileges on the **catalog** rather than the schema. Select the catalog and tick `USE CATALOG`, `USE SCHEMA` and `SELECT`.

That covers every schema in the catalog, including ones created later, so there's nothing to repeat. The trade-off is that the service principal can then read *all* the data in that catalog, not just what the dashboards display.

Choose based on what you're comfortable with the screens being able to query:

* **Schema level** — the service principal reads only the schemas your dashboards use.
* **Catalog level** — one grant, but the service principal can read everything in the catalog.

---

## Create a Databricks App Within OptiSigns

Now that we've got our service principal connection and dashboard(s) prepared, we need to actually set them up as Assets within OptiSigns.

To do this, open OptiSigns and go to **Files/Assets** → **Apps** → **Databricks**.

![OptiSigns Add App dialog with the Databricks app tile in the search results](https://support.optisigns.com/hc/article_attachments/54089511443091)

You'll open up the Databricks app and need to fill in some required information:

![OptiSigns Databricks app settings with connection, published dashboard and refresh interval](https://support.optisigns.com/hc/article_attachments/54089526955283)

* **Name -** The name of your Databricks app. This is for use in OptiSigns and will not display on your screen.
* **Databricks Connection -** Choose from any Databricks connections you've set up.
* **Dashboard -** Choose from a list of dashboards associated with this connection.
* **Display**
  + **Refresh (seconds) -** How often you want to refresh the Dashboard. This can be as low as 30s or as high as 3600s. Note that this will cause OptiSigns to fetch updated data, meaning it will flash on your display. More frequent updates will cause more load on the Databricks warehouse.

---

## Deploying a Databricks App

You can deploy your new Databricks app as an individual asset, or as part of a [Split Screen](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App).

To get your new Databricks asset to a screen, go to the **Screens** tab, then click the screen you want to assign it to.

[![OptiSigns Screens list with the Edit button highlighted on a screen](https://support.optisigns.com/hc/article_attachments/54089526956179)](https://support.optisigns.com/hc/article_attachments/54089526956179)

This brings us to the **Edit Screen** tab:

[![Edit Screen dialog with Content Type set to Asset and an asset selector](https://support.optisigns.com/hc/article_attachments/54089511451283)](https://support.optisigns.com/hc/article_attachments/54089511451283)

Here, select **Asset** under Content type. If you already have an Asset, Playlist, or Schedule selected, you can hit **Change**.

Then, select your created Databricks Asset.

Now hit **Save**. Your Databricks asset will now display on screen.

You can also deploy it as part of a split screen, allowing you to show other assets at the same time. See how in our [Split Screen app article.](https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App) It can also be displayed in a Playlist or Schedule.

### How Updates will Appear Onscreen

When you republish your dashboard within Databricks, your changes will appear within one refresh interval.

Your dashboard shows Databricks' cached query results. For the newest data, we recommend you set up a scheduled refresh of the dashboard within Databricks. Your screen will then display the latest results on its next refresh.

---

## Frequently Asked Questions

Here, we'll answer some frequently asked questions our customers have, and solve some common troubleshooting issues.

#### My Dashboard list is empty, or I can't find my Dashboard when configuring the app. How can I make them appear?

This is usually caused when your dashboard isn't shared with your service principal. Ensure the published dashboard is shared with the service principal the connection uses. It should say "CAN RUN". When it does, reopen the picker.

Additionally, make sure the connection you're using matches the workspace where the dashboard lives.

#### My screen is showing "reach out to your workspace administrator." How can I solve this?

This is caused by one of two things:

1. Embedding isn't enabled, or
2. The OptiSigns host isn't allowed

Make sure you've enabled Embedding, and set Embed dashboards to Allow within Databricks. You can, alternatively, make sure "social-player.optisigns.com" is under Allow approved domains.

#### My connection won't save or my verification fails. What can I do?

This means that you've input either the wrong Client ID / Secret, or the wrong Workspace URL / Workspace ID. Re-copy them from Databricks.

Note that the secret is shown only once. You may need to regenerate it if it is lost.

#### My screen is showing an old dashboard and isn't refreshing. Why not?

Your layout updates on the next refresh interval. Additionally, when updates to your Dashboard are made, they need to be published in Databricks (not just saved as a draft). After publishing, wait one interval.

You can always refresh your screen manually to get the latest update.

#### My Databricks dashboard used to display fine, but stopped all of a sudden! What's wrong?

Usually, this has to do with an expired or rotated service principal secret. Try generating a new secret within Databricks and updating your OptiSigns connection.

### That’s all!

OptiSigns is a leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns or getting Snowflake to work on it, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
