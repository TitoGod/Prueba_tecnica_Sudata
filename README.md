# Repositorio de Prueba Técnica Sudata

Este repositorio contiene la resolución de distintos ejercicios como parte de una prueba técnica. Cada ejercicio se encuentra organizado en su propia carpeta con código fuente, scripts, y un `README.md` explicativo.

---

## 📁 Estructura general

```text
Ejercicio 1/
├── replicate.py        # Script Python de replicación
├── create_db.py        # Script Python para crear la base de datos y las tablas en PostgreSQL
├── csv_to_db.py        # Script Python para poblar las tablas con datos
├── .env.example        # Ejemplo de archivo con variables de entorno
├── README.md           # Documentación principal para este ejercicio
└── screenshots/        # Capturas de pantalla del Programador de Tareas en Windows
    ├── Esqueda DB      # Screenshot del esquema creado en Supabase
    └── pasos.png       # Imagenes explicativas

Ejercicio 2/
├── data_historica.py   # Script principal para extraer las cotizaciones históricas desde la API del BCRA
├── incremental.py      # Script para ingresar los nuevos datos a partir de la ultima fecha registrada en la base de datos
├── utils.py            # Todas las funciones necesarias para mantener el código limpio y escalable
├── .env.example        # Ejemplo con variables necesarias
└── README.md           # Documentación detallada del Ejercicio 2

└── README.md           # Este README global
````

---

## 📌 Contenidos por ejercicio

### 🔹 Ejercicio 1: Replicación PostgreSQL → Supabase

* Crear una base PostgreSQL local (`ventas_origen`)
* Crear y poblar tablas con datos desde CSV
* Replicar los datos a una base espejo en Supabase (`ventas_espejo`)
* Automatizar la replicación diaria con Task Scheduler (Programador de Tareas de Windows)

> Actualmente la replicación se realiza utilizando un cron job en **Render**, conectando a una base PostgreSQL desplegada también en **Render**.
> La carpeta `.github/workflows` ha sido eliminada ya que **no se utiliza GitHub Actions**.

Ver [Ejercicio 1/README.md](Ejercicio%201/README.md) para más detalles.

---

### 🔹 Ejercicio 2: Extracción incremental desde la API del BCRA usando Render cron jobs

* Se conecta a la [API oficial del BCRA](https://api.bcra.gob.ar/) para obtener las cotizaciones del dólar tipo vendedor.
* La extracción es **incremental**, es decir, se descarga solo la información nueva desde la última fecha registrada.
* Se utiliza una base PostgreSQL en la nube desplegada en **Render**.
* La actualización semanal se realiza mediante un **cron job configurado en Render** (sin necesidad de Task Scheduler ni GitHub Actions).

Ver [Ejercicio 2/README.md](Ejercicio%202/README.md) para más detalles.

---

## ✅ Recomendaciones de uso

* Ingresar a cada carpeta de ejercicio para acceder a sus scripts y documentación específica.
* Usar entornos virtuales para instalar dependencias locales.
* Documentar cada nuevo ejercicio agregando su propia carpeta y README.

---

## 📄 Licencia

Este repositorio está disponible bajo la licencia MIT.
