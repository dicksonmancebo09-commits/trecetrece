# Biblia visual — Villa Duarte y sus barrios

**Dirección artística principal de _Villa Duarte — Sector Cero_**  
**Estado:** criterio de trabajo aprobado como intención del proyecto; pendiente convertirlo en una hoja de estilo pixel-art y validarlo en pantalla.

## Regla central

El juego debe sentirse inspirado específicamente en **Villa Duarte, Santo Domingo Este, y en la textura cotidiana de sus barrios**, no en una ciudad genérica con elementos dominicanos añadidos. Las imágenes reales del lugar son la fuente primaria de observación; los videojuegos de referencia sirven solamente para estudiar legibilidad, ritmo, atmósfera y composición.

**Docking Bays / Main Deck room 1 es únicamente un punto de referencia técnico para estudiar la ROM. No define la estética del mundo.**

## Rasgos visuales que deben orientar los escenarios

Estos rasgos aparecen en las referencias consultadas, pero deben distribuirse según el tipo de calle o barrio; no se deben colocar todos en cada escena:

- **Viviendas de escala y acabados variados:** casas bajas, edificios de varias plantas, ampliaciones, bloques de hormigón, paredes revocadas y fachadas pintadas en tonos pastel o colores vivos.
- **Frentes habitados:** rejas en puertas y ventanas, galerías, balcones, barandas, muros bajos, persianas y pequeños detalles domésticos visibles desde la calle.
- **Comercio de barrio:** colmados, talleres pequeños, repuestos, mostradores, rótulos pintados y mercancía en estantes o junto a la entrada. Los nombres y marcas del juego serán ficticios salvo que haya permiso para usar marcas reales.
- **Calle real, no escenario limpio:** aceras irregulares o estrechas, bordillos, parches de asfalto, cemento, callejones, entradas laterales y calles con vehículos aparcados.
- **Capa superior urbana:** cables aéreos y postes que recortan el cielo; vegetación tropical, plantas en patios y árboles que proyectan sombras donde corresponda.
- **Vida cotidiana:** bicicletas, motocicletas, coches, sillas, cubos, macetas y presencia vecinal cuando la composición lo permita. No convertir a los residentes en caricaturas ni saturar cada plano de objetos.
- **Luz caribeña:** contraste de sol fuerte y sombras de galerías, árboles y edificios; superficies de hormigón cálidas, pintura algo desgastada y acentos de color comercial.

## Variación entre barrios

No representar Villa Duarte como si todos sus sectores fueran iguales. Crear pequeñas familias visuales, basadas en referencias adicionales antes de cerrar cada diseño:

- **El Caliche:** puede orientar callejones estrechos, frentes modestos, paredes de colores gastados y una escala peatonal cercana, cuando la referencia de esa zona lo respalde.
- **La Francia Nueva:** puede orientar ciertas calles residenciales con fachadas continuas y vehículos en la vía, según las fotografías disponibles.
- **Calero, Pueblo Nuevo, Los Molinos y Simonico:** tratarlos como zonas distintas del mapa, no como etiquetas intercambiables. No fijar arquitectura, distribución ni hitos sin reunir referencias específicas de cada una.

El Atlas de Condición de la Infraestructura del Sistema Vial Urbano de Santo Domingo Este describe Villa Duarte como un sector con siete áreas o subbarrios y una red donde predominan calles, callejones y otras vías de menor jerarquía. Esto refuerza la importancia de diseñar transiciones urbanas y callejones, en lugar de usar solo avenidas anchas. Fuente: [ONE — Atlas de condición de la infraestructura vial urbana de Santo Domingo Este (PDF)](https://www.one.gob.do/media/jojdvjhn/atlascondici%C3%B3ndelainfraestructuradelsistemavialurbanodesantodomingoesterepdom2015.pdf).

## Paleta y tratamiento pixel-art

Punto de partida para probar, no una tabla definitiva:

- Base: grises cálidos de hormigón y cemento, tierra, asfalto oscuro y sombras frías.
- Fachadas: coral apagado, rosa viejo, amarillo soleado, verde menta, azul claro, crema y pintura desgastada, distribuidos según las referencias.
- Acentos pequeños: rojo, verde y colores saturados en letreros, envases, puertas, comercios o vehículos.
- Vegetación: verdes tropicales variados; evitar que el conjunto parezca una jungla.
- Noche/interiores: iluminación cálida desde ventanas y comercios, sombras azuladas y focos selectivos. No aplicar estética neon/cyberpunk global salvo que una zona narrativa concreta lo justifique.

A resolución nativa el jugador, enemigos, plataformas, puertas, peligros y objetos interactivos tienen prioridad de lectura sobre el detalle ambiental. No pintar cada píxel con ruido ni suavizar los bordes por defecto. Los fondos deben aportar identidad sin ocultar colisiones ni confundir siluetas.

## Composición y diseño de niveles

1. Construir primero una calle o callejón reconocible como composición de fondo y suelo, con referencias fotográficas concretas.
2. Separar planos: cielo/cables/árboles, fachadas, objetos cercanos y suelo; usar parallax solo cuando el recurso y el rendimiento lo permitan.
3. Convertir detalles reales en patrones de tiles reutilizables, sin clonar literalmente fachadas, grafitis o composiciones fotográficas.
4. Reservar zonas tranquilas y contrastadas detrás de personajes y enemigos.
5. Crear variantes de calle, callejón, interior de colmado/taller, patio, azotea y paso de servicio únicamente cuando la progresión del juego las necesite y haya referencia visual suficiente.
6. Mantener versiones nativas y ampliadas separadas. Una lámina de 4K es para inspección/presentación; no cambia la resolución nativa de GBA.

## Referencias visuales consultadas

Estas imágenes sirven como **referencia de observación**, no como assets libres para copiar. Antes de reutilizar directamente cualquier imagen, confirmar su licencia específica y los permisos aplicables.

- [Villa Duarte — fachada residencial, pequeño taller, árboles y cableado (Wikimedia Commons)](https://commons.wikimedia.org/wiki/File:Villa_Duarte,_Santo_Domingo_Este,_Dominican_Republic_-_panoramio_(1).jpg)
- [El Caliche — vida de calle y fachadas del barrio (Diario Libre)](https://www.diariolibre.com/actualidad/ciudad/fundacion-busca-fondos-para-transformar-el-sector-el-caliche-de-villa-duarte-MG11174899)
- [La Francia Nueva — calles residenciales y viviendas (El Aviador)](https://www.elaviador.do/texto-diario/mostrar/1343145/asde-entrega-asfaltadas-calles-sector-francia-nueva-villa-duarte)
- [El Caliche — callejón y estado de fachadas (Hoy)](https://hoy.com.do/el-pais/el-caliche-de-villa-duarte-la-otra-cara-del-crecimiento-economico_762790.html)
- [Investigación sobre espacios públicos en Villa Duarte (Entrópico, 2023)](https://revistas.unphu.edu.do/index.php/entropico/es/article/view/238)

## Qué evitar

- Un fondo genérico de “ciudad latinoamericana” que podría pertenecer a cualquier país.
- Neón cyberpunk como identidad por defecto.
- Poner banderas, palmeras, grafitis o motores de forma decorativa en cada plano sin referencia concreta.
- Representar pobreza como espectáculo o a los residentes como estereotipos.
- Copiar sprites, mapas, grafitis identificables, arte o composiciones de juegos comerciales o de fotografías.
- Aprobar el diseño solo porque se ve bien ampliado: debe funcionar a escala de juego.

## Criterio de aceptación

Una hoja de estilo se acepta cuando una persona familiarizada con Villa Duarte puede reconocer rasgos locales en la arquitectura, las proporciones, el comercio, el cableado y las calles; la escena mantiene lectura clara a resolución nativa; y se conoce la procedencia de cada recurso incorporado.

## Siguiente entregable visual

Preparar un **moodboard referencial** con imágenes reales separadas por zona y rasgo, seguido de una composición pixel-art original de una calle de Villa Duarte. La composición será nueva, no una conversión automática ni una copia de una foto. No sustituir la captura real de una sala de Metroid Fusion necesaria para la auditoría técnica.
