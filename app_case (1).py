import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from model.simulate import Params, simulate

st.set_page_config(page_title="Caso Escuela San Gabriel", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .big-metric { font-size: 1.8rem; font-weight: bold; }
    .problem-box { 
        background-color: #fff3cd; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .insight-box { 
        background-color: #d1ecf1; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Caso: Escuela San Gabriel")
st.markdown("### Simulador de Dinámica de Sistemas para Instituciones Educativas")

# Inicialización de parámetros
if "params" not in st.session_state:
    st.session_state.params = Params()

# ========== ESCENARIOS PREDEFINIDOS ==========
def cargar_escenario(nombre: str):
    p = Params()
    
    if nombre == "Situación Actual (2024)":
        # Problema: baja continuidad, poca inversión en soluciones
        p.tasa_continuidad_jardin_primaria = 0.56
        p.nivel_articulacion = 0.3
        p.nivel_comunicacion = 0.2
        p.nivel_diferenciacion = 0.4
        p.cuota_mensual = 85000.0
        p.prop_mkt = 0.08
        
    elif nombre == "Escenario A: Comunicación y Articulación":
        # Foco en retención con inversión moderada
        p.tasa_continuidad_jardin_primaria = 0.56  # Mejorará con el tiempo
        p.nivel_articulacion = 0.85  # Espacios de articulación, reuniones, visitas
        p.nivel_comunicacion = 0.80  # Web renovada, redes activas, seguimiento
        p.nivel_diferenciacion = 0.45  # Mejora leve en inglés
        p.cuota_mensual = 87000.0  # Aumento pequeño
        p.prop_mkt = 0.10  # Mayor inversión en comunicación
        p.inversion_calidad_por_alumno = 10000.0
        
    elif nombre == "Escenario B: Diferenciación (Bilingüe)":
        # Inversión fuerte en propuesta de valor
        p.tasa_continuidad_jardin_primaria = 0.56
        p.nivel_articulacion = 0.50
        p.nivel_comunicacion = 0.60
        p.nivel_diferenciacion = 0.90  # Programa bilingüe completo
        p.cuota_mensual = 105000.0  # Aumento significativo
        p.prop_mkt = 0.12
        p.inversion_calidad_por_alumno = 15000.0
        p.costo_docente_por_aula = 1_500_000.0  # Docentes bilingües
        
    elif nombre == "Escenario C: Enfoque Económico":
        # Prioriza mantener cuota baja y eficiencia
        p.tasa_continuidad_jardin_primaria = 0.56
        p.nivel_articulacion = 0.60
        p.nivel_comunicacion = 0.65
        p.nivel_diferenciacion = 0.35
        p.cuota_mensual = 80000.0  # Rebaja para retener familias
        p.prop_mkt = 0.07
        p.inversion_calidad_por_alumno = 6000.0
        
    elif nombre == "Escenario D: Solución Integral":
        # Combinación equilibrada de todas las estrategias
        p.tasa_continuidad_jardin_primaria = 0.56
        p.nivel_articulacion = 0.90  # Máxima prioridad
        p.nivel_comunicacion = 0.85  # Inversión sostenida
        p.nivel_diferenciacion = 0.70  # Mejora significativa pero realista
        p.cuota_mensual = 95000.0  # Aumento moderado
        p.prop_mkt = 0.11
        p.inversion_calidad_por_alumno = 12000.0
        p.costo_docente_por_aula = 1_350_000.0
        
    st.session_state.params = p

# ========== SIDEBAR: SELECTOR DE ESCENARIOS ==========
st.sidebar.title("🎯 Escenarios")
st.sidebar.markdown("**Selecciona un escenario para analizar:**")

escenarios = [
    "Situación Actual (2024)",
    "Escenario A: Comunicación y Articulación",
    "Escenario B: Diferenciación (Bilingüe)",
    "Escenario C: Enfoque Económico",
    "Escenario D: Solución Integral"
]

col1, col2 = st.sidebar.columns([3, 1])
with col1:
    escenario_seleccionado = st.selectbox("", escenarios, key="escenario_selector")
with col2:
    if st.button("Cargar", use_container_width=True):
        cargar_escenario(escenario_seleccionado)
        st.rerun()

st.sidebar.divider()

# ========== SIDEBAR: PARÁMETROS AJUSTABLES ==========
st.sidebar.title("⚙️ Parámetros Clave")

with st.sidebar.expander("📊 Variables de Decisión", expanded=True):
    st.session_state.params.nivel_articulacion = st.slider(
        "Articulación Jardín-Primaria",
        0.0, 1.0, st.session_state.params.nivel_articulacion, 0.05,
        help="Espacios de integración, reuniones con familias, visitas pedagógicas"
    )
    st.session_state.params.nivel_comunicacion = st.slider(
        "Calidad de Comunicación",
        0.0, 1.0, st.session_state.params.nivel_comunicacion, 0.05,
        help="Web actualizada, redes sociales activas, seguimiento a familias"
    )
    st.session_state.params.nivel_diferenciacion = st.slider(
        "Nivel de Diferenciación",
        0.0, 1.0, st.session_state.params.nivel_diferenciacion, 0.05,
        help="Calidad de la propuesta educativa (inglés, tecnología, innovación)"
    )

with st.sidebar.expander("💰 Aspectos Económicos"):
    st.session_state.params.cuota_mensual = st.number_input(
        "Cuota Mensual ($)",
        min_value=50000.0, max_value=150000.0,
        value=st.session_state.params.cuota_mensual,
        step=5000.0
    )
    st.session_state.params.inversion_calidad_por_alumno = st.number_input(
        "Inversión en Calidad ($/alumno/año)",
        min_value=0.0, max_value=30000.0,
        value=st.session_state.params.inversion_calidad_por_alumno,
        step=1000.0
    )
    st.session_state.params.prop_mkt = st.slider(
        "% Inversión en Marketing",
        0.0, 0.20, st.session_state.params.prop_mkt, 0.01
    )

with st.sidebar.expander("📉 Contexto Externo"):
    st.session_state.params.tasa_descenso_demanda = st.slider(
        "Tasa Descenso Demanda (crisis + natalidad)",
        0.0, 0.15, st.session_state.params.tasa_descenso_demanda, 0.01
    )
    st.session_state.params.demanda_potencial_inicial = st.number_input(
        "Demanda Potencial Inicial",
        min_value=100, max_value=1000,
        value=st.session_state.params.demanda_potencial_inicial,
        step=50
    )

with st.sidebar.expander("🎓 Parámetros Académicos"):
    st.session_state.params.tasa_continuidad_jardin_primaria = st.slider(
        "Tasa de Continuidad Jardín→Primaria",
        0.30, 1.0, st.session_state.params.tasa_continuidad_jardin_primaria, 0.01,
        help="% de familias del jardín que continúan en primaria"
    )
    st.session_state.params.politica_seleccion = st.slider(
        "% Candidatos Admitidos",
        0.50, 1.0, st.session_state.params.politica_seleccion, 0.05
    )

# ========== SIMULACIÓN ==========
p = st.session_state.params
df, _ = simulate(p)

# ========== TABS ==========
tab_contexto, tab_dashboard, tab_retención, tab_financiero, tab_comparar = st.tabs(
    ["📖 Contexto del Caso", "📊 Dashboard", "🎯 Retención", "💰 Análisis Financiero", "⚖️ Comparar Escenarios"]
)

# ========== TAB: CONTEXTO ==========
with tab_contexto:
    st.markdown("""
    ## 🏫 La Escuela San Gabriel
    
    Institución privada con 25 años de historia en un barrio residencial de clase media.
    Reconocida por su clima familiar y buen nivel académico.
    """)
    
    st.markdown('<div class="problem-box">', unsafe_allow_html=True)
    st.markdown("""
    ### ⚠️ El Problema
    
    **La inscripción para primer grado cayó un 30% este año.**
    
    | Año | Sala de 5 | 1° Grado | Tasa de Continuidad |
    |-----|-----------|----------|---------------------|
    | 2022 | 48 | 46 | 95% |
    | 2023 | 50 | 42 | 84% |
    | 2024 | 52 | 29 | **56%** |
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 Hallazgos Clave
        
        **Encuesta a familias que NO reinscribieron:**
        - 50% eligieron colegios bilingües o con jornada extendida
        - 28% mencionaron temor al salto pedagógico
        - 17% problemas económicos
        - 5% mudanza
        
        **Contexto externo:**
        - Caída del 18% en natalidad (últimos 5 años)
        - 22% de familias migraron a escuelas públicas
        - Dos nuevas escuelas privadas con promociones
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Insights
        
        **Problema de retención interna:**
        - La cantidad en jardín no bajó
        - La pérdida ocurre en la transición jardín→primaria
        - Sin articulación pedagógica entre niveles
        - Comunicación deficiente con familias
        
        **Oportunidad:**
        - De 29 inscriptos en 1°, 15 vienen de afuera
        - Buena imagen externa, debilidad en retención
        """)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 La Pregunta Central
    
    **¿Cómo recuperar la continuidad entre jardín y primaria sin comprometer 
    la sustentabilidad económica de la institución?**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB: DASHBOARD ==========
with tab_dashboard:
    st.header("📊 Panel de Control")
    
    # Métricas principales
    inicial = df.iloc[0]
    final = df.iloc[-1]
    mitad = df.iloc[len(df)//2]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_alumnos = int(final['AlumnosTotales'] - inicial['AlumnosTotales'])
        st.metric(
            "Alumnos Totales",
            f"{int(final['AlumnosTotales'])}",
            f"{delta_alumnos:+d}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Calidad Final",
            f"{final['Calidad']:.2f}",
            f"{(final['Calidad'] - inicial['Calidad']):.2f}",
            delta_color="normal"
        )
    
    with col3:
        cont_final = final['TasaContinuidad']
        cont_inicial = inicial['TasaContinuidad'] if inicial['TasaContinuidad'] > 0 else p.tasa_continuidad_jardin_primaria
        st.metric(
            "Tasa Continuidad",
            f"{cont_final:.1%}",
            f"{(cont_final - cont_inicial):.1%}",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "Resultado Neto (Año 10)",
            f"${final['ResultadoNeto']:,.0f}",
            f"Margen: {final['MargenNeto']:.1%}"
        )
    
    with col5:
        st.metric(
            "Caja Final",
            f"${final['Caja']:,.0f}",
            f"vs Inicial: {((final['Caja']/inicial['Caja'])-1):.1%}" if inicial['Caja'] > 0 else "N/A"
        )
    
    st.divider()
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de Matrícula")
        chart_data = df[['Año', 'AlumnosTotales', 'DemandaPotencial']].copy()
        chart_data = chart_data.melt('Año', var_name='Serie', value_name='Cantidad')
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Año:Q', title='Año'),
            y=alt.Y('Cantidad:Q', title='Cantidad de Alumnos'),
            color=alt.Color('Serie:N', legend=alt.Legend(title="Serie")),
            tooltip=['Año', 'Serie', 'Cantidad']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Calidad Percibida")
        chart = alt.Chart(df).mark_line(point=True, color='#17a2b8').encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Calidad:Q', scale=alt.Scale(domain=[0, 1]), title='Calidad (0-1)'),
            tooltip=['Año', 'Calidad']
        ).properties(height=300)
        
        # Línea de referencia
        ref_line = alt.Chart(pd.DataFrame({'y': [0.7]})).mark_rule(
            color='red', strokeDash=[5, 5]
        ).encode(y='y:Q')
        
        st.altair_chart(chart + ref_line, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resultado Operativo vs Neto")
        chart_data = df[['Año', 'ResultadoOperativo', 'ResultadoNeto']].copy()
        chart_data = chart_data.melt('Año', var_name='Tipo', value_name='Monto')
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Monto:Q', title='$ por año'),
            color='Tipo:N',
            tooltip=['Año', 'Tipo', alt.Tooltip('Monto:Q', format='$,.0f')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Composición de Ingresos")
        chart_data = df[['Año', 'NuevosCandidatosMkt', 'NuevosCandidatosQ']].copy()
        chart_data.columns = ['Año', 'Candidatos Pagados (Mkt)', 'Candidatos Orgánicos (Calidad)']
        chart_data = chart_data.melt('Año', var_name='Origen', value_name='Cantidad')
        
        chart = alt.Chart(chart_data).mark_area().encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Cantidad:Q', title='Candidatos', stack='zero'),
            color=alt.Color('Origen:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Origen', 'Cantidad']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)

# ========== TAB: RETENCIÓN ==========
with tab_retención:
    st.header("🎯 Análisis de Retención")
    
    st.markdown("""
    Este análisis se enfoca en el problema central del caso: **la pérdida de alumnos 
    en la transición entre jardín y primaria**.
    """)
    
    # Métricas de retención
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tasa_cont_promedio = df['TasaContinuidad'].replace(0, np.nan).mean()
        st.metric(
            "Continuidad Promedio",
            f"{tasa_cont_promedio:.1%}",
            f"Objetivo: 85%",
            delta_color="off"
        )
    
    with col2:
        bajas_cont_total = df['BajasNoContinuidad'].sum()
        st.metric(
            "Pérdidas por No Continuidad",
            f"{int(bajas_cont_total)}",
            "alumnos en 10 años"
        )
    
    with col3:
        ingreso_perdido = bajas_cont_total * p.cuota_mensual * p.meses
        st.metric(
            "Ingreso Perdido",
            f"${ingreso_perdido:,.0f}",
            "por no retención"
        )
    
    with col4:
        calidad_promedio = df['Calidad'].mean()
        st.metric(
            "Calidad Promedio",
            f"{calidad_promedio:.2f}",
            f"{(calidad_promedio - p.calidad_base):.2f}",
            delta_color="normal"
        )
    
    st.divider()
    
    # Gráfico de continuidad en el tiempo
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de la Tasa de Continuidad")
        
        # Preparar datos
        df_cont = df[df['TasaContinuidad'] > 0].copy()
        
        chart = alt.Chart(df_cont).mark_line(point=True, color='#28a745', size=3).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('TasaContinuidad:Q', 
                    scale=alt.Scale(domain=[0, 1]),
                    axis=alt.Axis(format='%'),
                    title='Tasa de Continuidad'),
            tooltip=['Año', alt.Tooltip('TasaContinuidad:Q', format='.1%')]
        ).properties(height=350)
        
        # Líneas de referencia
        ref_actual = alt.Chart(pd.DataFrame({'y': [0.56], 'label': ['Situación 2024']})).mark_rule(
            color='red', strokeDash=[5, 5]
        ).encode(
            y='y:Q',
            tooltip=['label']
        )
        
        ref_objetivo = alt.Chart(pd.DataFrame({'y': [0.85], 'label': ['Objetivo']})).mark_rule(
            color='blue', strokeDash=[3, 3]
        ).encode(
            y='y:Q',
            tooltip=['label']
        )
        
        st.altair_chart(chart + ref_actual + ref_objetivo, use_container_width=True)
        
        st.caption("🔴 Rojo: Situación 2024 (56%) | 🔵 Azul: Objetivo (85%)")
    
    with col2:
        st.subheader("Factores que Impactan la Retención")
        
        # Mostrar valores actuales de los factores
        factores = pd.DataFrame({
            'Factor': [
                'Articulación Jardín-Primaria',
                'Comunicación con Familias',
                'Diferenciación Pedagógica',
                'Calidad General'
            ],
            'Nivel': [
                p.nivel_articulacion,
                p.nivel_comunicacion,
                p.nivel_diferenciacion,
                df['Calidad'].mean()
            ]
        })
        
        chart = alt.Chart(factores).mark_bar().encode(
            x=alt.X('Nivel:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
            y=alt.Y('Factor:N', sort='-x', title=''),
            color=alt.Color('Nivel:Q', 
                           scale=alt.Scale(scheme='blues'),
                           legend=None),
            tooltip=['Factor', alt.Tooltip('Nivel:Q', format='.1%')]
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Análisis de bajas
    st.subheader("Composición de Bajas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart_data = df[['Año', 'BajasNoContinuidad', 'BajasTotales']].copy()
        chart_data['BajasOtras'] = chart_data['BajasTotales'] - chart_data['BajasNoContinuidad']
        chart_data = chart_data[['Año', 'BajasNoContinuidad', 'BajasOtras']]
        chart_data.columns = ['Año', 'No Continuidad Jardín→Primaria', 'Otras Bajas']
        chart_data = chart_data.melt('Año', var_name='Tipo', value_name='Cantidad')
        
        chart = alt.Chart(chart_data).mark_area().encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Cantidad:Q', title='Alumnos que se van', stack='zero'),
            color=alt.Color('Tipo:N', 
                           scale=alt.Scale(domain=['No Continuidad Jardín→Primaria', 'Otras Bajas'],
                                         range=['#dc3545', '#6c757d'])),
            tooltip=['Año', 'Tipo', 'Cantidad']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("""
        ### 💡 Insight
        
        Las **bajas por no continuidad** 
        entre jardín y primaria representan 
        una pérdida significativa que puede 
        ser revertida con:
        
        - ✅ Mejor articulación pedagógica
        - ✅ Comunicación proactiva
        - ✅ Propuesta de valor clara
        - ✅ Acompañamiento a familias
        
        Estas acciones no requieren 
        grandes inversiones en CAPEX.
        """)

# ========== TAB: FINANCIERO ==========
with tab_financiero:
    st.header("💰 Análisis Financiero")
    
    # Métricas financieras clave
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        fact_total = df['Facturacion'].sum()
        st.metric("Facturación Acumulada", f"${fact_total:,.0f}")
    
    with col2:
        resultado_acum = df['ResultadoNeto'].sum()
        st.metric("Resultado Neto Acumulado", f"${resultado_acum:,.0f}")
    
    with col3:
        margen_prom = df['MargenNeto'].mean()
        st.metric("Margen Neto Promedio", f"{margen_prom:.1%}")
    
    with col4:
        st.metric("Caja Final", f"${final['Caja']:,.0f}")
    
    with col5:
        st.metric("Deuda Final", f"${final['Deuda']:,.0f}")
    
    st.divider()
    
    # Gráficos financieros
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Facturación vs Costos Totales")
        
        chart_data = df[['Año', 'Facturacion', 'CostosTotalesCash']].copy()
        chart_data.columns = ['Año', 'Facturación', 'Costos Totales']
        chart_data = chart_data.melt('Año', var_name='Concepto', value_name='Monto')
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Monto:Q', title='$ por año'),
            color=alt.Color('Concepto:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Concepto', alt.Tooltip('Monto:Q', format='$,.0f')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Márgenes Operativo y Neto")
        
        chart_data = df[['Año', 'MargenOperativo', 'MargenNeto']].copy()
        chart_data.columns = ['Año', 'Margen Operativo', 'Margen Neto']
        chart_data = chart_data.melt('Año', var_name='Tipo', value_name='Porcentaje')
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Porcentaje:Q', axis=alt.Axis(format='%'), title='Margen'),
            color='Tipo:N',
            tooltip=['Año', 'Tipo', alt.Tooltip('Porcentaje:Q', format='.1%')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Composición de OPEX
    st.subheader("Composición de Costos Operativos")
    
    chart_data = df[['Año', 'Sueldos', 'Marketing', 'InversionCalidadAlumno', 
                      'InversionInfra', 'Mantenimiento']].copy()
    chart_data = chart_data.melt('Año', var_name='Concepto', value_name='Monto')
    
    chart = alt.Chart(chart_data).mark_area().encode(
        x=alt.X('Año:Q'),
        y=alt.Y('Monto:Q', title='$ por año', stack='normalize'),
        color=alt.Color('Concepto:N', scale=alt.Scale(scheme='tableau10')),
        tooltip=['Año', 'Concepto', alt.Tooltip('Monto:Q', format='$,.0f')]
    ).properties(height=350)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Análisis de sensibilidad a cuota
    st.divider()
    st.subheader("💡 Sensibilidad: Impacto de la Cuota Mensual")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        **Cuota actual:** ${p.cuota_mensual:,.0f}
        
        **Cuota de referencia (2024):** $85.000
        
        **Competencia:**
        - Jardín Arco Iris: $75.000
        - Colegio Horizonte: $95.000 (bilingüe)
        
        Un aumento de cuota puede:
        - ✅ Mejorar resultados financieros
        - ⚠️ Aumentar bajas por precio
        - ⚠️ Reducir competitividad
        """)
    
    with col2:
        # Simulación rápida con diferentes cuotas
        cuotas_test = [75000, 80000, 85000, 90000, 95000, 100000, 110000]
        resultados_cuota = []
        
        for cuota in cuotas_test:
            p_test = Params()
            # Copiar parámetros actuales
            for attr in ['nivel_articulacion', 'nivel_comunicacion', 'nivel_diferenciacion',
                        'tasa_continuidad_jardin_primaria']:
                setattr(p_test, attr, getattr(p, attr))
            p_test.cuota_mensual = cuota
            df_test, _ = simulate(p_test)
            
            resultados_cuota.append({
                'Cuota': cuota,
                'Facturación Total': df_test['Facturacion'].sum(),
                'Resultado Neto Total': df_test['ResultadoNeto'].sum(),
                'Alumnos Finales': df_test['AlumnosTotales'].iloc[-1]
            })
        
        df_sensib = pd.DataFrame(resultados_cuota)
        
        # Gráfico
        chart1 = alt.Chart(df_sensib).mark_line(point=True, color='#28a745').encode(
            x=alt.X('Cuota:Q', axis=alt.Axis(format='$,.0f'), title='Cuota Mensual'),
            y=alt.Y('Resultado Neto Total:Q', title='Resultado Neto Acumulado ($)'),
            tooltip=[alt.Tooltip('Cuota:Q', format='$,.0f'), 
                    alt.Tooltip('Resultado Neto Total:Q', format='$,.0f')]
        )
        
        chart2 = alt.Chart(df_sensib).mark_line(point=True, color='#007bff').encode(
            x=alt.X('Cuota:Q', axis=alt.Axis(format='$,.0f')),
            y=alt.Y('Alumnos Finales:Q', title='Alumnos al Año 10'),
            tooltip=[alt.Tooltip('Cuota:Q', format='$,.0f'), 
                    'Alumnos Finales:Q']
        )
        
        combined = alt.layer(chart1, chart2).resolve_scale(y='independent').properties(height=300)
        st.altair_chart(combined, use_container_width=True)

# ========== TAB: COMPARAR ESCENARIOS ==========
with tab_comparar:
    st.header("⚖️ Comparación de Escenarios")
    
    st.markdown("""
    Aquí puedes comparar los diferentes escenarios propuestos para ver cuál ofrece 
    el mejor balance entre matrícula, calidad y sustentabilidad financiera.
    """)
    
    # Simulación de todos los escenarios
    escenarios_comparar = {
        "Situación Actual": Params(
            tasa_continuidad_jardin_primaria=0.56,
            nivel_articulacion=0.3,
            nivel_comunicacion=0.2,
            nivel_diferenciacion=0.4,
            cuota_mensual=85000.0
        ),
        "Escenario A\n(Comunicación)": Params(
            tasa_continuidad_jardin_primaria=0.56,
            nivel_articulacion=0.85,
            nivel_comunicacion=0.80,
            nivel_diferenciacion=0.45,
            cuota_mensual=87000.0,
            prop_mkt=0.10,
            inversion_calidad_por_alumno=10000.0
        ),
        "Escenario B\n(Bilingüe)": Params(
            tasa_continuidad_jardin_primaria=0.56,
            nivel_articulacion=0.50,
            nivel_comunicacion=0.60,
            nivel_diferenciacion=0.90,
            cuota_mensual=105000.0,
            prop_mkt=0.12,
            inversion_calidad_por_alumno=15000.0,
            costo_docente_por_aula=1_500_000.0
        ),
        "Escenario C\n(Económico)": Params(
            tasa_continuidad_jardin_primaria=0.56,
            nivel_articulacion=0.60,
            nivel_comunicacion=0.65,
            nivel_diferenciacion=0.35,
            cuota_mensual=80000.0,
            prop_mkt=0.07,
            inversion_calidad_por_alumno=6000.0
        ),
        "Escenario D\n(Integral)": Params(
            tasa_continuidad_jardin_primaria=0.56,
            nivel_articulacion=0.90,
            nivel_comunicacion=0.85,
            nivel_diferenciacion=0.70,
            cuota_mensual=95000.0,
            prop_mkt=0.11,
            inversion_calidad_por_alumno=12000.0,
            costo_docente_por_aula=1_350_000.0
        )
    }
    
    # Simular todos los escenarios
    resultados_comparacion = {}
    
    with st.spinner("Simulando escenarios..."):
        for nombre, params in escenarios_comparar.items():
            df_esc, _ = simulate(params)
            resultados_comparacion[nombre] = {
                'df': df_esc,
                'params': params
            }
    
    # Tabla comparativa de resultados clave
    st.subheader("📊 Resumen Comparativo (Año 10)")
    
    comparativo = []
    for nombre, resultado in resultados_comparacion.items():
        df_esc = resultado['df']
        p_esc = resultado['params']
        final_esc = df_esc.iloc[-1]
        
        comparativo.append({
            'Escenario': nombre.replace('\n', ' '),
            'Alumnos Finales': int(final_esc['AlumnosTotales']),
            'Calidad Final': f"{final_esc['Calidad']:.2f}",
            'Continuidad Promedio': f"{df_esc['TasaContinuidad'].replace(0, np.nan).mean():.1%}",
            'Facturación Año 10': f"${final_esc['Facturacion']:,.0f}",
            'Resultado Neto Año 10': f"${final_esc['ResultadoNeto']:,.0f}",
            'Margen Neto Año 10': f"{final_esc['MargenNeto']:.1%}",
            'Caja Final': f"${final_esc['Caja']:,.0f}",
            'Cuota Mensual': f"${p_esc.cuota_mensual:,.0f}"
        })
    
    df_comparativo = pd.DataFrame(comparativo)
    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de Matrícula por Escenario")
        
        # Combinar datos de todos los escenarios
        df_combined = pd.DataFrame()
        for nombre, resultado in resultados_comparacion.items():
            df_temp = resultado['df'][['Año', 'AlumnosTotales']].copy()
            df_temp['Escenario'] = nombre
            df_combined = pd.concat([df_combined, df_temp])
        
        chart = alt.Chart(df_combined).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('AlumnosTotales:Q', title='Alumnos Totales'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Escenario', 'AlumnosTotales']
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Calidad Percibida por Escenario")
        
        df_combined = pd.DataFrame()
        for nombre, resultado in resultados_comparacion.items():
            df_temp = resultado['df'][['Año', 'Calidad']].copy()
            df_temp['Escenario'] = nombre
            df_combined = pd.concat([df_combined, df_temp])
        
        chart = alt.Chart(df_combined).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Calidad:Q', scale=alt.Scale(domain=[0, 1]), title='Calidad (0-1)'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Escenario', alt.Tooltip('Calidad:Q', format='.2f')]
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resultado Neto Acumulado")
        
        df_combined = pd.DataFrame()
        for nombre, resultado in resultados_comparacion.items():
            df_temp = resultado['df'][['Año', 'ResultadoNeto']].copy()
            df_temp['ResultadoNetoAcum'] = df_temp['ResultadoNeto'].cumsum()
            df_temp['Escenario'] = nombre
            df_combined = pd.concat([df_combined, df_temp[['Año', 'ResultadoNetoAcum', 'Escenario']]])
        
        chart = alt.Chart(df_combined).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('ResultadoNetoAcum:Q', title='Resultado Neto Acumulado ($)'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Escenario', alt.Tooltip('ResultadoNetoAcum:Q', format='$,.0f')]
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Evolución de Caja")
        
        df_combined = pd.DataFrame()
        for nombre, resultado in resultados_comparacion.items():
            df_temp = resultado['df'][['Año', 'Caja']].copy()
            df_temp['Escenario'] = nombre
            df_combined = pd.concat([df_combined, df_temp])
        
        chart = alt.Chart(df_combined).mark_line(point=True).encode(
            x=alt.X('Año:Q'),
            y=alt.Y('Caja:Q', title='Caja ($)'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Año', 'Escenario', alt.Tooltip('Caja:Q', format='$,.0f')]
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Análisis de trade-offs
    st.subheader("🎯 Análisis de Trade-offs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📈 Matrícula vs Calidad
        
        ¿Qué escenario logra el mejor balance entre cantidad de alumnos y calidad educativa?
        """)
        
        # Scatter plot: Alumnos finales vs Calidad final
        scatter_data = []
        for nombre, resultado in resultados_comparacion.items():
            final_esc = resultado['df'].iloc[-1]
            scatter_data.append({
                'Escenario': nombre,
                'Alumnos': final_esc['AlumnosTotales'],
                'Calidad': final_esc['Calidad']
            })
        
        df_scatter = pd.DataFrame(scatter_data)
        
        chart = alt.Chart(df_scatter).mark_circle(size=200).encode(
            x=alt.X('Alumnos:Q', title='Alumnos Totales (Año 10)'),
            y=alt.Y('Calidad:Q', scale=alt.Scale(domain=[0, 1]), title='Calidad Final'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Escenario', 'Alumnos', alt.Tooltip('Calidad:Q', format='.2f')]
        ).properties(height=300)
        
        # Línea de referencia de calidad
        ref_line = alt.Chart(pd.DataFrame({'y': [0.7]})).mark_rule(
            color='red', strokeDash=[5, 5]
        ).encode(y='y:Q')
        
        st.altair_chart(chart + ref_line, use_container_width=True)
    
    with col2:
        st.markdown("""
        ### 💰 Rentabilidad vs Inversión
        
        ¿Qué escenario ofrece mejor retorno considerando la inversión requerida?
        """)
        
        # Scatter plot: Inversión total vs Resultado neto
        scatter_data = []
        for nombre, resultado in resultados_comparacion.items():
            df_esc = resultado['df']
            p_esc = resultado['params']
            inv_total = df_esc['InversionCalidadAlumno'].sum() + df_esc['InversionInfra'].sum()
            resultado_total = df_esc['ResultadoNeto'].sum()
            
            scatter_data.append({
                'Escenario': nombre,
                'Inversión Total': inv_total,
                'Resultado Neto Acumulado': resultado_total
            })
        
        df_scatter = pd.DataFrame(scatter_data)
        
        chart = alt.Chart(df_scatter).mark_circle(size=200).encode(
            x=alt.X('Inversión Total:Q', title='Inversión Total en Calidad e Infra ($)'),
            y=alt.Y('Resultado Neto Acumulado:Q', title='Resultado Neto Acumulado ($)'),
            color=alt.Color('Escenario:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Escenario', 
                    alt.Tooltip('Inversión Total:Q', format='$,.0f'),
                    alt.Tooltip('Resultado Neto Acumulado:Q', format='$,.0f')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Recomendaciones
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 💡 Preguntas para la Discusión
    
    1. **¿Qué escenario es más sostenible a largo plazo?**
       - Considerar equilibrio entre matrícula, calidad y finanzas
    
    2. **¿Qué riesgos implica cada estrategia?**
       - Escenario A: ¿Alcanza con mejorar comunicación?
       - Escenario B: ¿Es viable el salto de precio?
       - Escenario C: ¿Compromete la calidad?
       - Escenario D: ¿Es realista implementar todo junto?
    
    3. **¿Qué factores externos podrían cambiar el análisis?**
       - Crisis económica más profunda
       - Nueva competencia en la zona
       - Cambios demográficos
    
    4. **¿Cómo se mediría el éxito de cada estrategia?**
       - KPIs clave para monitorear
       - Hitos intermedios
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== FOOTER ==========
st.divider()
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 1rem;'>
    <small>
    Simulador de Dinámica de Sistemas - Escuela San Gabriel<br>
    Desarrollado para análisis educativo | Basado en método del caso
    </small>
</div>
""", unsafe_allow_html=True)
