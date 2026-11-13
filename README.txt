# Guía de instalación y requerimientos del proyecto "2026-III-de-Casilla-en-Casilla"

Este proyecto es una aplicación web desarrollada con Django. A continuación se detallan todos los requerimientos y pasos necesarios para su correcta instalación y funcionamiento.

---

## 1. Requerimientos del sistema

- **Python**: 3.10 o superior (recomendado)
- **Django**: 5.x o 6.x (verifica la versión en requirement.txt)
- **Dependencias adicionales**:
  - dj-database-url
  - python-dotenv
   - mysqlclient (para conexión con MySQL/MariaDB; en Linux requiere las bibliotecas de desarrollo de MySQL o MariaDB)
   - psycopg2-binary (para conexión con PostgreSQL)
- **Base de datos**: SQLite por defecto; también MySQL/MariaDB y PostgreSQL mediante configuración
- **Node.js y npm**: Solo si se va a modificar algun archivos JS/CSS y necesitas herramientas de frontend (opcional)

---

## 2. Instalación de dependencias

1. **Clona el repositorio**
2. Crea un entorno virtual de Python y actívalo:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirement.txt
   ```

---

## 3. Configuración de variables de entorno

Crea o ajusta `De_Casilla_en_Casilla/.env`. Para usar MySQL, configura las variables así:

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=casilla
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3308
```

Para PostgreSQL puedes usar el mismo esquema `DB_*` cambiando `DB_ENGINE` a `django.db.backends.postgresql`. También se admite `DATABASE_URL` cuando `DB_ENGINE` no está definido, por ejemplo:

```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
```

El backend de Django se elige con `DB_ENGINE`; así se pueden usar los motores integrados o backends compatibles de terceros, configurando sus opciones específicas cuando sean necesarias. Si no defines `DB_ENGINE` ni `DATABASE_URL`, se usa SQLite en `De_Casilla_en_Casilla/db.sqlite3`.

---

## 4. Migraciones y carga inicial de datos

Desde la carpeta `De_Casilla_en_Casilla`, ejecuta:

```bash
python manage.py migrate
```

Esto creará todas las tablas necesarias y cargará los niveles iniciales.

---

## 5. Crear superusuario (opcional, para acceso admin)

```bash
python manage.py createsuperuser
```

---

## 6. Ejecutar el servidor de desarrollo

Desde la carpeta `De_Casilla_en_Casilla`, ejecuta:

```bash
python manage.py runserver
```

El sitio estará disponible en http://127.0.0.1:8000/

---

## 7. Estructura de aplicaciones Django incluidas

- **usuarios**: Gestión de usuarios, roles y permisos personalizados.
- **game**: Lógica y vistas del juego.
- **preguntas**: Gestión de preguntas y niveles.

---

## 8. Archivos estáticos y plantillas

- Los archivos estáticos (CSS, JS, imágenes) están en `game/static/` y `usuarios/static/`.
- Las plantillas HTML están en `game/templates/`, `usuarios/templates/` y `preguntas/templates/`.

---

## 9. Notas adicionales

- No compartas el archivo `.env` ni credenciales sensibles.
- Si cambias la base de datos, actualiza `DB_ENGINE` y sus variables `DB_*`, o define `DATABASE_URL`.
- Para producción, configura correctamente `DEBUG`, `ALLOWED_HOSTS` y usa un servidor WSGI adecuado.

---

## 10. Contacto y soporte

Para dudas o soporte, contacta al equipo de desarrollo.
