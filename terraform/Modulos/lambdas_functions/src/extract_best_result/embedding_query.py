import os
import json
import boto3

bedrock_client = boto3.client("bedrock-runtime")
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "amazon.titan-embed-text-v2:0")

def generate_embedding(text) -> list[float]:
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}).encode("utf-8"),
    )
    result = json.loads(response["body"].read())
    return result.get("embedding", [])

