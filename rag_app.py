import streamlit as st
import boto3
import json

# =============================
# CONFIGURACIÓN
# =============================
region = "us-east-1"
bucket_name = "anitsuga-bedrock-kb"
file_key = "mi_documento.txt"

# Crear clientes AWS
bedrock = boto3.client("bedrock-runtime", region_name=region)
s3 = boto3.client("s3")

# =============================
# FUNCIONES AUXILIARES
# =============================
@st.cache_data
def cargar_documento():
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    return obj["Body"].read().decode("utf-8", errors="ignore")

import time
import random
import botocore.exceptions

def consultar_bedrock(document_text, query):
    prompt = f"""
    Respondé de manera breve, clara y basada en el siguiente documento.
    Documento:
    {document_text[:1500]}

    Pregunta: {query}
    """

    # Intentar hasta 3 veces con espera progresiva
    for intento in range(3):
        try:
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
            return result["content"][0]["text"]

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException":
                wait = random.uniform(2, 5) * (intento + 1)
                print(f"⚠️ Solicitud limitada. Esperando {wait:.1f} segundos antes de reintentar...")
                time.sleep(wait)
            else:
                raise e

    return "❌ Se alcanzó el límite de reintentos. Esperá unos segundos antes de volver a intentar."


# =============================
# INTERFAZ STREAMLIT CON MEMORIA
# =============================

st.set_page_config(page_title="Chat con tu documento - AWS Bedrock", page_icon="💬")
st.title("💬 Chat con tu documento (RAG + Memoria)")
st.caption("Modelo: Claude 3.5 Sonnet - AWS Bedrock")

document_text = cargar_documento()

# Inicializar el historial de mensajes
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar historial previo
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Campo de entrada estilo chat
if query := st.chat_input("Escribí tu pregunta sobre el documento..."):
    with st.chat_message("user"):
        st.write(query)
    st.session_state.chat_history.append({"role": "user", "content": query})

    # Combinar historial en el prompt para mantener contexto
    context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])

    prompt = f"""
    Usá la siguiente conversación y el contenido del documento para responder de forma coherente y precisa.

    Documento:
    {document_text[:2000]}

    Conversación previa:
    {context}

    Nueva pregunta: {query}
    """

    with st.chat_message("assistant"):
        with st.spinner("Consultando a Claude..."):
            respuesta = consultar_bedrock(document_text, prompt)
        st.write(respuesta)

    st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
