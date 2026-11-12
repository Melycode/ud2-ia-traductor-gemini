# Prueba de Concepto: Automatización de Atención al Cliente con IA (UD2)

Solución desarrollada para optimizar los costes de soporte y agilizar la atención al cliente en una empresa de comercio internacional mediante una arquitectura híbrida (inferencia local en el cliente + API generativa en el servidor).

## Arquitectura del Proyecto

1. **Frontend (`index.html`, `style.css`, `app.js`) — Traductor Offline en el Navegador:**
   * Implementado con **Transformers.js** (`@huggingface/transformers`) vía CDN.
   * Ejecuta localmente los modelos `Xenova/opus-mt-en-es` (Inglés ➔ Español) y `Xenova/opus-mt-es-en` (Español ➔ Inglés) sin costes por llamada ni sobrecarga en el servidor.
   * Detecta automáticamente aceleración por hardware mediante **WebGPU**, aplicando **WebAssembly (WASM)** como *fallback* transparente.

2. **Backend (`backend.py`) — Clasificación y Respuesta Automática:**
   * Desarrollado en Python utilizando el SDK oficial `google-genai` con el modelo ligero `gemini-3.1-flash-lite`.
   * Fuerza una salida estructurada estricta mediante **JSON Schema** (`categoria`, `prioridad` y `respuesta_sugerida`).
   * Gestiona errores transitorios (`429`, `500`, `503`) mediante un algoritmo de **retroceso exponencial con *jitter*** (*Exponential Backoff*) y monitoriza el consumo de tokens (`usage_metadata`).

