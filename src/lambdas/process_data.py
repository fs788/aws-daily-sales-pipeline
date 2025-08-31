import json
import boto3
import pandas as pd
from io import BytesIO
import awswrangler as wr

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get the bucket and file name from the event
    records = event.get('Records', [])
    if not records:
        return {
            'statusCode': 400,
            'body': json.dumps('No records found in event')
        }
    
    # Process each record (file uploaded to S3)
    for record in records:
        s3_bucket = record['s3']['bucket']['name']
        s3_key = record['s3']['object']['key']
        
        # Only process CSV files
        if not s3_key.endswith('.csv'):
            continue
            
        try:
            # Read CSV file from S3
            response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            df = pd.read_csv(BytesIO(response['Body'].read()))
            
            # Simple transformation: add a processed timestamp
            df['processed_at'] = pd.Timestamp.now()
            
            # Calculate total sales if columns exist
            if 'quantity' in df.columns and 'unit_price' in df.columns:
                df['total_sales'] = df['quantity'] * df['unit_price']
            
            # Convert to Parquet format
            parquet_buffer = BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            parquet_buffer.seek(0)
            
            # Upload to processed bucket
            processed_bucket = s3_bucket.replace('raw', 'processed')
            processed_key = s3_key.replace('.csv', '.parquet')
            
            s3.put_object(
                Bucket=processed_bucket,
                Key=processed_key,
                Body=parquet_buffer.getvalue(),
                ContentType='application/parquet'
            )
            
            print(f"Successfully processed {s3_key} to {processed_key}")
            
        except Exception as e:
            print(f"Error processing {s3_key}: {str(e)}")
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing completed successfully')
    }