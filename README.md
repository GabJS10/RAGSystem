# SistemaRAG

SistemaRAG es una API backend para un sistema de RAG (Retrieval-Augmented Generation) construido con Python y FastAPI. Proporciona endpoints para la gestión de autenticación, mensajes y tableros, orquestando el procesamiento de documentos y búsqueda vectorial.

## Tecnologías Principales

- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/)
- **Cola de Tareas:** [RQ (Redis Queue)](https://python-rq.org/)
- **Base de Datos / Auth:** [Supabase](https://supabase.com/)
- **Búsqueda Vectorial:** FAISS / Supabase pgvector (según implementación)
- **Modelos IA:** OpenAI / HuggingFace Transformers
- **Infraestructura:** Docker & Docker Compose
- **Cache/Broker:** Redis

## Estructura del Proyecto

El código fuente se encuentra principalmente en el directorio `backend/`.

```
backend/
├── config/         # Configuraciones de la aplicación (settings, database, etc.)
├── routers/        # Definición de endpoints (auth, dashboard, messages, init)
├── schemas/        # Modelos Pydantic para validación de datos
├── utils/          # Utilidades y lógica de negocio
├── worker/         # Workers para procesamiento de tareas en segundo plano
└── main.py         # Punto de entrada de la aplicación FastAPI
```

- **docker-compose.yml**: Orquesta los servicios de API, Worker y Redis.

## Prerrequisitos

Asegúrate de tener instalados:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Instalación y Uso

1. **Clonar el repositorio:**

   ```bash
   git clone <url-del-repositorio>
   cd SistemaRAG
   ```

2. **Configurar variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto basándote en el ejemplo (si existe) o con las siguientes variables requeridas (ejemplo):
   ```env
   # .env
   SUPABASE_URL=...
   SUPABASE_KEY=...
   OPENAI_API_KEY=...
   REDIS_URL=redis://redis:6379
   ```

3. **Iniciar los servicios:**
   Utiliza Docker Compose para construir y levantar los contenedores.
   ```bash
   docker-compose up --build
   ```

4. **Acceder a la API:**
   Una vez que los contenedores estén corriendo, la API estará disponible en:
   - URL Base: `http://localhost:8000`
   - Documentación Interactiva (Swagger UI): `http://localhost:8000/docs`

## Desarrollo Local

El volumen de Docker está configurado para recargar el código automáticamente (`backend:/app`), por lo que los cambios en el código local se reflejarán inmediatamente en el contenedor.
