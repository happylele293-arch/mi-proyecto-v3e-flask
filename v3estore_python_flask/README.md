# V3E STORE en Python + Base de Datos + CRUD

Este proyecto conserva el front original y lo reorganiza en Flask para que quede más claro y profesional.

## Qué incluye
- Python + Flask
- Base de datos SQLite automática
- Compatible con MySQL cambiando DATABASE_URL
- Registro de usuarios
- Login y logout
- Dashboard
- Perfil editable
- Contacto guardado en base de datos
- CRUD completo de productos
- Catálogo por categorías

## Nombres conservados
### HTML
- index.html
- productos.html
- maquillaje.html
- ropa.html
- skincare.html
- registro.html
- contacto.html
- dashboard.html
- perfil.html
- instagrampagina.html

### CSS / JS
- style.css
- registro.css
- insta.css
- main.js

## Ejecutar
```bash
pip install -r requirements.txt
python app.py
```

Abre:
http://127.0.0.1:5000/

## MySQL
Puedes usar MySQL definiendo la variable:
DATABASE_URL=mysql+pymysql://root:tu_clave@localhost/v3estore
