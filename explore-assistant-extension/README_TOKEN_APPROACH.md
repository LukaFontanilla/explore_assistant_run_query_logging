# Explore Assistant: Private Cloud Run with Token

This document outlines the necessary changes to configure the Explore Assistant to support invoking a private Cloud Run service. The process leverages the Looker Extension Server Proxy method and a `createSecretKeyTag` to securely fetch a GCP ID token from a user attribute. This allows the request to the private endpoint to be made from the Looker server, rather than directly from the user's browser, enhancing security.

*Note: No changes are needed on the Cloud Run backend service. However, if there is a need to parse and validate the ID token, refer to the [official GCP documentation](https://cloud.google.com/run/docs/authenticating/service-to-service#receive-request).*

## Step 1: Generate a GCP ID Token for Solution Testing

From a GCP environment (such as Cloud Shell, another Cloud Run service, or a Compute Engine instance), run the following `curl` command to generate a test ID token.

**Replace `AUDIENCE` with the URL of your private Cloud Run deployment for Explore Assistant.**

```sh
curl -H "Metadata-Flavor: Google"

'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=AUDIENCE'
```
Example: 
Cloud Run deployment URL -> https://explore-assistant-12345-us-central1.run.app. 
Script -> 
```sh
curl -H "Metadata-Flavor: Google" \
  'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://explore-assistant-12345-us-central1.run.app'
```

Copy the generated ID token for use in the next step.

## Step 2: Configure a Looker User Attribute

Create a new Looker user attribute with the following properties:

* **Name:** `<extension_id>_gcp_id_token`

  The `<extension_id>` is the portion of your Explore Assistant URL after `extensions/`. For example, from `https://looker.lukapuka.co/extensions/bqml::explore_match`, the extension ID is `bqml::explore_match`. Replace the `::` with a single underscore (`_`) to get the final name: `bqml_explore_match_gcp_id_token`.

* **Data Type:** String Filter (Advanced)

* **User Access:** None

* **Hide Values:** Yes

* **Domain Allowlist:** Your Cloud Run Service URL

* **Default Value:** The ID Token you generated in Step 1

## Step 3: Configure the Looker Extension Manifest

Add the following line to the `entitlements` object in your Explore Assistant's extension manifest file:

```
"scoped_user_attributes": ["gcp_id_token"]
```

> **Important Note:** This user attribute will only be accessible from this specific extension and is resolved exclusively on the Looker server. It will not be accessible from other extensions.

## Step 4: Test the Explore Assistant

After deploying this version of the Explore Assistant, you can verify the secure request flow.

In your browser's network tab, look for request paths that contain `api/internal/extension/external_api_proxy/`. You will observe that the ID token is **not visible** or displayed in this request. The `serverProxy` method passes the necessary information in the request payload to the Looker server, which then makes the secure network request to the endpoint. This ensures that the credential remains secure and is never exposed in the browser.

## Step 5: Configure a Service to Refresh the ID Token

This step is not included as part of the initial implementation but is important for production use.

1. **Configure a cron job service** to periodically run the `curl` command from Step 1 to fetch a new ID token.

2. **Use the Looker API endpoint** to update the user attribute's default value with the newly generated token. The API endpoint for this is documented here: `https://cloud.google.com/looker/docs/reference/looker-api/latest/methods/UserAttribute/update_user_attribute`

> **Note:** GCP ID tokens have a default expiry of one hour. It is recommended to schedule your cron job to run 5-10 minutes before the token's expiration to ensure continuous service.