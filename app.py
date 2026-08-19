import base64
import hashlib
import io
import os
import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 🔒 1. CONFIGURACIÓN DE SEGURIDAD Y USUARIO
# ==========================================
USUARIO_ADMIN = "admin"
PASSWORD_SECRETA = "PastoSmartVita2026*"


def generar_hash(cadena: str) -> str:
  return hashlib.sha256(cadena.encode()).hexdigest()


HASH_ADMIN = generar_hash(PASSWORD_SECRETA)

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

CARPETA_FOTOS = "fotos_arboles"
os.makedirs(CARPETA_FOTOS, exist_ok=True)

LOGO_LOCAL = "logo_sepal.png"
LOGO_SEPAL_URL = (
    "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=100063569889815"
)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SEPAL S.A. - Smart Vita",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 🎨 2. ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #f0f8ff;
    }
    div[data-testid="stForm"], div[data-testid="stExpander"], div.stMarkdown > div {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
    }
    h1 {
        color: #72efdd !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 800;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
    }
    h2, h3, h4 { color: #80ed99 !important; }
    .stButton > button {
        background: linear-gradient(90deg, #38b000 0%, #007200 100%);
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 12px rgba(56, 176, 0, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(56, 176, 0, 0.7);
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 25, 30, 0.85) !important;
        border-right: 1px solid rgba(128, 237, 153, 0.2);
    }
    .metric-card {
        background: rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(114, 239, 221, 0.3);
    }
    </style>
""",
    unsafe_allow_html=True,
)

CAMPOS_BD = [
    "codigo",
    "codigo_qr",
    "nombre_comun",
    "nombre_cientifico",
    "familia",
    "genero",
    "especie",
    "origen",
    "latitud",
    "longitud",
    "altitud",
    "direccion",
    "barrio",
    "comuna",
    "sector",
    "coord_magna",
    "dap",
    "altura_total",
    "altura_fuste",
    "diametro_mayor_copa",
    "diametro_menor_copa",
    "area_copa",
    "estado_fuste",
    "inclinacion",
    "cavidades_descortezamiento",
    "ramas_secas",
    "raices_expuestas",
    "plagas",
    "enfermedades",
    "sintomas",
    "porcentaje_afectacion",
    "estado_copa",
    "estado_general",
    "riesgo_volcamiento",
    "riesgo_caida_ramas",
    "interferencia_redes",
    "infraestructura_movilidad",
    "emplazamiento",
    "infraestructura",
    "manejo",
    "priorizacion",
    "evidencia_fuste",
    "evidencia_copa",
    "evidencia_afectaciones",
    "evidencia_general",
    "fecha_inventario",
    "responsable",
    "fecha_actualizacion",
    "intervencion_realizada",
    "nueva_evaluacion",
]


# ==========================================
# 🗄️ 3. BASE DE DATOS SQLITE
# ==========================================
def init_db():
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS arboles (
            codigo TEXT PRIMARY KEY,
            codigo_qr TEXT,
            nombre_comun TEXT,
            nombre_cientifico TEXT,
            familia TEXT,
            genero TEXT,
            especie TEXT,
            origen TEXT,
            latitud REAL,
            longitud REAL,
            altitud REAL,
            direccion TEXT,
            barrio TEXT,
            comuna TEXT,
            sector TEXT,
            coord_magna TEXT,
            dap REAL,
            altura_total REAL,
            altura_fuste REAL,
            diametro_mayor_copa REAL,
            diametro_menor_copa REAL,
            area_copa REAL,
            estado_fuste TEXT,
            inclinacion TEXT,
            cavidades_descortezamiento TEXT,
            ramas_secas TEXT,
            raices_expuestas TEXT,
            plagas TEXT,
            enfermedades TEXT,
            sintomas TEXT,
            porcentaje_afectacion REAL,
            estado_copa TEXT,
            estado_general TEXT,
            riesgo_volcamiento TEXT,
            riesgo_caida_ramas TEXT,
            interferencia_redes TEXT,
            infraestructura_movilidad TEXT,
            emplazamiento TEXT,
            infraestructura TEXT,
            manejo TEXT,
            priorizacion TEXT,
            evidencia_fuste TEXT,
            evidencia_copa TEXT,
            evidencia_afectaciones TEXT,
            evidencia_general TEXT,
            fecha_inventario TEXT,
            responsable TEXT,
            fecha_actualizacion TEXT,
            intervencion_realizada TEXT,
            nueva_evaluacion TEXT
        )
    """)
  conn.commit()
  conn.close()


def insertar_datos_prueba():
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("SELECT COUNT(*) FROM arboles")
  if c.fetchone()[0] == 0:
    arboles_demo = [
        (
            "ARB-001",
            "QR-ARB-001",
            "Urapán",
            "Fraxinus uhdei",
            "Oleaceae",
            "Fraxinus",
            "uhdei",
            "Introducido",
            1.213611,
            -77.281111,
            2527.0,
            "Av. los Estudiantes",
            "Palermo",
            "Comuna 9",
            "Norte",
            "N: 123456, E: 654321",
            35.0,
            8.5,
            3.0,
            5.0,
            4.2,
            16.5,
            "Bueno",
            "Ninguna",
            "Sin cavidades",
            "Escasas",
            "No",
            "Ninguna",
            "Ninguna",
            "Sin síntomas",
            0.0,
            "Buena",
            "Bueno",
            "Bajo",
            "Bajo",
            "No",
            "Adecuada",
            "Separador",
            "Redes eléctricas",
            "Poda de mantenimiento",
            "Prioridad Baja",
            "",
            "",
            "",
            "",
            "2026-08-18",
            "Equipo Ambiental SEPAL",
            "",
            "",
            "",
        ),
        (
            "ARB-002",
            "QR-ARB-002",
            "Sangregao",
            "Croton magdalenensis",
            "Euphorbiaceae",
            "Croton",
            "magdalenensis",
            "Nativo",
            1.214500,
            -77.280500,
            2530.0,
            "Av. los Estudiantes - Esquina Cra 39",
            "Palermo",
            "Comuna 9",
            "Norte",
            "N: 123480, E: 654350",
            22.0,
            4.5,
            2.0,
            3.5,
            3.0,
            8.2,
            "Excelente",
            "Ninguna",
            "Sin cavidades",
            "Ninguna",
            "No",
            "Ninguna",
            "Ninguna",
            "Sin síntomas",
            0.0,
            "Excelente",
            "Excelente",
            "Bajo",
            "Bajo",
            "No",
            "Adecuada",
            "Andén",
            "Ninguna",
            "Mantenimiento regular",
            "Prioridad Baja",
            "",
            "",
            "",
            "",
            "2026-08-18",
            "Equipo Ambiental SEPAL",
            "",
            "",
            "",
        ),
    ]
    c.executemany(
        """
            INSERT INTO arboles VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """,
        arboles_demo,
    )
    conn.commit()
  conn.close()


def obtener_arboles():
  conn = sqlite3.connect("arboles.db")
  df = pd.read_sql_query("SELECT * FROM arboles", conn)
  conn.close()
  return df


def agregar_actualizar_arbol(datos: dict):
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  columnas = ", ".join(datos.keys())
  placeholders = ", ".join(["?"] * len(datos))
  sql = f"INSERT OR REPLACE INTO arboles ({columnas}) VALUES ({placeholders})"
  c.execute(sql, list(datos.values()))
  conn.commit()
  conn.close()


def cargar_dataframe_masivo(df_excel: pd.DataFrame):
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()

  df_excel.columns = df_excel.columns.str.strip()

  for col in CAMPOS_BD:
    if col not in df_excel.columns:
      df_excel[col] = None

  df_excel = df_excel[CAMPOS_BD]
  df_excel["codigo"] = df_excel["codigo"].astype(str).str.strip()
  df_excel = df_excel[
      (df_excel["codigo"] != "")
      & (df_excel["codigo"] != "nan")
      & (df_excel["codigo"].notna())
  ]

  df_excel = df_excel.astype(object).where(pd.notna(df_excel), None)
  registros = df_excel.to_dict(orient="records")

  columnas_str = ", ".join(CAMPOS_BD)
  placeholders = ", ".join(["?"] * len(CAMPOS_BD))
  sql = f"INSERT OR REPLACE INTO arboles ({columnas_str}) VALUES ({placeholders})"

  for reg in registros:
    valores = [reg[col] for col in CAMPOS_BD]
    c.execute(sql, valores)

  conn.commit()
  conn.close()


def eliminar_arbol(codigo):
  conn = sqlite3.connect("arboles.db")
  c = conn.cursor()
  c.execute("DELETE FROM arboles WHERE codigo = ?", (codigo,))
  conn.commit()
  conn.close()


init_db()
insertar_datos_prueba()


# ==========================================
# 🗺️ 4. MAPA SATELITAL HD (CORREGIDO)
# ==========================================
def generar_mapa_html(df):
  if df.empty:
    return "<div style='color: #ff4d4d; padding: 10px;'>⚠️ No hay registros cargados.</div>"

  df_mapa = df.copy()

  if "lat" in df_mapa.columns and "latitud" not in df_mapa.columns:
    df_mapa.rename(columns={"lat": "latitud", "lon": "longitud"}, inplace=True)

  # Asegurar conversión a numérico por si vienen como string desde Excel
  df_mapa["latitud"] = pd.to_numeric(df_mapa["latitud"], errors="coerce")
  df_mapa["longitud"] = pd.to_numeric(df_mapa["longitud"], errors="coerce")

  df_valido = df_mapa.dropna(subset=["latitud", "longitud"])
  df_valido = df_valido[
      (df_valido["latitud"] != 0) & (df_valido["longitud"] != 0)
  ]

  if df_valido.empty:
    return """
        <div style='background: rgba(255,0,0,0.15); border: 1px solid #ff4d4d; color: #ff9999; padding: 15px; border-radius: 10px; font-family: Arial;'>
            ⚠️ No se encontraron registros con coordenadas GPS válidas. Ingresa al Panel Administrador para georreferenciar.
        </div>
        """

  puntos_js = []
  for _, r in df_valido.iterrows():
    color = (
        "#76ff03"
        if str(r.get("origen", "")).strip().capitalize() == "Nativo"
        else "#ff3d00"
    )
    codigo = str(r.get("codigo") or "S/C")
    nombre = str(r.get("nombre_comun") or "Árbol")
    cientifico = str(r.get("nombre_cientifico") or "")
    dap = str(r.get("dap") or "N/A")
    altura = str(r.get("altura_total") or "N/A")
    estado = str(r.get("estado_general") or "N/A")
    direccion = str(r.get("direccion") or "Sin dirección")

    popup = f"""
        <div style='font-family: Arial; font-size: 12px; width: 210px;'>
            <b style='color: #2e7d32; font-size: 14px;'>🌳 {codigo} - {nombre}</b><br>
            <b>Especie:</b> <i>{cientifico}</i><br>
            <b>DAP:</b> {dap} cm | <b>Altura:</b> {altura} m<br>
            <b>Estado:</b> {estado}<br>
            <b>Ubicación:</b> {direccion}
        </div>
        """

    # Limpieza total de saltos de línea y escape de comillas
    popup_clean = (
        popup.replace("\r", "")
        .replace("\n", "")
        .replace("'", "\\'")
        .replace('"', "&quot;")
    )

    lat_val = r["latitud"]
    lng_val = r["longitud"]

    # ✅ Sintaxis corregida: lat_val y lng_val sin corchetes dobles
    puntos_js.append(f"""
            L.circleMarker([{lat_val}, {lng_val}], {{
                radius: 8,
                fillColor: "{color}",
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            }}).addTo(map).bindPopup('{popup_clean}');
        """)

  js_markers = "\n".join(puntos_js)
  lat_center = float(df_valido["latitud"].mean())
  lng_center = float(df_valido["longitud"].mean())

  # ✅ Sintaxis corregida: setView([lat_center, lng_center], 17)
  html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; height: 100%; width: 100%; }}
            #map {{ width: 100%; height: 100vh; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{lat_center}, {lng_center}], 17);
            
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19,
                attribution: 'Esri World Imagery'
            }}).addTo(map);

            {js_markers}
        </script>
    </body>
    </html>
    """
  return html_code

# ==========================================
# 🖼️ 5. ENCABEZADO Y LOGO
# ==========================================
col_espacio1, col_logo, col_espacio2 = st.columns([1, 4, 1])
with col_logo:
  if os.path.exists(LOGO_LOCAL):
    st.image(LOGO_LOCAL, width="stretch")
  else:
    st.image(LOGO_SEPAL_URL, width="stretch")

st.markdown(
    "<h1 style='text-align: center; margin-top: -15px;'>Programa Smart Vita</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #80ed99; font-size: 1.1em;'>🌿"
    " Caracterización Arbórea y Cobertura Vegetal | Avenida de los Estudiantes,"
    " Pasto</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# 🧭 6. BARRA LATERAL
# ==========================================
with st.sidebar:
  st.markdown("### **Navegación Principal**")
  rol = st.radio("Ir a:", ["👤 Consulta Pública", "🛠️ Panel Administrador"])

# ==========================================
# 👤 VISTA 1: CONSULTA PÚBLICA
# ==========================================
if rol == "👤 Consulta Pública":
  df = obtener_arboles()

  st.sidebar.markdown("---")
  st.sidebar.markdown("### **Filtros de Búsqueda**")
  busqueda = st.sidebar.text_input("🔍 Buscar por Código o Nombre:")

  estados_unicos = (
      ["Todos"] + list(df["estado_general"].dropna().unique())
      if not df.empty and "estado_general" in df.columns
      else ["Todos"]
  )
  filtro_estado = st.sidebar.selectbox(
      "Filtrar por Estado General:", estados_unicos
  )

  df_filtrado = df.copy()
  if not df_filtrado.empty:
    if busqueda:
      col_cod = (
          "codigo" if "codigo" in df_filtrado.columns else df_filtrado.columns[0]
      )
      col_nom = (
          "nombre_comun"
          if "nombre_comun" in df_filtrado.columns
          else df_filtrado.columns[0]
      )
      df_filtrado = df_filtrado[
          df_filtrado[col_cod]
          .astype(str)
          .str.contains(busqueda, case=False, na=False)
          | df_filtrado[col_nom]
          .astype(str)
          .str.contains(busqueda, case=False, na=False)
      ]

    if filtro_estado != "Todos" and "estado_general" in df_filtrado.columns:
      df_filtrado = df_filtrado[df_filtrado["estado_general"] == filtro_estado]

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.markdown(
        f"<div class='metric-card'><h4>Total"
        f" Registros</h4><h2>{len(df_filtrado)}</h2></div>",
        unsafe_allow_html=True,
    )
  with c2:
    nativos = (
        len(df_filtrado[df_filtrado["origen"] == "Nativo"])
        if not df_filtrado.empty and "origen" in df_filtrado.columns
        else 0
    )
    st.markdown(
        f"<div class='metric-card'><h4>Especies"
        f" Nativas</h4><h2>{nativos}</h2></div>",
        unsafe_allow_html=True,
    )
  with c3:
    prom_dap = (
        round(df_filtrado["dap"].mean(), 1)
        if not df_filtrado.empty and "dap" in df_filtrado.columns
        else 0
    )
    st.markdown(
        f"<div class='metric-card'><h4>DAP"
        f" Promedio</h4><h2>{prom_dap} cm</h2></div>",
        unsafe_allow_html=True,
    )
  with c4:
    prom_alt = (
        round(df_filtrado["altura_total"].mean(), 1)
        if not df_filtrado.empty and "altura_total" in df_filtrado.columns
        else 0
    )
    st.markdown(
        f"<div class='metric-card'><h4>Altura"
        f" Prom.</h4><h2>{prom_alt} m</h2></div>",
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown("### 🗺️ Mapa General del Inventario Arbóreo (ArcGIS Satellite)")
  import streamlit.components.v1 as components
  components.html(generar_mapa_html(df_filtrado), height=520)

  st.markdown("### 📋 Consultar Ficha Técnica Completa")
  if not df_filtrado.empty and "codigo" in df_filtrado.columns:
    codigo_sel = st.selectbox(
        "Selecciona un código del inventario:", df_filtrado["codigo"].tolist()
    )
    arbol_info = df_filtrado[
        df_filtrado["codigo"] == codigo_sel
    ].iloc[0].to_dict()

    with st.expander(
        f"🔍 Ver Ficha Técnica Completa - {arbol_info.get('codigo')}",
        expanded=True,
    ):
      c_f1, c_f2, c_f3 = st.columns(3)
      with c_f1:
        st.write(f"**Nombre Común:** {arbol_info.get('nombre_comun')}")
        st.write(f"**Nombre Científico:** {arbol_info.get('nombre_cientifico')}")
        st.write(f"**Familia:** {arbol_info.get('familia')}")
        st.write(f"**Origen:** {arbol_info.get('origen')}")
        st.write(f"**Ubicación:** {arbol_info.get('direccion')}")
        st.write(
            f"**Barrio/Comuna:** {arbol_info.get('barrio')} /"
            f" {arbol_info.get('comuna')}"
        )
      with c_f2:
        st.write(f"**DAP:** {arbol_info.get('dap')} cm")
        st.write(f"**Altura Total:** {arbol_info.get('altura_total')} m")
        st.write(f"**Altura Fuste:** {arbol_info.get('altura_fuste')} m")
        st.write(f"**Diámetro Copa:** {arbol_info.get('diametro_mayor_copa')} m")
        st.write(f"**Estado General:** {arbol_info.get('estado_general')}")
      with c_f3:
        st.write(
            "**Coordenadas:**"
            f" {arbol_info.get('latitud')}, {arbol_info.get('longitud')}"
        )
        st.write(
            f"**Riesgo Volcamiento:** {arbol_info.get('riesgo_volcamiento')}"
        )
        st.write(
            f"**Riesgo Caída Ramas:** {arbol_info.get('riesgo_caida_ramas')}"
        )
        st.write(f"**Manejo Recomendado:** {arbol_info.get('manejo')}")
        st.write(f"**Fecha Inventario:** {arbol_info.get('fecha_inventario')}")

  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name="SmartVita")
  st.download_button(
      label="📥 Descargar Inventario en Excel",
      data=buffer.getvalue(),
      file_name="Inventario_Smart_Vita_Pasto.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )

# ==========================================
# 🛠️ VISTA 2: PANEL ADMINISTRADOR
# ==========================================
elif rol == "🛠️ Panel Administrador":
  if not st.session_state.autenticado:
    st.subheader("🔑 Acceso Administrador Smart Vita")
    with st.form("form_login"):
      usuario_ingresado = st.text_input("Usuario:")
      clave_ingresada = st.text_input("Contraseña:", type="password")
      btn_login = st.form_submit_button("Iniciar Sesión")

      if btn_login:
        if (
            usuario_ingresado == USUARIO_ADMIN
            and generar_hash(clave_ingresada) == HASH_ADMIN
        ):
          st.session_state.autenticado = True
          st.success("Acceso concedido.")
          st.rerun()
        else:
          st.error("Usuario o contraseña incorrectos.")
  else:
    st.sidebar.success(f"Sesión Activa: {USUARIO_ADMIN}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
      st.session_state.autenticado = False
      st.rerun()

    st.markdown("### 🛠️ Gestión Completa del Inventario Arbóreo")
    df = obtener_arboles()

    tab1, tab2, tab3 = st.tabs([
        "➕ Registrar / Editar Árbol",
        "📂 Carga Masiva y Respaldo (Excel)",
        "🗑️ Eliminar Registros",
    ])

    with tab1:
      opciones_edicion = ["-- Nuevo Registro --"] + (
          df["codigo"].tolist()
          if not df.empty and "codigo" in df.columns
          else []
      )
      arbol_editar_cod = st.selectbox(
          "Selecciona un código si deseas EDITAR un árbol existente:",
          opciones_edicion,
      )

      datos_prev = {}
      if arbol_editar_cod != "-- Nuevo Registro --":
        datos_prev = df[df["codigo"] == arbol_editar_cod].iloc[0].to_dict()

      with st.form("form_caracterizacion_completa"):
        st.markdown("#### 1️⃣ Ubicación y Georreferenciación")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
          codigo = st.text_input(
              "Código Árbol*", value=datos_prev.get("codigo", "ARB-003")
          )
          codigo_qr = st.text_input(
              "Código QR", value=datos_prev.get("codigo_qr", "QR-ARB-003")
          )
        with c2:
          latitud = st.number_input(
              "Latitud*",
              value=float(datos_prev.get("latitud", 1.2140)),
              format="%.6f",
          )
          longitud = st.number_input(
              "Longitud*",
              value=float(datos_prev.get("longitud", -77.2808)),
              format="%.6f",
          )
        with c3:
          altitud = st.number_input(
              "Altitud (m.s.n.m.)",
              value=float(datos_prev.get("altitud", 2528.0)),
          )
          direccion = st.text_input(
              "Dirección",
              value=datos_prev.get("direccion", "Av. los Estudiantes"),
          )
        with c4:
          barrio = st.text_input(
              "Barrio", value=datos_prev.get("barrio", "Palermo")
          )
          comuna = st.text_input(
              "Comuna", value=datos_prev.get("comuna", "Comuna 9")
          )

        c4_extra1, c4_extra2 = st.columns(2)
        with c4_extra1:
          sector = st.text_input(
              "Sector", value=datos_prev.get("sector", "Norte")
          )
        with c4_extra2:
          coord_magna = st.text_input(
              "Coordenadas Magna Sirgas",
              value=datos_prev.get("coord_magna", "N: 123450, E: 654320"),
          )

        st.markdown("---")
        st.markdown("#### 2️⃣ Taxonomía y Características Biológicas")
        c5, c6, c7, c8 = st.columns(4)
        with c5:
          nombre_comun = st.text_input(
              "Nombre Común*",
              value=datos_prev.get("nombre_comun", "Siete Cueros"),
          )
          nombre_cientifico = st.text_input(
              "Nombre Científico*",
              value=datos_prev.get("nombre_cientifico", "Tibouchina lepidota"),
          )
        with c6:
          familia = st.text_input(
              "Familia", value=datos_prev.get("familia", "Melastomataceae")
          )
          genero = st.text_input(
              "Género", value=datos_prev.get("genero", "Tibouchina")
          )
        with c7:
          especie = st.text_input(
              "Especie", value=datos_prev.get("especie", "lepidota")
          )
          origen = st.selectbox(
              "Origen",
              ["Nativo", "Introducido", "Endémico"],
              index=[
                  "Nativo",
                  "Introducido",
                  "Endémico",
              ].index(datos_prev.get("origen", "Nativo")),
          )

        st.markdown("---")
        st.markdown("#### 3️⃣ Dasometría y Estructura")
        c9, c10, c11, c12 = st.columns(4)
        with c9:
          dap = st.number_input(
              "DAP (cm)", value=float(datos_prev.get("dap", 28.0))
          )
          altura_total = st.number_input(
              "Altura Total (m)",
              value=float(datos_prev.get("altura_total", 6.5)),
          )
        with c10:
          altura_fuste = st.number_input(
              "Altura Fuste (m)",
              value=float(datos_prev.get("altura_fuste", 2.2)),
          )
          diametro_mayor_copa = st.number_input(
              "Diámetro Mayor Copa (m)",
              value=float(datos_prev.get("diametro_mayor_copa", 4.0)),
          )
        with c11:
          diametro_menor_copa = st.number_input(
              "Diámetro Menor Copa (m)",
              value=float(datos_prev.get("diametro_menor_copa", 3.5)),
          )
          area_copa = st.number_input(
              "Área Copa (m²)",
              value=float(datos_prev.get("area_copa", 11.0)),
          )

        st.markdown("---")
        st.markdown("#### 4️⃣ Fitosanidad y Estado Fitosanitario")
        c13, c14, c15, c16 = st.columns(4)
        with c13:
          estado_fuste = st.selectbox(
              "Estado Fuste",
              ["Bueno", "Regular", "Malo", "Crítico"],
              index=["Bueno", "Regular", "Malo", "Crítico"].index(
                  datos_prev.get("estado_fuste", "Bueno")
              ),
          )
          inclinacion = st.text_input(
              "Inclinación", value=datos_prev.get("inclinacion", "Ninguna")
          )
          cavidades_descortezamiento = st.text_input(
              "Cavidades / Descortezamiento",
              value=datos_prev.get(
                  "cavidades_descortezamiento", "Sin cavidades"
              ),
          )
        with c14:
          ramas_secas = st.text_input(
              "Ramas Secas", value=datos_prev.get("ramas_secas", "Escasas")
          )
          raices_expuestas = st.text_input(
              "Raíces Expuestas",
              value=datos_prev.get("raices_expuestas", "No"),
          )
          plagas = st.text_input(
              "Plagas", value=datos_prev.get("plagas", "Ninguna")
          )
        with c15:
          enfermedades = st.text_input(
              "Enfermedades", value=datos_prev.get("enfermedades", "Ninguna")
          )
          sintomas = st.text_input(
              "Síntomas", value=datos_prev.get("sintomas", "Sin síntomas")
          )
          porcentaje_afectacion = st.number_input(
              "% Afectación",
              value=float(datos_prev.get("porcentaje_afectacion", 0.0)),
          )
        with c16:
          estado_copa = st.selectbox(
              "Estado Copa",
              ["Buena", "Regular", "Mala", "Excelente"],
              index=["Buena", "Regular", "Mala", "Excelente"].index(
                  datos_prev.get("estado_copa", "Buena")
              ),
          )
          estado_general = st.selectbox(
              "Estado General*",
              ["Bueno", "Excelente", "Regular", "Crítico"],
              index=["Bueno", "Excelente", "Regular", "Crítico"].index(
                  datos_prev.get("estado_general", "Bueno")
              ),
          )

        st.markdown("---")
        st.markdown("#### 5️⃣ Evaluaciones de Riesgo y Manejo")
        c17, c18, c19, c20 = st.columns(4)
        with c17:
          riesgo_volcamiento = st.selectbox(
              "Riesgo Volcamiento",
              ["Bajo", "Medio", "Alto"],
              index=["Bajo", "Medio", "Alto"].index(
                  datos_prev.get("riesgo_volcamiento", "Bajo")
              ),
          )
          riesgo_caida_ramas = st.selectbox(
              "Riesgo Caída Ramas",
              ["Bajo", "Medio", "Alto"],
              index=["Bajo", "Medio", "Alto"].index(
                  datos_prev.get("riesgo_caida_ramas", "Bajo")
              ),
          )
        with c18:
          interferencia_redes = st.text_input(
              "Interferencia Redes",
              value=datos_prev.get("interferencia_redes", "No"),
          )
          infraestructura_movilidad = st.text_input(
              "Infraestructura / Movilidad",
              value=datos_prev.get("infraestructura_movilidad", "Adecuada"),
          )
        with c19:
          emplazamiento = st.text_input(
              "Emplazamiento",
              value=datos_prev.get("emplazamiento", "Separador Vial"),
          )
          infraestructura = st.text_input(
              "Infraestructura Cercana",
              value=datos_prev.get("infraestructura", "Redes eléctricas"),
          )
        with c20:
          manejo = st.text_input(
              "Manejo Recomendado",
              value=datos_prev.get("manejo", "Poda de mantenimiento"),
          )
          priorizacion = st.selectbox(
              "Priorización",
              ["Prioridad Baja", "Prioridad Media", "Prioridad Alta"],
              index=[
                  "Prioridad Baja",
                  "Prioridad Media",
                  "Prioridad Alta",
              ].index(datos_prev.get("priorizacion", "Prioridad Baja")),
          )

        st.markdown("---")
        st.markdown("#### 6️⃣ Control y Registro")
        c21, c22, c23 = st.columns(3)
        with c21:
          fecha_inventario = st.text_input(
              "Fecha Inventario",
              value=datos_prev.get("fecha_inventario", "2026-08-18"),
          )
        with c22:
          responsable = st.text_input(
              "Responsable",
              value=datos_prev.get("responsable", "Equipo Ambiental SEPAL"),
          )
        with c23:
          fecha_actualizacion = st.text_input(
              "Fecha Actualización",
              value=datos_prev.get("fecha_actualizacion", "2026-08-18"),
          )

        guardar = st.form_submit_button("💾 Guardar / Actualizar Árbol")

        if guardar:
          nuevo_arbol = {
              "codigo": codigo,
              "codigo_qr": codigo_qr,
              "nombre_comun": nombre_comun,
              "nombre_cientifico": nombre_cientifico,
              "familia": familia,
              "genero": genero,
              "especie": especie,
              "origen": origen,
              "latitud": latitud,
              "longitud": longitud,
              "altitud": altitud,
              "direccion": direccion,
              "barrio": barrio,
              "comuna": comuna,
              "sector": sector,
              "coord_magna": coord_magna,
              "dap": dap,
              "altura_total": altura_total,
              "altura_fuste": altura_fuste,
              "diametro_mayor_copa": diametro_mayor_copa,
              "diametro_menor_copa": diametro_menor_copa,
              "area_copa": area_copa,
              "estado_fuste": estado_fuste,
              "inclinacion": inclinacion,
              "cavidades_descortezamiento": cavidades_descortezamiento,
              "ramas_secas": ramas_secas,
              "raices_expuestas": raices_expuestas,
              "plagas": plagas,
              "enfermedades": enfermedades,
              "sintomas": sintomas,
              "porcentaje_afectacion": porcentaje_afectacion,
              "estado_copa": estado_copa,
              "estado_general": estado_general,
              "riesgo_volcamiento": riesgo_volcamiento,
              "riesgo_caida_ramas": riesgo_caida_ramas,
              "interferencia_redes": interferencia_redes,
              "infraestructura_movilidad": infraestructura_movilidad,
              "emplazamiento": emplazamiento,
              "infraestructura": infraestructura,
              "manejo": manejo,
              "priorizacion": priorizacion,
              "fecha_inventario": fecha_inventario,
              "responsable": responsable,
              "fecha_actualizacion": fecha_actualizacion,
          }
          agregar_actualizar_arbol(nuevo_arbol)
          st.success(f"✅ Árbol {codigo} guardado exitosamente.")
          st.rerun()

    with tab2:
      st.subheader("📂 Respaldo y Carga Masiva mediante Excel")
      st.info(
          "Descarga la base de datos actual para usarla como plantilla o"
          " realiza respaldos periódicos."
      )

      c_down, c_up = st.columns(2)

      with c_down:
        st.markdown("#### 1. Descargar Respaldo / Plantilla Base")
        df_export = obtener_arboles()

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
          df_export.to_excel(
              writer, index=False, sheet_name="Inventario_SmartVita"
          )

        st.download_button(
            label="⬇️ Descargar Backup / Plantilla (.xlsx)",
            data=buffer.getvalue(),
            file_name="Backup_Smart_Vita_SEPAL.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

      with c_up:
        st.markdown("#### 2. Carga Masiva desde Excel")
        archivo_excel = st.file_uploader(
            "Selecciona el archivo Excel con nuevos registros o"
            " actualizaciones:",
            type=["xlsx", "xls"],
        )

        if archivo_excel is not None:
          if st.button("🚀 Ejecutar Carga Masiva a la Base de Datos"):
            try:
              df_import = pd.read_excel(archivo_excel)
              df_import.columns = df_import.columns.str.strip()

              if "codigo" in df_import.columns:
                cargar_dataframe_masivo(df_import)
                st.success(
                    "🎉 Carga masiva completada exitosamente"
                    f" ({len(df_import)} registros procesados)."
                )
                st.rerun()
              else:
                st.error(
                    "❌ El archivo Excel debe contener la columna obligatoria"
                    " 'codigo'."
                )
            except Exception as e:
              st.error(f"❌ Error al procesar el archivo Excel: {e}")

      st.markdown("---")
      st.markdown("#### 📊 Vista previa de la Base de Datos Local")
      st.dataframe(df, width="stretch")

    with tab3:
      if not df.empty and "codigo" in df.columns:
        codigo_eliminar = st.selectbox(
            "Selecciona el código del árbol a ELIMINAR:", df["codigo"].tolist()
        )
        if st.button("❌ Eliminar Árbol Permanentemente"):
          eliminar_arbol(codigo_eliminar)
          st.warning(f"Árbol {codigo_eliminar} eliminado de la base de datos.")
          st.rerun()
