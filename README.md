# SistemaRAG (Retrieval-Augmented Generation)

## Descripción

SistemaRAG es un backend desarrollado con **FastAPI** que proporciona una plataforma completa para la carga, procesamiento y consulta de documentos mediante técnicas de Retrieval-Augmented Generation (RAG). 

El sistema utiliza **Supabase** para la gestión de base de datos, autenticación de usuarios y almacenamiento de archivos. Implementa procesamiento asíncrono para la generación de *embeddings* utilizando **Redis** y **RQ** (Redis Queue), y se integra con modelos de Inteligencia Artificial (como OpenAI, PyTorch y HuggingFace Transformers) para entender y responder a preguntas basadas en los documentos cargados.

## Características Principales

*   **Autenticación y Gestión de Usuarios**: Registro, inicio de sesión (JWT) y gestión de perfiles de usuario integrados con Supabase Auth.
*   **Gestión de Documentos**: 
    *   Carga y almacenamiento de archivos de forma segura.
    *   Procesamiento asíncrono de documentos (extracción de texto y segmentación/*chunking*).
    *   Listado y eliminación de documentos asociados a cada usuario.
*   **Motor RAG avanzado**:
    *   Generación de *embeddings* en segundo plano.
    *   Búsqueda vectorial de contexto relevante.
    *   Endpoints REST (`/ask-from-supabase`) y **WebSockets** (`/ws`) para respuestas en tiempo real o por *streaming*.
*   **Historial de Conversaciones**: Almacenamiento automático y recuperación de hilos de chat y mensajes.

## Tecnologías Utilizadas

*   **Backend**: Python 3.12+, FastAPI
*   **Base de datos, Auth & Storage**: Supabase (PostgreSQL)
*   **Cola de tareas y Caché**: Redis, RQ (Redis Queue)
*   **IA & Machine Learning**: 
    *   OpenAI API
    *   HuggingFace (`transformers`, `accelerate`)
    *   PyTorch
    *   FAISS (Búsqueda de similitud)
*   **Orquestación**: Docker y Docker Compose

## Estructura del Proyecto

```text
SistemaRAG/
├── backend/
│   ├── config/         # Configuraciones globales (Supabase, Redis, FastAPI, Tokenizers)
│   ├── routers/        # Definición de endpoints de la API (Auth, Dashboard, RAG, etc.)
│   ├── schemas/        # Modelos de validación de datos (Pydantic)
│   ├── utils/          # Lógica de negocio core (Procesamiento RAG, LLMs, Chunking)
│   ├── worker/         # Scripts del proceso trabajador en segundo plano (RQ Worker)
│   └── main.py         # Punto de entrada principal de la aplicación FastAPI
├── docker-compose.yml  # Orquestación de contenedores (API, Redis, Worker)
└── requirements.txt    # Dependencias del proyecto Python
```

## Requisitos Previos

*   Docker y Docker Compose (Recomendado)
*   Python 3.12+ (Para ejecución local sin Docker)
*   Proyecto y cuenta en [Supabase](https://supabase.com/)
*   Clave(s) de API (p. ej., de OpenAI)

## Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd SistemaRAG
   ```

2. **Configurar las Variables de Entorno:**
   Crea un archivo `.env` en el directorio raíz basándote en las variables requeridas por el sistema (por ejemplo, credenciales de Supabase, Redis URL, claves de la API de OpenAI).

3. **Ejecutar con Docker Compose (Recomendado):**
   Levanta todos los servicios (API, Worker, Redis) ejecutando:
   ```bash
   docker-compose up --build
   ```
   *La API estará disponible en `http://localhost:8000`.*

4. **Ejecución Local (Alternativa sin Docker):**
   ```bash
   # Crear entorno virtual e instalar dependencias
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Iniciar el servidor de desarrollo
   uvicorn backend.main:app --reload

   # En otra terminal, iniciar el worker de RQ
   rq worker --url redis://localhost:6379
   ```

## Endpoints Principales

La documentación interactiva de la API de FastAPI (Swagger UI) está disponible en `http://localhost:8000/docs` una vez que el servidor esté en ejecución.

*   `POST /api/auth/register` - Registro de usuario.
*   `POST /api/auth/login` - Inicio de sesión y obtención de tokens.
*   `GET /api/dashboard/get-documents` - Lista los documentos del usuario.
*   `POST /api/supabase/upload_document_to_supabase` - Sube un documento para ser procesado por el RAG.
*   `POST /api/supabase/ask-from-supabase` - Realiza una pregunta a los documentos (vía REST).
*   `WS /api/supabase/ws` - Endpoint de WebSocket para interacción en tiempo real.
*   `POST /api/messages/get-messages` - Recupera los mensajes de una conversación.
