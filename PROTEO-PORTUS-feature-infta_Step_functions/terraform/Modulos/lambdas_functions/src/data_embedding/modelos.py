import boto3

region = "eu-west-1"
bedrock = boto3.client("bedrock", region_name=region)

response = bedrock.list_foundation_models()

print(f"Modelos disponibles en {region}:\n")
for model in response["modelSummaries"]:
    print(f"- {model['modelId']} ({model['modelName']}) - {model['outputModalities']}")
