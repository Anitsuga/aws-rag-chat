import boto3
import json

# =============================
# CONFIGURACIÓN INICIAL
# =============================

region = "us-east-1"
bucket_name = "anitsuga-bedrock-kb"
file_key = "mi_documento.txt"

# Crear clientes AWS
bedrock = boto3.client("bedrock-runtime", region_name=region)
s3 = boto3.client("s3")

# =============================
# PASO 1: LEER DOCUMENTO DESDE S3
# =============================

try:
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    document_text = obj["Body"].read().decode("utf-8", errors="ignore")
    print("✅ Documento leído desde S3 correctamente.")
except Exception as e:
    print("❌ Error al leer el documento desde S3:", e)
    exit()

# =============================
# PASO 2: LOOP INTERACTIVO
# =============================

print("\n💬 Chat con tu documento. Escribí 'salir' para terminar.")

while True:
    query = input("\n🧠 Tu pregunta: ")
    if query.lower() == "salir":
        print("👋 Fin del chat.")
        break

    prompt = f"""
    Responde de forma clara y breve según el contenido del documento a continuación.
    Documento:
    {document_text[:1500]}

    Pregunta: {query}
    """

    try:
        # Llamada al modelo Claude 3.5 Sonnet
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 400,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            })
        )

        result = json.loads(response["body"].read())
        print("\n🤖 Claude responde:\n")
        print(result["content"][0]["text"])

    except Exception as e:
        print("❌ Error al invocar el modelo:", e)
