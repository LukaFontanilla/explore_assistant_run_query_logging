# Explore Assistant Backend

## Overview

This Terraform configuration establishes a backend for the Looker Explore Assistant on Google Cloud Platform (GCP), facilitating interaction with the Gemini Pro model of Vertex AI. The setup supports two options: a Cloud Run backend and a BigQuery backend, each acting as a proxy/relay for running content through the model.

The Explore Assistant also uses a set of examples to improve the quality of its answers. We store those examples in BigQuery. Please see the comparisons below when deciding which deployment approach to use.

### What backend should I use?

Here we list the reasons and tradeoffs of each deployment approach in an effort to scope the right backend deployment approach based on individual preferences and existing setups. 

**Regardless of Backend**:
* Any Looker database connection can be used for fetching the actual data returned from the natural language query url
* They implement the same API, as in no Looker Credentials are stored in the backends and the arguments are the same (*ie. model parameters and a prompt*)
* By default both approaches fetch examples from a BigQuery table out of simplicity. For Cloud Run you can modify [this React Hook](../explore-assistant-extension/src/hooks/useBigQueryExamples.ts) and change the `connection_name` on line 18 to point to the non BQ database connection in Looker that houses your example prompts/training data.

**For Cloud Run**:
* Generally speaking, this approach is recommended for folks who want more development control on the backend.
* Your programming language of choice can be used.
* Workflows for custom codeflow like using custom models, combining models to improve results, fetching from external datastores, etc. are supported.
* The service is deployed as a private endpoint within your GCP project, enhancing security. Communication from Looker would typically be configured through a VPC connector.

**For BigQuery**:
* The BigQuery backend is a prototype backend. The cloud run backend will provide better performance
* Generally speaking, this approach will be easier for users already familiar with Looker
* Invoking the LLM with custom prompts is all done through SQL
* BigQuery's Service Account or User Oauth Authentication can be used
* BigQuery however will serve as a pass through to the Vertex API
* Looker & BigQuery query limits will apply to this approach 

## Prerequisites

- Terraform installed on your machine.
- Docker installed on your machine.
- Access to a GCP account with permission to create and manage resources.
- A GCP project where the resources will be deployed.

## Configuration and Deployment

We are using terraform to setup the backend. By default, we will store the state locally. You can also host the terraform state inside the project itself by using a [remote backend](https://developer.hashicorp.com/terraform/language/settings/backends/remote). The configuration is passed on the command line since we want to use the project-id in the bucket name. Since the project-ids are globally unique, so will the storage bucket name.

To use the remote backend you can run `./init.sh remote` instead of `terraform init`. This will create the bucket in the project, and setup the terraform project to use it as a backend.

### Cloud Run Backend

To deploy the Cloud Run backend (Production):

1.  **Build and Push the Docker Image:**
    From the root of the repository, run the following commands to build the Docker image and push it to the Artifact Registry. Make sure you have authenticated with gcloud (`gcloud auth login` and `gcloud auth configure-docker`).

    ```bash
    export PROJECT_ID=(PASTE GCP PROJECT ID HERE)
    export REGION=(PASTE DEPLOYMENT REGION HERE, e.g., us-central1)
    export SERVICE_NAME=explore-assistant-api
    export IMAGE_URL=$REGION-docker.pkg.dev/$PROJECT_ID/explore-assistant-repo/$SERVICE_NAME:latest

    gcloud artifacts repositories create explore-assistant-repo --repository-format=docker --location=$REGION --project=$PROJECT_ID
    gcloud builds submit --project=$PROJECT_ID --tag $IMAGE_URL explore-assistant-cloud-function

    echo "Docker Image URL: $IMAGE_URL"
    ```

2.  **Deploy with Terraform:**
    From the `/explore-assistant-backend/terraform` directory, run the following commands:

    ```bash
    export TF_VAR_project_id=$PROJECT_ID
    export TF_VAR_use_bigquery_backend=0
    export TF_VAR_use_cloud_run_backend=1
    terraform init
    terraform plan
    terraform apply
    ```

### Optional: Deploy with gcloud

As an alternative to using Terraform, you can deploy the Cloud Run service directly using the `gcloud` command-line tool. This is useful for quick deployments or for environments where you are not using Terraform.

```bash
export PROJECT_ID=(PASTE GCP PROJECT ID HERE)
export REGION=(PASTE DEPLOYMENT REGION HERE, e.g., us-central1)
export SERVICE_NAME=explore-assistant-api
export MODEL_NAME=gemini-2.5-flash-lite
export TEMPERATURE=0.2
export IMAGE_URL=$REGION-docker.pkg.dev/$PROJECT_ID/explore-assistant-repo/$SERVICE_NAME:latest
export SERVICE_ACCOUNT="explore-assistant-cr-sa@$PROJECT_ID.iam.gserviceaccount.com"

# First, create the service account if it doesn't exist
gcloud iam service-accounts create explore-assistant-cr-sa --display-name="Looker Explore Assistant Cloud Run SA" --project=$PROJECT_ID

# Grant the aiplatform.user role to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/aiplatform.user"

# Deploy the Cloud Run service
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --platform managed \
  --region $REGION \
  --ingress internal \
  --service-account $SERVICE_ACCOUNT \
  --set-env-vars="PROJECT=$PROJECT_ID,REGION=$REGION,MODEL_NAME=$MODEL_NAME,TEMPERATURE=$TEMPERATURE" \
  --project=$PROJECT_ID
```



### BigQuery Backend

To deploy the BigQuery backend (Prototype):

```bash
cd terraform 
export TF_VAR_project_id=(PASTE BQ PROJECT ID HERE)
export TF_VAR_use_bigquery_backend=1
export TF_VAR_use_cloud_run_backend=0
terraform init
terraform plan
terraform apply
```

You will have to wait 1-2 minutes for the APIs to turn on. You will also have to wait a couple of minutes for the service account for the BigQuery connection to appear.

If you use the defaults, you can test whether everything is working by running:

```sql
    SELECT ml_generate_text_llm_result AS generated_content
    FROM
    ML.GENERATE_TEXT(
        MODEL `explore_assistant.explore_assistant_llm`,
        (
          SELECT "hi" as prompt
        ),
        STRUCT(
        0.05 AS temperature,
        1024 AS max_output_tokens,
        0.98 AS top_p,
        TRUE AS flatten_json_output,
        1 AS top_k)
      )
```

Also, as part of the BigQuery backend setup, we create the Service Account that can be used to connect Looker to the BigQuery dataset to fetch the examples and use the model. You can follow the instructions for creating the connection in Looker here (https://cloud.google.com/looker/docs/db-config-google-bigquery#authentication_with_bigquery_service_accounts). You should be able to pickup the instructions on step 5. 

## Deployment Notes

- Changes to the code in `explore-assistant-cloud-run` will require you to rebuild and push the Docker image to the Artifact Registry. After pushing the new image, you may need to redeploy the Cloud Run service for the changes to take effect. You can do this by running `terraform apply` again.

## Resources Created

- Google Cloud Run service.
- Google BigQuery dataset and table to store the examples
- Google BigQuery connection and gemini pro model, if using the BigQuery backend.
- Necessary IAM roles and permissions for the Looker Explore Assistant to operate.
- Artifact Registry for storing Docker images.

## Cleaning Up

To remove all resources created by this Terraform configuration, run:

```sh
terraform destroy
```

**Note:** This will delete all resources and data. Ensure you have backups if needed.

## Support

For issues, questions, or contributions, please open an issue in the GitHub repository where this configuration is hosted.
