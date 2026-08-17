# Sprint Monitor 100/200 — MVP

Aplicación web en Streamlit + Supabase para velocistas de 100 y 200 m.

## Incluye

- Login con Supabase Auth.
- Perfil de atleta: hombre/mujer y especialidad.
- Entrenamiento con:
  - distancia de cada bloque,
  - número de repeticiones,
  - recuperación,
  - tiempo individual de cada repetición.
- RPE única para toda la sesión.
- Duración total y cálculo automático de sRPE.
- Registro de competiciones de 100/200 m.
- Registro menstrual para atletas que lo quieran usar.
- Cada registro menstrual puede compartirse o no con el entrenador.
- Dashboard básico de entrenador.
- Row Level Security (RLS).

---

## 1. Crear un proyecto en Supabase

1. Entra en Supabase y crea un proyecto.
2. Ve a **SQL Editor**.
3. Copia todo el archivo `db/schema.sql`.
4. Ejecútalo.
5. En **Authentication > Providers**, deja Email activado.
6. En **Project Settings / API** localiza:
   - Project URL
   - anon/public key

NO uses la `service_role` key en Streamlit.

---

## 2. Configurar el proyecto localmente

Necesitas Python instalado.

```bash
git clone TU_REPOSITORIO
cd sprint-monitor
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

Copia:

```text
.streamlit/secrets.toml.example
```

como:

```text
.streamlit/secrets.toml
```

y rellena:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "tu-anon-key"
```

Ejecuta:

```bash
streamlit run app.py
```

---

## 3. Crear entrenador y atletas

En el MVP todos los usuarios se registran inicialmente como `athlete`.

### Convertir tu cuenta en entrenador

1. Regístrate desde la aplicación.
2. En Supabase abre **Table Editor > profiles**.
3. Busca tu fila.
4. Cambia `role` de `athlete` a `coach`.

### Asignar un atleta al entrenador

1. El atleta crea su cuenta.
2. En `profiles`, abre la fila del atleta.
3. En `coach_id`, introduce el UUID del perfil del entrenador.

Después, las políticas RLS permiten que el entrenador lea sus datos deportivos. La API no permite que un atleta cambie por sí mismo `role` o `coach_id`; esas columnas se administran desde Supabase.

---

## 4. Subir a GitHub

Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Primera versión Sprint Monitor"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

El archivo real `.streamlit/secrets.toml` está ignorado en `.gitignore`, por lo que las claves no se subirán.

---

## 5. Desplegar en Streamlit Community Cloud

1. Entra en Streamlit Community Cloud.
2. Pulsa **Create app**.
3. Selecciona tu repositorio de GitHub.
4. Branch: `main`.
5. Main file path: `app.py`.
6. En **Advanced settings / Secrets**, pega:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "tu-anon-key"
```

7. Despliega.

---

## 6. Datos de series

Ejemplo:

- 60 m
- 3 repeticiones
- 6 min recuperación
- 6.72 / 6.68 / 6.75

La base de datos lo guarda así:

`training_sessions`
→ `sprint_sets`
→ `sprint_reps`

Esto permite calcular posteriormente mejor marca, media, caída de rendimiento, volumen por distancia y evolución histórica.

---

## 7. Importante sobre datos menstruales

Los datos de salud/ciclo pueden ser datos sensibles. El MVP:

- los separa en una tabla propia;
- aplica RLS;
- deja a la atleta decidir si comparte cada registro con su entrenador.

Antes de usar la app con un grupo real, revisa las obligaciones de privacidad, consentimiento y conservación de datos aplicables a tu organización y país.

---

## Siguiente fase recomendada

1. Mejorar dashboard del entrenador.
2. Añadir edición/eliminación de sesiones.
3. Mostrar los tiempos de cada repetición en el historial.
4. PB/SB de 100 y 200.
5. Volumen semanal por distancias.
6. Carga 7/28 días.
7. Wellness diario.
8. Importación/exportación CSV.
9. Alta de atletas controlada por entrenador.
10. Tests y CI con GitHub Actions.
