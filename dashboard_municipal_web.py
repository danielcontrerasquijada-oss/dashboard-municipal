import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Dashboard Municipal | Web', page_icon='🏛️', layout='wide')
st.title('🏛️ Dashboard de Gestión Municipal')
st.caption('Demostración educativa · Utilizar exclusivamente datos ficticios o autorizados')
st.info('Sube un Excel ficticio para analizarlo. El archivo se procesa en el servidor donde está alojada esta aplicación; no cargues datos personales o confidenciales.')

archivo = st.file_uploader('Selecciona un archivo Excel (.xlsx)', type=['xlsx'])
if archivo is None:
    st.info('Para comenzar, selecciona un Excel con la hoja «Datos preparados».')
    st.stop()

try:
    libro = pd.ExcelFile(archivo)
    if 'Datos preparados' not in libro.sheet_names:
        st.error('El archivo no contiene la hoja «Datos preparados». Hojas encontradas: ' + ', '.join(libro.sheet_names))
        st.stop()
    df = pd.read_excel(libro, sheet_name='Datos preparados')
except Exception as exc:
    st.error(f'No se pudo leer el Excel: {exc}')
    st.stop()

requeridas = ['Estado', 'Departamento limpio', 'Dias corridos calculados', 'Satisfaccion validada']
faltantes = [c for c in requeridas if c not in df.columns]
if faltantes:
    st.error('Faltan columnas obligatorias: ' + ', '.join(faltantes))
    st.stop()

st.sidebar.header('Filtros interactivos')
departamentos = df['Departamento limpio'].fillna('Sin información').astype(str)
opciones = sorted(departamentos.unique().tolist())
elegidos = st.sidebar.multiselect('Departamento', opciones, default=opciones)
filtrados = df.loc[departamentos.isin(elegidos)].copy()

if 'Estado' in filtrados:
    opciones_estado = sorted(filtrados['Estado'].fillna('Sin información').astype(str).unique().tolist())
    estados_elegidos = st.sidebar.multiselect('Estado', opciones_estado, default=opciones_estado)
    filtrados = filtrados.loc[filtrados['Estado'].fillna('Sin información').astype(str).isin(estados_elegidos)].copy()

estados = filtrados['Estado'].fillna('').astype(str).str.strip().str.casefold()
resueltas = estados.str.contains('resuelt', regex=False)
dias = pd.to_numeric(filtrados['Dias corridos calculados'], errors='coerce')
evaluables = dias.loc[resueltas & dias.notna() & (dias >= 0)]
satisfaccion = pd.to_numeric(filtrados['Satisfaccion validada'], errors='coerce')

total = len(filtrados)
porcentaje = 100 * resueltas.sum() / total if total else 0
promedio = evaluables.mean()
cumplimiento = 100 * (evaluables <= 15).mean() if len(evaluables) else float('nan')
satisfaccion_media = satisfaccion.mean()

st.subheader('Indicadores principales')
a, b, c = st.columns(3)
a.metric('Total de atenciones', f'{total:,}'.replace(',', '.'))
b.metric('Solicitudes resueltas', f'{porcentaje:.2f}%'.replace('.', ','))
c.metric('Tiempo promedio', f'{promedio:.2f} días'.replace('.', ',') if pd.notna(promedio) else 'Sin datos')
d, e, f = st.columns(3)
d.metric('Cumplimiento de plazos', f'{cumplimiento:.2f}%'.replace('.', ',') if pd.notna(cumplimiento) else 'Sin datos')
e.metric('Satisfacción promedio', f'{satisfaccion_media:.2f} / 5'.replace('.', ',') if pd.notna(satisfaccion_media) else 'Sin datos')
f.metric('Casos evaluables', str(len(evaluables)))
st.caption('Indicador didáctico: plazo de 15 días corridos; se consideran solo solicitudes resueltas con duración no negativa.')

izq, der = st.columns(2)
with izq:
    st.subheader('Solicitudes por estado')
    tabla = filtrados['Estado'].fillna('Sin información').value_counts().rename_axis('Estado').reset_index(name='Cantidad')
    if not tabla.empty:
        st.plotly_chart(px.bar(tabla, x='Estado', y='Cantidad', color='Estado', text='Cantidad'), use_container_width=True)
    else:
        st.info('Sin datos para estos filtros.')
with der:
    st.subheader('Atenciones por departamento')
    tabla = filtrados['Departamento limpio'].fillna('Sin información').value_counts().rename_axis('Departamento').reset_index(name='Atenciones')
    if not tabla.empty:
        st.plotly_chart(px.bar(tabla, x='Departamento', y='Atenciones', color='Departamento', text='Atenciones'), use_container_width=True)
    else:
        st.info('Sin datos para estos filtros.')

st.subheader('Explorar registros')
st.dataframe(filtrados, use_container_width=True)
st.caption('Los datos cargados no se incorporan al repositorio GitHub. El servicio de alojamiento procesa el archivo durante la sesión.')
