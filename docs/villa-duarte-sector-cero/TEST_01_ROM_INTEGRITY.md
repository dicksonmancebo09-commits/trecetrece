# Prueba 01 de ROM — Urban Opening v1.0

**Proyecto oficial:** LATINO AMÉRICA Zector Cero  
**Prueba:** #01 · integridad del parche y revisión de vista de referencia  
**Fecha:** 27 de octubre de 2026  
**Estado:** comprobado estáticamente; no probado en emulador.

## Qué se ha probado

Se tomó la ROM base archivada por el usuario y el parche existente `Villa_Duarte_Sector_Cero_v1.0_full.ips`. Se aplicó el parche mediante un verificador IPS independiente y se comparó la salida byte por byte con la build `Villa_Duarte_Sector_Cero_v1.0_URBAN_OPENING.gba` archivada en la biblioteca. El resultado **coincide exactamente** con esa build.

### Identificadores verificados

| Elemento | Resultado |
|---|---|
| ROM base | `MetroidFusion_original_backup.gba` |
| Tamaño de la base | 8.388.608 bytes (8 MiB) |
| SHA-256 de la base | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` |
| Parche | `Villa_Duarte_Sector_Cero_v1.0_full.ips` |
| Tamaño del parche | 98.969 bytes |
| SHA-256 del parche | `7b51ad528bd2e965e5c8ac399452f2f53c99cc21d164a951919be6268eb4da96` |
| Registros IPS | 7.892 |
| Bytes distintos de la base tras aplicar el parche | 59.501 |
| SHA-256 de la salida v1.0 | `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5` |
| Cabecera | título `METROID4USA`, código `AMTE`, checksum `0x98` |
| Comparación con la build archivada | Coincidencia byte por byte: sí |

## Vista disponible

![Reconstrucción de la sala de Urban Opening v1.0](../../assets/test-builds/test-01/v1.0-urban-opening-room-reconstruction.png)

Esta imagen es una **reconstrucción del mapa/sala para inspección**, no una captura producida por un emulador. Sirve para observar el aspecto de la versión anterior: edificios de varias plantas, colmado ficticio, ventanas, rejas, calzada y vehículo.

## Qué no se ha validado

- No se ha ejecutado la ROM en mGBA, MAGE ni otro emulador en esta prueba.
- No hay confirmación de arranque, control del jugador, transiciones, colisiones ni estabilidad durante juego.
- La imagen mostrada no procede de una sesión de emulador.
- Los atlas de los escenarios 1 y 2, creados después, no están integrados en esta build.
- El paquete de localización `es-419` no está insertado en esta build.

## Conclusión

La prueba demuestra que el parche IPS reproduce exactamente el prototipo v1.0 archivado y conserva los datos de cabecera esperados. **No demuestra jugabilidad**. La siguiente fase de validación requiere abrir esta misma salida en mGBA/MAGE y obtener una captura nueva, identificada como captura de emulador. Solo después se podrá comparar la ROM en ejecución con la dirección visual actual de LATINO AMÉRICA Zector Cero.

## Descarga privada de la prueba

El paquete descargable entregado en esta conversación incluye el parche IPS y la documentación de prueba, pero excluye la ROM comercial completa. El parche debe aplicarse a una copia propia de la ROM base con el SHA-256 indicado arriba. El parche IPS no se añade a este repositorio público.
