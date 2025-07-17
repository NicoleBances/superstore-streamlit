import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuraciones iniciales
sns.set_style("whitegrid")
st.set_page_config(layout="wide")
st.title("Análisis Interactivo de Clientes y Ventas")

# Carga de datos con caché
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Superstore.csv", encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['YearMonth'] = df['Order Date'].dt.to_period('M')
    return df

df = cargar_datos()

# Sidebar con filtros
st.sidebar.header("Filtros")
segmentos = df['Segment'].unique().tolist()
segmento_seleccionado = st.sidebar.multiselect("Selecciona segmento(s):", segmentos, default=segmentos)

# Filtro por segmento
df_filtrado = df[df['Segment'].isin(segmento_seleccionado)]

# =====================
# HIPÓTESIS 1
# =====================
st.header("Hipótesis 1: Todos los clientes tienen comportamientos de compra semejante")

gasto_por_cliente = df_filtrado.groupby('Customer ID')['Sales'].sum()
gasto_segmentado = pd.qcut(gasto_por_cliente, q=4, labels=['Bajo', 'Medio-Bajo', 'Medio-Alto', 'Alto'])

gasto_segmentado_df = pd.DataFrame({
    'Customer ID': gasto_por_cliente.index,
    'Gasto Total': gasto_por_cliente.values,
    'Segmento': gasto_segmentado
})

fig1, ax1 = plt.subplots()
sns.boxplot(data=gasto_segmentado_df, x='Segmento', y='Gasto Total', order=['Bajo', 'Medio-Bajo', 'Medio-Alto', 'Alto'], ax=ax1)
ax1.set_title("Distribución del gasto total por segmento de cliente")
st.pyplot(fig1)

# HIPÓTESIS 2: Ciertos segmentos siempre generan más venta que otros
st.header("Hipótesis 2: Ciertos segmentos siempre generan más venta que otros")

# Filtro de fechas
st.sidebar.subheader("Filtrar por fecha")
fecha_min = df['Order Date'].min()
fecha_max = df['Order Date'].max()

rango_fechas = st.sidebar.date_input(
    "Selecciona un rango de fechas:",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtrar el dataframe por fechas seleccionadas
if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado_fecha = df_filtrado[
        (df_filtrado['Order Date'] >= pd.to_datetime(fecha_inicio)) &
        (df_filtrado['Order Date'] <= pd.to_datetime(fecha_fin))
    ]
else:
    df_filtrado_fecha = df_filtrado  # Por si acaso no se selecciona bien el rango

# Ventas totales por segmento (filtradas por fecha)
st.subheader("Ventas totales por segmento")
fig2, ax2 = plt.subplots()
df_filtrado_fecha.groupby('Segment')['Sales'].sum().plot(kind='bar', ax=ax2, color='skyblue')
ax2.set_title("Ventas por segmento")
st.pyplot(fig2)

# Tendencia mensual de ventas por segmento (filtradas por fecha)
st.subheader("Tendencia mensual de ventas por segmento")
ventas_segmento = df_filtrado_fecha.groupby(['YearMonth', 'Segment'])['Sales'].sum().unstack()
fig3, ax3 = plt.subplots(figsize=(12,6))
ventas_segmento.plot(marker='o', ax=ax3)
ax3.set_title("Tendencia mensual de ventas por segmento")
ax3.set_xlabel("Mes")
ax3.set_ylabel("Ventas totales")
plt.xticks(rotation=45)
ax3.legend(title="Segmento")
st.pyplot(fig3)

# =====================
# HIPÓTESIS 3
# =====================
st.header("Hipótesis 3: No existe un mes de ventas bajas")

# Usamos el mismo df_filtrado_fecha que ya se generó con el rango de fechas
st.subheader("Ventas totales por mes (acumulado)")
fig4, ax4 = plt.subplots()
df_filtrado_fecha.groupby(df_filtrado_fecha['Order Date'].dt.month)['Sales'].sum().plot(
    kind='bar', ax=ax4, color='lightgreen')
ax4.set_title("Ventas totales por mes (1=Enero, 12=Diciembre)")
ax4.set_xlabel("Mes")
st.pyplot(fig4)

st.subheader("Ventas totales mensuales (línea de tiempo)")
ventas_mensuales = df_filtrado_fecha.groupby('YearMonth')['Sales'].sum()
fig5, ax5 = plt.subplots(figsize=(10, 5))
ventas_mensuales.plot(ax=ax5, marker='o')
ax5.set_title("Ventas mensuales totales")
ax5.set_ylabel("Total ventas")
st.pyplot(fig5)

