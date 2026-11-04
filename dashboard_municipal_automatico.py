import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Dashboard Municipal', page_icon='🏛️', layout='wide')
st.title('🏛️ Dashboard de Gestión Municipal')
st.caption('Atención ciudadana | Datos ficticios')

RUTA = os.path.expanduser('~/Downloads/Base_Municipal_Consolidada.xlsx')
if not os.path.isfile(RUTA):
    st.error('No se encontró Base_Municipal_Consolidada.xlsx en Descargas. Comprueba el nombre y la ubicación.')
    st.stop()

@st.cache_data
def cargar(ruta, fecha_modificacion):
    return pd.read_excel(ruta, sheet_name='Datos preparados')

try:
    df = cargar(RUTA, os.path.getmtime(RUTA))
except Exception as exc:
    st.error(f'No fue posible leer la hoja Datos preparados: {exc}')
    st.stop()

requeridas = ['Estado', 'Departamento limpio', 'Dias corridos calculados', 'Satisfaccion validada']
faltantes = [c for c in requeridas if c not in df.columns]
if faltantes:
    st.error('Faltan columnas: ' + ', '.join(faltantes))
    st.stop()

st.sidebar.header('Filtros interactivos')
departamento = df['Departamento limpio'].fillna('Sin información').astype(str)
opciones = sorted(departamento.unique().tolist())
elegidos = st.sidebar.multiselect('Departamentos', opciones, default=opciones)
datos = df.loc[departamento.isin(elegidos)].copy()

estados = datos['Estado'].fillna('').astype(str).str.strip().str.casefold()
resueltas = estados.str.contains('resuelt', regex=False)
dias = pd.to_numeric(datos['Dias corridos calculados'], errors='coerce')
evaluables = dias.loc[resueltas & dias.notna() & (dias >= 0)]
satisfaccion = pd.to_numeric(datos['Satisfaccion validada'], errors='coerce')

total = len(datos)
porcentaje_resueltas = 100 * resueltas.sum() / total if total else 0
cumplimiento = 100 * (evaluables <= 15).mean() if len(evaluables) else float('nan')
promedio = evaluables.mean()
satisfaccion_media = satisfaccion.mean()

st.subheader('Indicadores principales')
a, b, c = st.columns(3)
a.metric('Total de atenciones', f'{total:,}'.replace(',', '.'))
b.metric('Solicitudes resueltas', f'{porcentaje_resueltas:.2f}%'.replace('.', ','))
c.metric('Tiempo promedio', f'{promedio:.2f} días'.replace('.', ',') if pd.notna(promedio) else 'Sin datos')
d, e, f = st.columns(3)
d.metric('Cumplimiento de plazos', f'{cumplimiento:.2f}%'.replace('.', ',') if pd.notna(cumplimiento) else 'Sin datos')
e.metric('Satisfacción promedio', f'{satisfaccion_media:.2f} / 5'.replace('.', ',') if pd.notna(satisfaccion_media) else 'Sin datos')
f.metric('Casos evaluables para plazo', str(len(evaluables)))
st.caption('Referencia didáctica: 15 días corridos. Solo se consideran casos resueltos con duración calculada válida (≥ 0).')

izq, der = st.columns(2)
with izq:
    st.subheader('Solicitudes por estado')
    tabla_estado = datos['Estado'].fillna('Sin información').value_counts().rename_axis('Estado').reset_index(name='Cantidad')
    if not tabla_estado.empty:
        st.plotly_chart(px.bar(tabla_estado, x='Estado', y='Cantidad', color='Estado', text='Cantidad'), use_container_width=True)
    else:
        st.info('No hay datos para el filtro elegido.')
with der:
    st.subheader('Atenciones por departamento')
    tabla_depto = datos['Departamento limpio'].fillna('Sin información').value_counts().rename_axis('Departamento').reset_index(name='Atenciones')
    if not tabla_depto.empty:
        st.plotly_chart(px.bar(tabla_depto, x='Departamento', y='Atenciones', color='Departamento', text='Atenciones'), use_container_width=True)
    else:
        st.info('No hay datos para el filtro elegido.')

st.subheader('Explorar registros')
st.dataframe(datos, use_container_width=True)
st.success('Dashboard conectado al Excel local. El archivo original no se modifica.')
