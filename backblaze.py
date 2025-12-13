import boto3
from io import BytesIO
import pandas as pd
import json
import os

# ===========================
# Backblaze B2 Client Setup
# ===========================
S3_ENDPOINT = "https://s3.us-east-005.backblazeb2.com"
AWS_KEY_ID = "005239ca03b31af0000000001"
AWS_SECRET_KEY = "K005uGFZkrtYa4Hg1GliFUQohs/BTk4"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)


# ===========================
# Helper to get extension
# ===========================
def get_ext(file_name):
    return os.path.splitext(file_name)[1].lower().replace(".", "")


# ===========================
# Upload any file
# ===========================
def upload_file(bucket_name, file_name, file_content):
    """
    Upload any file to Backblaze B2.
    Auto-detect type from file_name extension.
    - str → txt
    - dict → json
    - pd.DataFrame → csv or excel
    - bytes → raw files (pdf, png, etc.)
    """
    ext = get_ext(file_name)

    if isinstance(file_content, pd.DataFrame):
        buffer = BytesIO()
        if ext in ["csv"]:
            file_content.to_csv(buffer, index=False)
        elif ext in ["xlsx", "xls"]:
            file_content.to_excel(buffer, index=False)
        else:
            raise ValueError(f"Unsupported dataframe extension: {ext}")
        buffer.seek(0)
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=buffer.getvalue())
        return

    if isinstance(file_content, dict) and ext == "json":
        file_content = json.dumps(file_content)

    if isinstance(file_content, str) and ext in ["txt", "csv", "json", "html"]:
        file_content = file_content.encode("utf-8")

    if isinstance(file_content, bytes):
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        return

    # fallback for str
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)


# ===========================
# Read any file
# ===========================
def read_file(bucket_name, file_name):
    """
    Read a file from B2.
    Auto-detect type from file_name extension.
    Returns:
    - str for txt, html, csv (or you can parse csv to DataFrame)
    - dict for json
    - bytes for pdf, images, etc.
    """
    ext = get_ext(file_name)
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        data = obj['Body'].read()

        if ext in ["txt", "html"]:
            return data.decode("utf-8")
        elif ext == "csv":
            return pd.read_csv(BytesIO(data))
        elif ext in ["xlsx", "xls"]:
            return pd.read_excel(BytesIO(data))
        elif ext == "json":
            return json.loads(data)
        else:
            return data  # raw bytes for pdf, png, images, etc.
    except s3.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error reading {file_name} from B2: {e}")
        return None
