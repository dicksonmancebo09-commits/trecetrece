# Localización es-419

Este directorio será la fuente de trabajo para el español de **LATINO AMÉRICA Zector Cero**.

## Archivos

- [Guía de voz y jerga](VOICE_AND_SLANG_GUIDE.md): principios de escritura, perfiles de personajes, referencias y lista obligatoria antes de probar ROM.
- [Diálogos y UI originales](dialogue.json): 27 entradas de diálogo en 7 escenarios, separadas por hablante y con saltos manuales de línea.
- [Glosario regional en JSON](glossary.json): 35 expresiones con región, significado contextual y personaje recomendado.

## Estado actual

La auditoría del árbol público de `main` no encontró una tabla de traducción ni archivos de diálogo ya conectados a la ROM. Por eso estos recursos son un **paquete original de preproducción**, no una afirmación de que la traducción existente haya sido reemplazada.

## Flujo obligatorio

1. Identificar el texto realmente usado por la ROM de trabajo y la versión exacta de su traducción.
2. Extraer las cadenas a un archivo separado o usar la tabla de texto que ya esté vinculada al proyecto.
3. Comparar cada cadena objetivo con la nueva versión, preservando la intención y las claves reales.
4. Ejecutar `python3 tools/check_localization_es419.py` y las pruebas unitarias.
5. Validar encoding, tabla de caracteres, punteros, terminadores, límites de línea y caja de diálogo.
6. Solo entonces ejecutar la prueba en emulador para comprobar la localización en contexto. Nunca subir la ROM ni un parche derivado a este repositorio público.

El límite de 28 caracteres del paquete actual es una guía de redacción, no una garantía de capacidad de la ROM.
