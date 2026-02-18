# Plan de Mejora de Respuestas RAG

Este documento detalla la estrategia para mejorar la calidad y profundidad de las respuestas del sistema RAG, priorizando la coherencia del contexto y la capacidad de razonamiento del modelo.

## 1. Mejorar Estrategia de "Chunking" (División de Texto)

**Problema Actual:**
La división actual corta el texto arbitrariamente cada 300 caracteres, rompiendo oraciones y perdiendo el significado semántico.

**Solución Propuesta:**
Implementar un **Recursive Character Text Splitter** en `backend/utils/chuncker.py`.

*   **Lógica:** Dividir recursivamente usando separadores en orden de prioridad: `["\n\n", "\n", " ", ""]`. Esto asegura que los párrafos y oraciones se mantengan juntos siempre que sea posible.
*   **Configuración:**
    *   `chunk_size`: Aumentar a ~1000-2000 caracteres (aprox. 300-500 tokens).
    *   `overlap`: ~200 caracteres para mantener contexto entre fragmentos.
*   **Impacto:** Los nuevos documentos indexados tendrán fragmentos con ideas completas, mejorando significativamente la recuperación de información relevante.

## 2. Actualizar Modelo y Prompts

**Problema Actual:**
El uso de `gpt-3.5-turbo` y un prompt restrictivo ("usa únicamente el contexto") limita la capacidad de síntesis y explicación detallada.

**Solución Propuesta:**
Modificar `backend/utils/rag_service.py`.

*   **Modelo:** Actualizar la llamada de `gpt-3.5-turbo` a **`gpt-4o`** (o `gpt-4-turbo`). Este modelo tiene mejor razonamiento y sigue instrucciones complejas con mayor fidelidad.
*   **System Prompt:**
    *   Cambiar el rol a "Asistente Experto y Analítico".
    *   Instrucciones explícitas: "Sintetiza la información de múltiples fuentes", "Explica conceptos complejos detalladamente", "Si la información es parcial, indícalo pero intenta responder con lo disponible".
*   **Estructura del Prompt:** Clarificar la separación entre:
    1.  `Historial de Chat`
    2.  `Contexto Recuperado (Documentos)`
    3.  `Pregunta del Usuario`

## 3. Ajuste de Parámetros de Recuperación

**Problema Actual:**
Con chunks pequeños, se necesitan muchos (top_k=20) para tener contexto, lo que introduce ruido.

**Solución Propuesta:**
Ajustar `backend/utils/rag_service.py` y `backend/schemas/ask_schema.py`.

*   **Top-K:** Reducir `top_k` a **10-15** chunks de alta calidad (dado que ahora serán más grandes y semánticamente completos).
*   **Re-ranking (Opcional):** Si la latencia lo permite, habilitar el re-ranking para estos 10-15 chunks para asegurar que los 5 mejores sean los que más influyan en la respuesta final. Pero esto solo se hará cuando el re-ranking esté habilitado.

## Pasos de Ejecución

1.  **Modificar `backend/utils/chuncker.py`**: Reescribir la función de división de texto.
2.  **Modificar `backend/utils/rag_service.py`**: Actualizar modelo a `gpt-4o` y refinar el prompt.
3.  **Verificación**: Subir un documento técnico o complejo y realizar preguntas de prueba para validar la mejora en la coherencia.

---
*Generado por OpenCode el 16 de Febrero de 2026*
