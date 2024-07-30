# Proyecto Postulación Abaqus

## Consideraciones generales

El proyecto está manejado con docker, por lo que para correrlo basta con hacer docker-compose build y luego docker-compose up. Para poblar los modelos con los datos del excel, mientras estén corriendo los contenedores, se debe correr el comando docker-compose exec web python manage.py load_data. Luego, el código con la api para ver lo pedido en el punto 4 está dentro de la carpeta portfolio en el archivo views.py.
