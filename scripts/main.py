import asyncio
from prefect.idealista_flow import idealista_to_gcp_pipeline

if __name__ == "__main__":
    zone = "madrid"
    province = "madrid"
    type_search = "sale"
    time_period = "24"
    bucket_name = "idealista_data_lake_idealista-scraper-384619"
    dataset_id = "idealista_listings"
    credentials_path = "~/.gcp/terraform.json"
    asyncio.run(
        idealista_to_gcp_pipeline(
            province,
            type_search,
            time_period,
            bucket_name,
            dataset_id,
            credentials_path,
            zone,
            testing=True,
        )
    )