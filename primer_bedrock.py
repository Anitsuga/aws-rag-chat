import boto3, json

# Crear cliente Bedrock Runtime
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Prompt de prueba
prompt = "Explicame brevemente qué es keto."

# Estructura del mensaje
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    ]
}

# Enviar el mensaje al modelo Claude
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    body=json.dumps(body)
)

# Leer y mostrar la respuesta
result = json.loads(response["body"].read())
print("\n📘 Respuesta del modelo:")
print(result["content"][0]["text"])
