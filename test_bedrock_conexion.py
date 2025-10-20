import boto3

try:
    # Cliente correcto para administración de modelos
    bedrock = boto3.client("bedrock", region_name="us-east-1")

    response = bedrock.list_foundation_models()
    print("✅ Conexión exitosa. Modelos disponibles:")
    for model in response["modelSummaries"]:
        print(" -", model["modelId"])

except Exception as e:
    print("❌ Error de conexión o permisos:")
    print(e)
