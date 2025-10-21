import os
import boto3
import io
from pdf2image import convert_from_bytes


def analyze_1040(document_bytes):
    """Call AWS Textract to analyze a 1040 form"""
    region = os.getenv("AWS_REGION", "us-east-1")
    
    client = boto3.client(
        "textract",
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    )
    
    # Try to detect if it's a PDF and convert to image
    processed_bytes = document_bytes
    if document_bytes.startswith(b'%PDF'):
        # Convert PDF first page to image
        try:
            images = convert_from_bytes(document_bytes, first_page=1, last_page=1)
            if images:
                # Convert to JPEG bytes
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='JPEG', quality=95)
                processed_bytes = img_byte_arr.getvalue()
        except:
            pass

    response = client.analyze_document(
        Document={"Bytes": processed_bytes}, FeatureTypes=["FORMS"]
    )

    return response
