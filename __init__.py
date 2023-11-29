import os
import logging
import azure.functions as func
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient
 
def optimize_blob_storage_access_tier(storage_connection_string, container_name, target_access_tier, threshold_age_days):
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
 
    threshold_age = timedelta(days=threshold_age_days)
    utc_now = datetime.utcnow()
 
    for blob_item in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob_item.name)
 
        # Check if the blob meets the criteria for transition
        if utc_now - blob_item.properties.last_modified < threshold_age:
            continue
 
        # Set the access tier to "Cool"
        blob_client.set_blob_access_tier(access_tier=target_access_tier)
        logging.info(f"Blob '{blob_client.url}' access tier set to '{target_access_tier}'.")
 
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()
 
    if mytimer.past_due:
        logging.info('The timer is past due!')
 
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
 
    # Load configuration from environment variables
    storage_connection_string = os.environ["AzureWebJobsStorage"]
    container_name = os.environ["ContainerName"]
    # Set the access tier to "Cool" for blobs that meet certain criteria (e.g., older than 30 days)
    optimize_blob_storage_access_tier(storage_connection_string, container_name, "Cool", 30)
