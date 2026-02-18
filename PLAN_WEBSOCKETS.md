# Plan de Implementación de WebSockets para RAG en Tiempo Real

**Estado Actual:**
- Lógica de negocio RAG movida a `backend/utils/rag_service.py` (Soporta callbacks).
- Autenticación preparada para WebSockets en `backend/utils/get_current_user_jwt.py`.

**Pasos Restantes:**

1.  **Modificar `backend/routers/init.py` para añadir el endpoint WebSocket**
    *   **Objetivo:** Crear el punto de entrada `/ws` que aceptará conexiones persistentes.
    *   **Acciones:**
        - Importar `WebSocket`, `WebSocketDisconnect` de `fastapi`.
        - Importar `get_current_user_ws` de `utils`.
        - Importar `AskSupabaseModel` (para validar los datos entrantes).
        - Crear el endpoint `@router.websocket("/ws")` (o `/ws/ask`).
    *   **Lógica del Endpoint:**
        - Aceptar conexión (`websocket.accept()`).
        - Validar token (usando `get_current_user_ws` con el token recibido por query param).
        - **Bucle de escucha:**
            - Recibir datos JSON del cliente.
            - Validar datos contra `AskSupabaseModel`.
            - Definir función `send_update(event, payload)` que envíe JSON al cliente: `{"type": event, "data": payload}`.
            - Invocar `process_rag_pipeline(..., callback=send_update)`.
        - Manejar `WebSocketDisconnect` para cerrar limpiamente.
        - Manejar excepciones generales enviando mensajes de error al cliente antes de cerrar si es crítico.

2.  **Actualizar cliente / Pruebas (Verificación)**
    *   **Objetivo:** Asegurar que el flujo funciona.
    *   **Acciones:**
        - Como no tenemos frontend accesible ahora mismo, crearé un pequeño script de Python (`test_ws.py`) que actúe como cliente:
            - Conecte al WebSocket.
            - Envíe un token válido (mock o real si podemos generarlo).
            - Envíe una pregunta.
            - Imprima los mensajes de estado y tokens que llegan en tiempo real.
