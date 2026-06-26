# Sistema de identificación y recuperación de mascotas mediante códigos QR

Sistema web desarrollado con Django para la gestión de mascotas, propietarios, placas QR y reportes de mascotas encontradas.  
El objetivo principal es facilitar la identificación de una mascota mediante un código QR físico y permitir que una persona que la encuentre pueda consultar su perfil, reportar el hallazgo y compartir una ubicación aproximada bajo consentimiento.

## Descripción general

Este proyecto implementa una solución web para asociar placas QR únicas a mascotas registradas.  
Cada placa QR apunta a una URL dinámica del sistema. Cuando una persona escanea el código, puede visualizar información básica de la mascota, consultar los medios de contacto autorizados y enviar un reporte de hallazgo.

El sistema incorpora opciones de privacidad para que el propietario decida si desea mostrar públicamente sus datos de contacto o si prefiere que se muestre información de una asociación civil intermediaria.

## Funcionalidades principales

- Registro y gestión de propietarios.
- Registro y edición de mascotas.
- Generación de placas QR por tipo de mascota.
- Clasificación de placas para perro, gato u otro tipo de mascota.
- Descarga de códigos QR en formato PNG.
- Vista de impresión para placas QR.
- Asignación de placas QR disponibles a mascotas registradas.
- Liberación automática de placas QR al eliminar una mascota.
- Perfil público de mascota accesible mediante QR.
- Control de privacidad de datos del propietario.
- Contacto alternativo mediante asociación civil.
- Validación de formularios.
- Reutilización de propietarios existentes para evitar duplicados.
- Reporte público de mascota encontrada.
- Registro de ubicación aproximada bajo consentimiento del usuario.
- Consulta de ubicación mediante Google Maps.
- Panel de seguimiento de reportes.
- Cierre de reportes con resultado final: mascota encontrada, falsa alarma, duplicado, no localizada u otro.

## Tecnologías utilizadas

- Python
- Django
- PostgreSQL
- HTML
- CSS
- Bootstrap
- JavaScript
- QRCode
- Geolocation API del navegador
- Google Maps mediante enlaces de coordenadas

## Flujo general del sistema

1. El administrador genera placas QR desde el sistema.
2. Las placas quedan registradas como disponibles.
3. Las placas pueden descargarse en PNG o imprimirse.
4. Al registrar una mascota, se selecciona una placa disponible.
5. La placa queda asociada a la mascota.
6. Al escanear el QR, se abre el perfil público de la mascota.
7. El sistema muestra datos de contacto según la configuración de privacidad.
8. La persona que encuentra la mascota puede enviar un reporte.
9. Si acepta compartir ubicación, se registran latitud y longitud aproximadas.
10. El administrador revisa el reporte y lo marca como pendiente, en seguimiento o resuelto.

## Privacidad

El sistema permite configurar si los datos del propietario serán visibles en el perfil público de la mascota.

Si el propietario acepta mostrar sus datos, el perfil puede mostrar nombre, teléfono y correo.  
Si no acepta, el sistema muestra datos de una asociación civil intermediaria para apoyar en el proceso de recuperación.

La ubicación solo se solicita mediante permiso explícito del navegador. Si el usuario no acepta compartirla, puede enviar una referencia manual del lugar donde encontró a la mascota.

## Estado del proyecto

Este proyecto se encuentra en versión beta funcional.

La versión actual permite probar el flujo principal de identificación y recuperación de mascotas, pero todavía no debe considerarse un sistema listo para producción sin ajustes adicionales de seguridad, despliegue y configuración.

## Limitaciones actuales

- La geolocalización es aproximada y depende del navegador, dispositivo, señal GPS, red WiFi o datos móviles.
- Para pruebas remotas se recomienda utilizar un túnel HTTPS temporal como ngrok.
- Para producción se requiere configurar un servidor público con HTTPS.
- La autenticación está orientada al panel administrativo y gestión interna.
- Los archivos multimedia se almacenan localmente.
- No incluye notificaciones automáticas por correo, SMS o WhatsApp.
- No incluye integración real con una asociación civil externa.
- No incluye aplicación móvil nativa.
- No incluye reconocimiento visual de mascotas mediante inteligencia artificial.

## Requisitos

- Python 3.11 o superior
- PostgreSQL
- pip
- virtualenv o entorno virtual equivalente

## Instalación local

Clonar el repositorio:

```bash
git clone https://github.com/luisleonanaya/sistema-codigo-mascotas-qr.git
cd sistema-codigo-mascotas-qr
