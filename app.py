import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st

# ==========================================
# 🔒 CONFIGURACIÓN DE SEGURIDAD Y LOGIN
# ==========================================
# CONTRASEÑA POR DEFECTO: pon aquí la contraseña que solo tú sabrás.
PASSWORD_SECRETA = "PastoSmartVita2026*"  # <-- 🔑 CAMBIA ESTA CONTRASEÑA


def generar_hash(password: str) -> str:
  """Convierte la contraseña a un hash SHA-256 seguro."""
  return hashlib.sha256(password.encode()).hexdigest()


HASH_ADMIN = generar_hash(PASSWORD_SECRETA)

# Manejo de la sesión de autenticación
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

# Crear carpeta de fotos
CARPETA_FOTOS = "fotos_arboles"
os.makedirs(CARPETA_FOTOS, exist_ok=True)

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Smart Vita - Caracterización de Árboles",
    page_icon="🌳",
    layout="wide",
)


# --- BASE DE DATOS (SQLite) ---
def init_db():
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS arboles (
            codigo TEXT PRIMARY KEY,
            especie TEXT,
            nombre_comun TEXT,
            altura_m REAL,
            estado_salud TEXT,
            ubicacion_tramo TEXT,
            observaciones TEXT,
            foto_path TEXT
        )
    """)
  try:
    c.execute("ALTER TABLE arboles ADD COLUMN foto_path TEXT")
  except sqlite3.OperationalError:
    pass

  conn.commit()
  conn.close()


def insertar_datos_prueba():
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("SELECT COUNT(*) FROM arboles")
  if c.fetchone()[0] == 0:
    arboles_prueba = [
        (
            "ARB-001",
            "Fraxinus uhdei",
            "Urapán",
            8.5,
            "Bueno",
            "Avenida los Estudiantes - Frente a fuente",
            "Requiere poda de realce.",
            "",
        ),
        (
            "ARB-002",
            "Croton magdalenensis",
            "Sangregao",
            4.5,
            "Excelente",
            "Avenida los Estudiantes - Esquina Cra 39",
            "Especie nativa en perfectas condiciones.",
            "",
        ),
    ]
    c.executemany(
        """
            INSERT INTO arboles 
            (codigo, especie, nombre_comun, altura_m, estado_salud, ubicacion_tramo, observaciones, foto_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        arboles_prueba,
    )
    conn.commit()
  conn.close()


init_db()
insertar_datos_prueba()


def agregar_arbol(
    codigo, especie, nombre_comun, altura, estado, ubicacion, obs, foto_path
):
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute(
      """
        INSERT OR REPLACE INTO arboles 
        (codigo, especie, nombre_comun, altura_m, estado_salud, ubicacion_tramo, observaciones, foto_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          codigo,
          especie,
          nombre_comun,
          altura,
          estado,
          ubicacion,
          obs,
          foto_path,
      ),
  )
  conn.commit()
  conn.close()


def obtener_arboles():
  conn = sqlite3.connect("arboles.db")
  df = pd.read_sql_query("SELECT * FROM arboles", conn)
  conn.close()
  return df


# --- ENCABEZADO PRINCIPAL ---
st.title("🌳 SEPAL - Programa Smart Vita")
st.subheader(
    "Piloto de Caracterización de Árboles - Avenida de los Estudiantes"
)

# --- BARRA LATERAL ---
st.sidebar.header("Menú Principal")
rol = st.sidebar.radio(
    "Selecciona una vista:", ["👤 Consulta Pública", "🛠️ Panel Administrador"]
)

# ==========================================
# VISTA 1: CONSULTA PÚBLICA (USUARIO)
# ==========================================
if rol == "👤 Consulta Pública":
  st.header("Catálogo de Especies Urbe")

  df = obtener_arboles()

  if df.empty:
    st.info("Aún no hay árboles registrados.")
  else:
    busqueda = st.text_input(
        "🔍 Buscar por código (ej. ARB-001) o nombre común:"
    )

    if busqueda:
      df_filtrado = df[
          df["codigo"].str.contains(busqueda, case=False)
          | df["nombre_comun"].str.contains(busqueda, case=False)
      ]
      st.dataframe(
          df_filtrado.drop(columns=["foto_path"], errors="ignore"),
          use_container_width=True,
      )
    else:
      st.dataframe(
          df.drop(columns=["foto_path"], errors="ignore"),
          use_container_width=True,
      )

    st.markdown("---")
    st.subheader("📋 Ficha de Detalle del Árbol")

    codigo_sel = st.selectbox(
        "Selecciona un código para ver ficha:", df["codigo"].unique()
    )

    if codigo_sel:
      arbol = df[df["codigo"] == codigo_sel].iloc[0]

      col_foto, col_datos1, col_datos2 = st.columns([1.2, 1, 1])

      with col_foto:
        foto_ruta = arbol.get("foto_path", "")
        if (
            pd.notna(foto_ruta)
            and foto_ruta != ""
            and os.path.exists(str(foto_ruta))
        ):
          st.image(
              foto_ruta,
              caption=f"Foto Registro: {arbol['codigo']}",
              use_container_width=True,
          )
        else:
          st.info("📷 Registro sin fotografía por el momento.")

      with col_datos1:
        st.metric("Código ID", arbol["codigo"])
        st.write(f"**Nombre Común:** {arbol['nombre_comun']}")
        st.write(f"**Especie Científica:** *{arbol['especie']}*")
        st.write(f"**Altura Estimada:** {arbol['altura_m']} m")

      with col_datos2:
        st.write(f"**Estado de Salud:** {arbol['estado_salud']}")
        st.write(f"**Ubicación/Tramo:** {arbol['ubicacion_tramo']}")
        st.write(f"**Observaciones:** {arbol['observaciones']}")

# ==========================================
# VISTA 2: PANEL ADMINISTRADOR (LOGIN REQUERIDO)
# ==========================================
elif rol == "🛠️ Panel Administrador":
  st.header("🔒 Módulo de Administración - SEPAL Smart Vita")

  # --- FORMULARIO DE LOGIN ---
  if not st.session_state.autenticado:
    st.info("Ingresa tus credenciales para acceder a la gestión de datos.")

    col_login, _ = st.columns([1, 1])
    with col_login:
      usuario = st.text_input("Usuario", placeholder="admin")
      password = st.text_input("Contraseña", type="password")

      if st.button("🔑 Iniciar Sesión"):
        if usuario.strip().lower() == "admin" and generar_hash(
            password
        ) == HASH_ADMIN:
          st.session_state.autenticado = True
          st.success("¡Autenticación exitosa!")
          st.rerun()
        else:
          st.error("Usuario o contraseña incorrectos.")

  # --- PANEL DE CONTROL (SESIÓN ACTIVA) ---
  else:
    # Botón para Cerrar Sesión
    col_saludo, col_logout = st.columns([3, 1])
    with col_saludo:
      st.success("Sesión activa como **Administrador**.")
    with col_logout:
      if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Registrar o Modificar Especie")

    with st.form("form_arbol", clear_on_submit=True):
      col_a, col_b = st.columns(2)

      with col_a:
        codigo = st.text_input("Código Único *", placeholder="ej. ARB-003")
        especie = st.text_input(
            "Especie / Nombre Científico *", placeholder="ej. Acacia melanoxylon"
        )
        nombre_comun = st.text_input(
            "Nombre Común", placeholder="ej. Acacia negra"
        )
        altura = st.number_input("Altura (metros)", min_value=0.0, step=0.5)

      with col_b:
        estado = st.selectbox(
            "Estado de Salud", ["Excelente", "Bueno", "Regular", "Crítico"]
        )
        ubicacion = st.text_input(
            "Tramo / Referencia", placeholder="Frente a Calle 18..."
        )
        observaciones = st.text_area("Observaciones Ambientales")

      st.markdown("📷 **Fotografía de Campo**")
      archivo_foto = st.file_uploader(
          "Cargar imagen (JPG, PNG)", type=["jpg", "png", "jpeg"]
      )

      submitted = st.form_submit_button("💾 Guardar Datos y Imagen")

      if submitted:
        if codigo and especie:
          foto_path = ""

          if archivo_foto is not None:
            ext = archivo_foto.name.split(".")[-1]
            nombre_archivo = f"{codigo}.{ext}"
            foto_path = os.path.join(CARPETA_FOTOS, nombre_archivo)

            with open(foto_path, "wb") as f:
              f.write(archivo_foto.getbuffer())

          agregar_arbol(
              codigo,
              especie,
              nombre_comun,
              altura,
              estado,
              ubicacion,
              observaciones,
              foto_path,
          )
          st.success(f"¡Árbol {codigo} guardado correctamente!")
          st.rerun()
        else:
          st.error("Debes completar al menos el Código y la Especie.")

    st.markdown("---")
    st.subheader("📊 Base de Datos Completa")
    df_admin = obtener_arboles()
    st.dataframe(df_admin, use_container_width=True)