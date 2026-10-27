# Bitácora de trabajo

## 2026-10-23 a 2026-10-25 — preparación del proyecto

- Se inició trabajo en el repositorio trecetrece con imágenes y referencias visuales de proyecto.
- En la rama main revisada posteriormente, el archivo asset juego barrio z tenía 1 byte y no contenía material útil; el inventario completo no mostraba archivos llamados REA o MAGE.

## 2026-10-26 — prototipo de sala inicial

- Se produjo una prueba de integración visual con ambientación urbana dominicana.
- Resultado real: sustitución gráfica de una sola sala (sala 0 de MAIN_DECK), no de todo el juego.
- En el proceso se identificó que una iteración anterior tenía referencias de gráficos inadecuadas; el prototipo posterior restauró desde la ROM original los dos punteros erróneos que se habían identificado.
- Se realizaron comprobaciones estáticas, pero no se confirmó una prueba de ejecución en MAGE ni en emulador.
- Conclusión: conservar la prueba como registro histórico local, no tratarla como versión estable ni continuar de forma automática por el mismo método.

## 2026-10-27 — documentación y cambio de método

- Se inspeccionó el árbol público de main: 14 archivos, compuesto por README.md, un placeholder llamado asset juego barrio z y varias imágenes watermarked_img_*.jpg.
- No aparece una carpeta/archivo llamado REA en la rama revisada. Es posible que el elemento esté local, en otra rama o en otro repositorio; aún no está identificado.
- Se decidió documentar referencias, licencias, alcance técnico y limitaciones sin subir ROMs, parches ni recursos comerciales.
- **Estado:** no realizar más cambios a la ROM hasta que se defina el nuevo procedimiento.

## Plantilla para nuevas pruebas

Para cada cambio futuro:
1. Objetivo y motivo.
2. Archivo/base/version utilizados.
3. Herramienta y versión.
4. Recurso exacto modificado y ubicación.
5. Hipótesis antes del cambio.
6. Resultado esperado y resultado observado.
7. Prueba de ejecución y evidencia.
8. Método de reversión.
9. Licencia y procedencia de cualquier recurso nuevo.
