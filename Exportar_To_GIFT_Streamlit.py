import streamlit as st
import pandas as pd
from io import StringIO
from docx import Document

# Función para leer tablas de Word (.docx)
def read_docx_table(uploaded_file):
    doc = Document(uploaded_file)
    table = doc.tables[0]
    # Encabezados: primera fila
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    data = []
    for row in table.rows[1:]:
        data.append([cell.text.strip() for cell in row.cells])
    return pd.DataFrame(data, columns=headers)

# Título de la app
st.title("🎁 Generador de GIFT para Moodle")
st.markdown("Genera tu archivo GIFT a partir de Excel, CSV o Word.")

# Sidebar: carga de archivo
st.sidebar.header("1. Sube tu archivo")
uploaded = st.sidebar.file_uploader(
    "Selecciona Excel (.xlsx/.xls), CSV o Word (.docx)",
    type=["xlsx", "xls", "csv", "docx"]
)

if uploaded:
    # Leer datos en DataFrame
    try:
        if uploaded.name.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded, dtype=str).fillna("")
        elif uploaded.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded, dtype=str).fillna("")
        else:
            df = read_docx_table(uploaded)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # Mostrar vista previa\ n    st.subheader("Vista previa de tus preguntas")
    st.dataframe(df)

    # Botón para generar GIFT
    if st.sidebar.button("2. Generar GIFT"):
        gift_buffer = StringIO()
        for _, row in df.iterrows():
            qid = str(row.get("id", "")).strip()
            text = str(row.get("enunciado", "")).replace("\n", " ").strip()
            correct = str(row.get("correcta", "")).replace("\n", " ").strip()

            # Escribir pregunta en formato GIFT
            gift_buffer.write(f"::{qid}:: {text} {{\n")
            gift_buffer.write(f"={correct}\n")
            # Distractores dinámicos
            for i in range(1, 5):
                d = str(row.get(f"distractor{i}", "")).strip()
                if d:
                    gift_buffer.write(f"~{d}\n")
            gift_buffer.write("}\n\n")

        gift_text = gift_buffer.getvalue()
        # Descargar
        st.subheader("Descarga tu archivo GIFT")
        st.download_button(
            label="📥 Descargar examen.gift",
            data=gift_text,
            file_name="examen.gift",
            mime="text/plain"
        )
else:
    st.info("Inicia subiendo un archivo en la barra lateral para empezar.")
