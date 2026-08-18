import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st

# ==========================================
# 🔒 CONFIGURACIÓN DE SEGURIDAD Y LOGIN
# ==========================================
PASSWORD_SECRETA = "PastoSmartVita2026*"  # 🔑 Cambia la contraseña aquí


def generar_hash(password: str) -> str:
  return hashlib.sha256(password.encode()).hexdigest()


HASH_ADMIN = generar_hash(PASSWORD_SECRETA)

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if "arbol_seleccionado" not in st.session_state:
  st.session_state.arbol_seleccionado = None

CARPETA_FOTOS = "fotos_arboles"
os.makedirs(CARPETA_FOTOS, exist_ok=True)

# Logo Local o URL alternativa
LOGO_LOCAL = "logo_sepal.PNG"
LOGO_SEPAL_URL = "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=100063569889815"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SEPAL S.A. - Smart Vita", page_icon="🌳", layout="wide"
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
            "Av. los Estudiantes - Frente a fuente",
            "Requiere poda de realce.",
            "",
        ),
        (
            "ARB-002",
            "Croton magdalenensis",
            "Sangregao",
            4.5,
            "Excelente",
            "Av. los Estudiantes - Esquina Cra 39",
            "Nativa en perfectas condiciones.",
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


def agregar_actualizar_arbol(
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


def eliminar_arbol(codigo):
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("DELETE FROM arboles WHERE codigo = ?", (codigo,))
  conn.commit()
  conn.close()


def obtener_arboles():
  conn = sqlite3.connect("arboles.db")
  df = pd.read_sql_query("SELECT * FROM arboles", conn)
  conn.close()
  return df


# --- FUNCIÓN AUXILIAR PARA MOSTRAR LOGO ---
def mostrar_logo(ancho=220):
  if os.path.exists(LOGO_LOCAL):
    st.image(LOGO_LOCAL, width=ancho)
  else:
    st.image(LOGO_SEPAL_URL, width=ancho)


# --- ENCABEZADO SUPERIOR CENTRADO ---
col_izq, col_centro, col_der = st.columns([1, 2, 1])
with col_centro:
  mostrar_logo(ancho=240)

st.markdown("<h1 style='text-align: center;'>SEPAL S.A. — Programa Smart Vita</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>🌱 Caracterización Arbórea y Cobertura Vegetal | Avenida de los Estudiantes, Pasto</p>", unsafe_allow_html=True)

st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
  mostrar_logo(ancho=180)
  st.markdown("### **Módulo de Navegación**")
  rol = st.radio("Ir a:", ["👤 Consulta Pública", "🛠️ Panel Administrador"])

# ==========================================
# VISTA 1: CONSULTA PÚBLICA (USUARIO)
# ==========================================
if rol == "👤 Consulta Pública":
  df = obtener_arboles()

  if df.empty:
    st.info("No hay registros en el inventario arbóreo.")
  else:
    tab_listado, tab_detalle = st.tabs(
        ["📖 Inventario General", "🔍 Ficha Individual de Especie"]
    )

    with tab_listado:
      col_busq, col_cant = st.columns([3, 1])
      with col_busq:
        busqueda = st.text_input(
            "🔍 Filtrar por código o nombre común:", placeholder="ej. Urapán..."
        )
      with col_cant:
        st.metric("Total Árboles", len(df))

      if busqueda:
        df_mostrar = df[
            df["codigo"].str.contains(busqueda, case=False)
            | df["nombre_comun"].str.contains(busqueda, case=False)
        ]
      else:
        df_mostrar = df

      st.dataframe(
          df_mostrar.drop(columns=["foto_path"], errors="ignore"),
          use_container_width=True,
          height=220,
      )

      st.markdown("##### **Seleccionar árbol para ir a la Ficha Técnica:**")
      col_sel, col_btn = st.columns([3, 1])

      with col_sel:
        codigo_elegido = st.selectbox(
            "Elige un árbol para ver detalles:",
            df_mostrar["codigo"].unique(),
            key="select_publico",
        )

      with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Ver Ficha Técnica"):
          st.session_state.arbol_seleccionado = codigo_elegido
          st.success(f"Cargando ficha de {codigo_elegido}...")

    with tab_detalle:
      codigo_actual = st.session_state.arbol_seleccionado or (
          df["codigo"].iloc[0] if not df.empty else None
      )

      codigo_sel = st.selectbox(
          "Ver detalle del código:",
          df["codigo"].unique(),
          index=list(df["codigo"].unique()).index(codigo_actual)
          if codigo_actual in df["codigo"].unique()
          else 0,
          key="select_detalle",
      )

      if codigo_sel:
        arbol = df[df["codigo"] == codigo_sel].iloc[0]

        col_img, col_info1, col_info2 = st.columns([1, 1.2, 1.2])

        with col_img:
          foto_ruta = arbol.get("foto_path", "")
          if (
              pd.notna(foto_ruta)
              and foto_ruta != ""
              and os.path.exists(str(foto_ruta))
          ):
            st.image(
                foto_ruta,
                caption=f"Registro Fotográfico: {arbol['codigo']}",
                use_container_width=True,
            )
          else:
            st.warning("📷 Sin fotografía registrada.")

        with col_info1:
          st.metric("Código ID", arbol["codigo"])
          st.write(f"**Nombre Común:** {arbol['nombre_comun']}")
          st.write(f"**Especie Científica:** *{arbol['especie']}*")

        with col_info2:
          st.write(f"**Estado de Salud:** `{arbol['estado_salud']}`")
          st.write(f"**Altura Estimada:** {arbol['altura_m']} m")
          st.write(f"**Ubicación:** {arbol['ubicacion_tramo']}")
          st.info(f"**Observaciones:** {arbol['observaciones']}")

# ==========================================
# VISTA 2: PANEL ADMINISTRADOR
# ==========================================
elif rol == "🛠️ Panel Administrador":
  st.subheader("🔒 Gestión de Campo (Equipo Ambiental)")

  if not st.session_state.autenticado:
    col_login, _ = st.columns([1, 1])
    with col_login:
      usuario = st.text_input("Usuario", placeholder="admin")
      password = st.text_input("Contraseña", type="password")

      if st.button("🔑 Iniciar Sesión"):
        if usuario.strip().lower() == "admin" and generar_hash(
            password
        ) == HASH_ADMIN:
          st.session_state.autenticado = True
          st.success("Sesión iniciada correctamente.")
          st.rerun()
        else:
          st.error("Credenciales no válidas.")

  else:
    col_saludo, col_logout = st.columns([4, 1])
    with col_saludo:
      st.success("Sesión de Administración Activa")
    with col_logout:
      if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("---")

    tab_crear_editar, tab_eliminar = st.tabs(
        ["📝 Registrar / Editar Árbol", "🗑️ Eliminar Registro"]
    )

    df_admin = obtener_arboles()

    with tab_crear_editar:
      modo = st.radio(
          "Selecciona la acción:",
          ["➕ Crear Nuevo Registro", "✏️ Editar Existente"],
          horizontal=True,
      )

      v_codigo = ""
      v_especie = ""
      v_nombre = ""
      v_altura = 0.0
      v_estado = "Bueno"
      v_ubicacion = ""
      v_obs = ""
      v_foto_path = ""

      if modo == "✏️ Editar Existente" and not df_admin.empty:
        codigo_edit = st.selectbox(
            "Selecciona el árbol que deseas editar:", df_admin["codigo"].unique()
        )
        arbol_ed = df_admin[df_admin["codigo"] == codigo_edit].iloc[0]

        v_codigo = arbol_ed["codigo"]
        v_especie = arbol_ed["especie"]
        v_nombre = arbol_ed["nombre_comun"]
        v_altura = float(arbol_ed["altura_m"]) if arbol_ed["altura_m"] else 0.0
        v_estado = (
            arbol_ed["estado_salud"]
            if arbol_ed["estado_salud"]
            in ["Excelente", "Bueno", "Regular", "Crítico"]
            else "Bueno"
        )
        v_ubicacion = arbol_ed["ubicacion_tramo"]
        v_obs = arbol_ed["observaciones"]
        v_foto_path = arbol_ed.get("foto_path", "")

      with st.form("form_admin_arbol", clear_on_submit=False):
        col_a, col_b = st.columns(2)

        with col_a:
          codigo = st.text_input(
              "Código Único *",
              value=v_codigo,
              disabled=(modo == "✏️ Editar Existente"),
          )
          especie = st.text_input("Especie / Nombre Científico *", value=v_especie)
          nombre_comun = st.text_input("Nombre Común", value=v_nombre)
          altura = st.number_input(
              "Altura (m)", min_value=0.0, step=0.5, value=v_altura
          )

        with col_b:
          estado = st.selectbox(
              "Estado de Salud",
              ["Excelente", "Bueno", "Regular", "Crítico"],
              index=["Excelente", "Bueno", "Regular", "Crítico"].index(v_estado),
          )
          ubicacion = st.text_input("Tramo / Referencia", value=v_ubicacion)
          observaciones = st.text_area("Observaciones Ambientales", value=v_obs)

        archivo_foto = st.file_uploader(
            "📷 Cargar o reemplazar imagen (JPG, PNG)",
            type=["jpg", "png", "jpeg"],
        )

        submitted = st.form_submit_button("💾 Guardar Registro")

        if submitted:
          if codigo and especie:
            foto_path = v_foto_path
            if archivo_foto is not None:
              ext = archivo_foto.name.split(".")[-1]
              nombre_archivo = f"{codigo}.{ext}"
              foto_path = os.path.join(CARPETA_FOTOS, nombre_archivo)
              with open(foto_path, "wb") as f:
                f.write(archivo_foto.getbuffer())

            agregar_actualizar_arbol(
                codigo,
                especie,
                nombre_comun,
                altura,
                estado,
                ubicacion,
                observaciones,
                foto_path,
            )
            st.success(f"¡Árbol {codigo} guardado exitosamente!")
            st.rerun()
          else:
            st.error("Completa el Código y la Especie.")

    with tab_eliminar:
      st.markdown("#### ⚠️ Eliminar un registro permanentemente")
      if not df_admin.empty:
        codigo_borrar = st.selectbox(
            "Selecciona el árbol a eliminar:",
            df_admin["codigo"].unique(),
            key="del_sel",
        )
        if st.button("❌ Confirmar Eliminación", type="primary"):
          eliminar_arbol(codigo_borrar)
          st.success(f"Árbol {codigo_borrar} eliminado con éxito.")
          st.rerun()
      else:
        st.info("No hay registros para eliminar.")

    st.markdown("---")
    st.markdown("#### 📊 Base de Datos General")
    st.dataframe(obtener_arboles(), use_container_width=True, height=200)
