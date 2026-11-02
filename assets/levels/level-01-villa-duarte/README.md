# L01 — Villa Duarte: atlas gráfico modular GBA v0.2

**Resolución:** 256 × 256 px · 32 × 32 tiles lógicos de 8 × 8 px  
**Estado:** SVG editable creado; PNG indexado, 4bpp e integración ROM pendientes.

## Archivos

- [Atlas SVG v0.2](level-01-villa-duarte-atlas-v0.2.svg)
- [Metadatos de módulos y paleta](level-01-villa-duarte-atlas-v0.2.json)
- Atlas anterior v0.1 conservado en `assets/tiles/scenario-01/`.

## Distribución

| Fila | Familia | Contenido |
|---:|---|---|
| 0 | Muros | 8 superficies de hormigón, bloque y pintura |
| 1 | Fachadas | plantas bajas/altas, balcones y esquinas |
| 2 | Ventanas | variantes estrechas, anchas, rejas y persianas |
| 3 | Puertas/comercio | puertas, colmado ficticio, mostrador, toldo y portón |
| 4 | Balcones/azoteas | escaleras, pretil, depósito, antena y patio |
| 5 | Calle/servicios | motocicleta, silla, cajas, planta, poste, contador, cable y drenaje |
| 6 | Suelo | acera, bordillo, asfalto, registro y bache |
| 7 | Interiores/hangar | estantería, mostrador, acceso de seguridad y compuerta |

Cada celda mide 32 × 32 px y agrupa 4 × 4 tiles lógicos. El JSON da las coordenadas y el índice inicial de los 64 módulos.

## Uso para las 87 salas

El atlas es una biblioteca, no 87 mapas ya montados. Cada sala se compone con módulos pertinentes y se cruza con su ID `L01_Rxxx`, las puertas extraídas, el mapa fuente, las dimensiones y el clipdata de la ROM exacta.

## Próxima integración

1. Exportar el SVG a PNG nativo de 256 × 256 sin suavizado.
2. Indexar con la paleta documentada y reservar el índice transparente según el layer objetivo.
3. Convertir a 4bpp y revisar el orden de los tiles.
4. Componer las primeras salas conectadas usando las puertas de referencia y geometría extraída.
5. Crear colisiones y eventos aparte del arte.

**No se ha modificado la ROM.** Este atlas aún no está validado dentro de MAGE o mGBA.
