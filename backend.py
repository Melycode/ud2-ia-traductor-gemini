import os
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Error crítico: No se encontró la variable GEMINI_API_KEY en el archivo .env")


client = genai.Client(api_key=api_key)


json_schema = {
    "type": "OBJECT",
    "properties": {
        "categoria": {
            "type": "STRING",
            "enum": ["incidencia_envio", "devolucion", "consulta_producto", "otro"],
            "description": "Categoría exacta basada en el problema del cliente."
        },
        "prioridad": {
            "type": "STRING",
            "enum": ["alta", "media", "baja"],
            "description": "Nivel de prioridad asignado a la consulta."
        },
        "respuesta_sugerida": {
            "type": "STRING",
            "description": "Borrador de respuesta cordial y profesional redactado en español para el cliente."
        }
    },
    "required": ["categoria", "prioridad", "respuesta_sugerida"]
}


config = types.GenerateContentConfig(
    system_instruction=(
        "Eres un asistente de backend especializado en atención al cliente para una empresa de comercio internacional."
        "Analizas consultas, clasificas incidencias según el esquema y redactas borradores de respuesta formales y cordiales."
    ),
    temperature=0.2, 
    response_mime_type="application/json",
    response_schema=json_schema
)

def procesar_consulta_cliente(mensaje_cliente: str, max_retries=5, base_delay=1.0) -> str:
    """
    Procesa la consulta consumiendo Gemini (gemini-3.1-flash-lite) e implementa
    reintentos con retroceso exponencial y jitter ante errores transitorios (429, 500, etc.).
    """
    for attempt in range(max_retries):
        try:
            print(f"Enviando consulta a Gemini (Intento {attempt + 1}/{max_retries})...")
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"Analiza la siguiente consulta de cliente: {mensaje_cliente}",
                config=config
            )
            

            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                print(f"[Tokens] Entrada: {response.usage_metadata.prompt_token_count} | Salida: {response.usage_metadata.candidates_token_count}")
                
            return response.text

        except APIError as e:
            if e.code in [400, 401, 403, 404]:
                print(f"[Error Permanente {e.code}] La petición no se reintentará.")
                raise e


            if attempt == max_retries - 1:
                print("Se alcanzó el número máximo de reintentos permitidos.")
                raise e


            backoff_delay = base_delay * (2 ** attempt)
            jitter = random.uniform(0, backoff_delay)
            sleep_time = backoff_delay + jitter
            
            print(f"[Error Temporal {e.code}] Reintentando en {sleep_time:.2f}s (Backoff: {backoff_delay:.2f}s + Jitter: {jitter:.2f}s)...")
            time.sleep(sleep_time)

        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)

if __name__ == "__main__":

    consulta_ejemplo = "Hello, my tracking number shows the package is stuck in customs for 5 days. I need it urgently!"
    print(f"Consulta de entrada:\n{consulta_ejemplo}\n")
    
    resultado_json = procesar_consulta_cliente(consulta_ejemplo)
    print("\nRespuesta JSON Estructurada:")
    print(resultado_json)