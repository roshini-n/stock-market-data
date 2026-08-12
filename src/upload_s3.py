import boto3
bucket_name = "stocks-bronze-layer"
def upload_file(file_path, bucket_name, s3_key):
    # Create an S3 client
    s3 = boto3.client("s3")
    
    # Upload the file
    s3.upload_file(file_path, bucket_name, s3_key)
    print(f"File {file_path} uploaded to s3://{bucket_name}/{s3_key} successfully!")
    
upload_file(
    "data/raw/SP500_Historical_Data.csv",
    bucket_name,
    "raw/batch/SP500_Historical_Data.csv"
)