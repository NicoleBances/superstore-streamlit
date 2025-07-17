import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuraciones iniciales
sns.set_style("whitegrid")
st.set_page_config(layout="wide")
st.title("Examen Final: Análisis de Ventas de Superstore")

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


st.markdown("""
**Segmento Bajo**  
- **Mediana del gasto**: S/. 688.32  
- **Rango intercuartílico (IQR)**: S/. 572.10 (Q1: S/. 351.09 – Q3: S/. 923.19)  
- **Mínimo y máximo**: S/. 4.83 – S/. 1,146.05  
- **Interpretación**: Este segmento presenta un gasto relativamente bajo, con una dispersión moderada. La mayoría de los clientes se concentran en un rango estrecho, no hay presencia de valores atípicos.  

**Segmento Medio-Bajo**  
- **Mediana del gasto**: S/. 1,651.35  
- **IQR**: S/. 570.91 (Q1: S/. 1,387.84 – Q3: S/. 1,958.75)  
- **Mínimo y máximo**: S/. 1,148.78 – S/. 2,256.39  
- **Interpretación**: Se observa un aumento significativo en el gasto respecto al segmento bajo, manteniendo una dispersión similar. no hay presencia de valores atípicos.  

**Segmento Medio-Alto**  
- **Mediana del gasto**: S/. 2,885.16  
- **IQR**: S/. 672.59 (Q1: S/. 2,563.01 – Q3: S/. 3,235.61)  
- **Mínimo y máximo**: S/. 2,258.19 – S/. 3,785.28  
- **Interpretación**: Este segmento muestra un incremento tanto en el gasto como en la dispersión. La amplitud del rango sugiere que existe una mayor diversidad en los patrones de consumo, aunque no hay presencia de valores atípicos.  

**Segmento Alto**  
- **Mediana del gasto**: S/. 5,447.33  
- **IQR**: S/. 2,943.21 (Q1: S/. 4,428.39 – Q3: S/. 7,371.60)  
- **Mínimo y máximo**: S/. 3,789.72 – S/. 25,043.05  
- **Interpretación**: Este segmento presenta la mayor variabilidad en el gasto total. La amplitud del IQR y la presencia de valores atípicos muy elevados nos dicen que hay una distribución muy dispersa, con clientes que realizan gastos superiores al promedio.
            
**La hipótesis no cumple, podemos ver que los clientes tienen comportamientos variados de compra.** 
""")

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

st.markdown("## El gráfico de barras muestra claramente que el segmento Consumer es el que más vende, con algo de 1.2 millones en ventas. Después viene Corporate, con unos 700 mil, y al final está Home Office, que tiene cerca de 400 mil. Se nota que hay una diferencia bien marcada entre los tres, así que no tendría sentido tratarlos igual. Cada segmento tiene su propio ritmo de gasto, así que lo más lógico sería aplicar estrategias distintas para cada uno.")

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

st.markdown("Este gráfico de líneas muestra cómo fueron cambiando las ventas mes a mes desde enero de 2014 hasta julio de 2017, separadas por segmento. El segmento Consumer es el que más vende durante todo el periodo, y va subiendo con algunos picos bien marcados en ciertos meses, probablemente por campañas o fechas festivas. Corporate está segundo, con ventas más estables y suaves subidas en algunos momentos. En cambio, Home Office es el que menos vende y se mantiene más plano. En resumen, cada segmento tiene su propio ritmo, tanto en volumen como en cómo cambian a lo largo del tiempo, así que claramente necesitan estrategias distintas.")

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

st.markdown("Este gráfico de barras muestra cómo se reparten las ventas a lo largo del año, y se nota clarito que hay meses donde la cosa despega. Hay subidas fuertes en marzo, septiembre y sobre todo en noviembre y diciembre, que son los meses con más ventas . O sea, en el último trimestre del año se vende un montón, debe ser por campañas, ofertas o simplemente porque la gente compra más en esas fechas. El resto del año es más tranquilo, con ventas más bajitas y parejitas.")

st.subheader("Ventas totales mensuales (línea de tiempo)")
ventas_mensuales = df_filtrado_fecha.groupby('YearMonth')['Sales'].sum()
fig5, ax5 = plt.subplots(figsize=(10, 5))
ventas_mensuales.plot(ax=ax5, marker='o')
ax5.set_title("Ventas mensuales totales")
ax5.set_ylabel("Total ventas")
st.pyplot(fig5)

st.markdown("Este gráfico de líneas muestra cómo fueron cambiando las ventas mes a mes desde enero de 2014 hasta julio de 2017. Se ve que las ventas suben y bajan con cierta regularidad, como si cada año tuvieran sus meses fuertes y sus meses flojos. Hay varios picos marcados que seguro coinciden con campañas o temporadas en que la gente compra más. Aunque hay movimiento mes a mes, en general las ventas se mantienen estables a lo largo del tiempo.")
