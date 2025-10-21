import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple

@dataclass
class Params:
    # Horizonte
    years: int = 10

    # Situación inicial (basada en el caso San Gabriel)
    demanda_potencial_inicial: int = 400  # Pool de familias potenciales en el barrio
    tasa_descenso_demanda: float = 0.05  # Refleja caída de natalidad y crisis económica
    
    # Alumnos iniciales (escuela pequeña, ~300 alumnos)
    g_inicial: int = 25  # Promedio por grado
    
    # Capacidad
    div_inicial_por_grado: int = 1
    cupo_optimo: int = 25
    cupo_maximo: int = 30

    # RETENCIÓN: El problema clave del caso
    tasa_continuidad_jardin_primaria: float = 0.56  # 56% como en 2024 del caso
    tasa_bajas_imprevistas: float = 0.02  # Bajas generales
    tasa_bajas_max_por_calidad: float = 0.10
    
    # Sensibilidad de bajas al precio
    k_bajas_precio: float = 0.15
    ref_precio: float = 85000.0  # Cuota actual según el caso

    # CALIDAD: Factor crítico
    calidad_base: float = 0.70  # Buen nivel académico pero con debilidades
    beta_hacinamiento: float = 1.5
    
    # Factores de calidad específicos del caso
    k_q_articulacion: float = 0.15  # Impacto de articulación jardín-primaria
    k_q_comunicacion: float = 0.10  # Impacto de comunicación con familias
    k_q_diferenciacion: float = 0.12  # Impacto de propuesta diferenciadora (inglés, etc)
    k_q_inv_alumno: float = 0.08
    k_q_infra_inversion: float = 0.06
    k_q_mantenimiento_netodep: float = 0.05
    
    # Variables de decisión (escenarios)
    nivel_articulacion: float = 0.3  # 0=nada, 1=excelente
    nivel_comunicacion: float = 0.2  # 0=nada, 1=excelente  
    nivel_diferenciacion: float = 0.4  # 0=básico, 1=bilingüe completo

    # Marketing y admisión
    cuota_mensual: float = 85000.0  # Según el caso
    meses: int = 10  # Colegios suelen facturar 10 meses
    
    prop_mkt: float = 0.08
    mkt_floor: float = 500_000.0
    cac_base: float = 25000.0  # CAC más realista para sector educativo
    k_saturacion: float = 1.5
    
    politica_seleccion: float = 0.80  # Menos selectivos = más admisiones

    # Costos (simplificados)
    costo_docente_por_aula: float = 1_200_000.0  # Anual
    sueldos_no_docentes: float = 3_000_000.0  # Anual
    inversion_infra_anual: float = 800_000.0
    inversion_calidad_por_alumno: float = 8000.0
    mantenimiento_pct_facturacion: float = 0.08

    # Activos
    activos_inicial: float = 5_000_000.0
    tasa_depreciacion_anual: float = 0.05

    # Financiamiento
    caja_inicial: float = 2_000_000.0
    pct_capex_financiado: float = 0.50
    tasa_interes_deuda: float = 0.15
    anos_amortizacion_deuda: int = 8
    deuda_inicial: float = 0.0

    # Pipeline (para escenarios de expansión)
    pipeline_start_year: int = -1
    costo_construccion_aula: float = 2_000_000.0

    # Candidatos orgánicos
    qref_candidatos: float = 0.65
    alpha_candidatos_q: float = 0.25
    lag_calidad_candidatos: int = 1
    
    # Referencias para normalización
    ref_inv_alumno: float = 8000.0
    ref_infra: float = 800_000.0
    ref_mant: float = 500_000.0
    
    # Selectividad
    k_q_selectividad: float = 0.15
    
    # Semilla aleatoria
    random_seed: int = 42
    candidatos_inicial: float = 60.0


def simulate(par: Params) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    T = par.years
    G = 12
    t = np.arange(T+1)

    rng = np.random.default_rng(par.random_seed)

    # Stocks
    Gk = np.zeros((T+1, G), dtype=float)
    Div = np.zeros((T+1, G), dtype=float)
    Cand = np.zeros(T+1, dtype=float)
    Act = np.zeros(T+1, dtype=float)
    Caja = np.zeros(T+1, dtype=float)
    Deuda = np.zeros(T+1, dtype=float)
    Demanda = np.zeros(T+1, dtype=float)

    # Iniciales
    Gk[0, :] = par.g_inicial
    Div[0, :] = par.div_inicial_por_grado
    Cand[0] = par.candidatos_inicial
    Act[0] = par.activos_inicial
    Caja[0] = par.caja_inicial
    Deuda[0] = par.deuda_inicial
    Demanda[0] = par.demanda_potencial_inicial

    # Series agregadas
    calidad = np.zeros(T+1)
    facturacion = np.zeros(T+1)
    sueldos = np.zeros(T+1)
    inv_infra = np.zeros(T+1)
    inv_calidad_alumno = np.zeros(T+1)
    mantenimiento = np.zeros(T+1)
    marketing = np.zeros(T+1)
    costos_opex = np.zeros(T+1)

    resultado_operativo = np.zeros(T+1)
    capex_total = np.zeros(T+1)
    capex_propio = np.zeros(T+1)
    capex_financiado = np.zeros(T+1)
    interes_deuda = np.zeros(T+1)
    amortizacion_deuda = np.zeros(T+1)
    resultado_neto = np.zeros(T+1)

    # Marketing y candidatos
    cac = np.zeros(T+1)
    nuevos_candidatos = np.zeros(T+1)
    nuevos_candidatos_mkt = np.zeros(T+1)
    nuevos_candidatos_q = np.zeros(T+1)
    admitidos = np.zeros(T+1)
    rechazados = np.zeros(T+1)
    selectividad = np.zeros(T+1)

    # Flujos académicos
    bajas_totales = np.zeros(T+1)
    bajas_no_continuidad = np.zeros(T+1)  # NUEVO: bajas entre jardín y primaria
    egresados = np.zeros(T+1)

    # Pipeline
    pipeline_construcciones = np.zeros(T+1)

    def cap_opt(row_div):
        return row_div * par.cupo_optimo

    def cap_max(row_div):
        return row_div * par.cupo_maximo

    def construir_en_anio(k: int) -> bool:
        if par.pipeline_start_year < 0:
            return False
        return (0 <= (k - par.pipeline_start_year) < 12)

    for k in range(T+1):
        # Demanda decreciente
        if k > 0:
            Demanda[k] = Demanda[k-1] * (1.0 - par.tasa_descenso_demanda)

        # Totales y capacidades
        alumnos_k = Gk[k, :].sum()
        Cap_opt_k = cap_opt(Div[k, :])
        aulas_k = float(Div[k, :].sum())

        # Hacinamiento
        with np.errstate(divide='ignore', invalid='ignore'):
            hac_k = np.maximum(0.0, (Gk[k, :] - Cap_opt_k) / np.maximum(Cap_opt_k, 1.0))
        hac_prom = 0.0 if alumnos_k <= 0 else float(np.dot(Gk[k, :], hac_k) / max(alumnos_k, 1.0))

        # Facturación
        facturacion[k] = alumnos_k * par.cuota_mensual * par.meses

        # Costos obligatorios
        sueldos[k] = par.costo_docente_por_aula * aulas_k + par.sueldos_no_docentes
        mantenimiento[k] = par.mantenimiento_pct_facturacion * facturacion[k]

        # Targets de inversión
        target_infra = par.inversion_infra_anual
        target_calidad = par.inversion_calidad_por_alumno * alumnos_k
        margen_prov = facturacion[k] - (sueldos[k] + mantenimiento[k])
        saturacion = 0.0 if Demanda[k] <= 0 else min(1.0, alumnos_k / Demanda[k])
        cac[k] = par.cac_base * (1.0 + par.k_saturacion * saturacion)
        target_mkt = max(par.mkt_floor, par.mkt_floor + par.prop_mkt * max(margen_prov, 0.0))

        # Asignación presupuestaria
        disponible = max(margen_prov, 0.0)
        deseos = np.array([target_infra, target_calidad, target_mkt], dtype=float)
        total_deseos = float(deseos.sum())
        if total_deseos <= disponible + 1e-9:
            inv_infra[k], inv_calidad_alumno[k], marketing[k] = deseos
        else:
            if total_deseos > 0:
                ratio = disponible / total_deseos
                inv_infra[k], inv_calidad_alumno[k], marketing[k] = deseos * ratio
            else:
                inv_infra[k] = inv_calidad_alumno[k] = marketing[k] = 0.0

        # Nuevos candidatos
        nuevos_candidatos_mkt[k] = 0.0 if cac[k] <= 0 else marketing[k] / cac[k]
        q_driver = calidad[k-1] if (k > 0 and par.lag_calidad_candidatos >= 1) else calidad[k]
        excedente_q = max(q_driver - par.qref_candidatos, 0.0)
        pool_satur = 0.0
        if Demanda[k] > 1e-9:
            pool_satur = max(0.0, 1.0 - (alumnos_k / Demanda[k]))
        nuevos_candidatos_q[k] = par.alpha_candidatos_q * excedente_q * alumnos_k * pool_satur
        nuevos_candidatos[k] = nuevos_candidatos_mkt[k] + nuevos_candidatos_q[k]

        # Admitidos
        gap_demanda = max(Demanda[k] - alumnos_k, 0.0)
        capacidad_g1_max = float(Div[k, 0] * par.cupo_maximo)
        admitidos[k] = min(par.politica_seleccion * nuevos_candidatos[k], gap_demanda, capacidad_g1_max)

        rechazados[k] = max(nuevos_candidatos[k] - admitidos[k], 0.0)
        Cand[k] = nuevos_candidatos[k]
        selectividad[k] = float(admitidos[k] / nuevos_candidatos[k]) if nuevos_candidatos[k] > 0 else 0.0

        # BAJAS: Distinguimos entre jardín→primaria y resto
        calidad_prev = calidad[k-1] if k > 0 else par.calidad_base
        presion_precio = par.k_bajas_precio * max((par.cuota_mensual / max(par.ref_precio, 1e-9)) - 1.0, 0.0)
        tasa_bajas_general = min(
            1.0,
            par.tasa_bajas_imprevistas
            + (1.0 - calidad_prev) * par.tasa_bajas_max_por_calidad
            + presion_precio
        )
        
        bajas_vec = np.zeros(G, dtype=float)
        
        # Bajas en grados medios (G3-G10)
        segmento = Gk[k, 2:10].copy()
        total_segmento = float(segmento.sum())
        if total_segmento > 0 and tasa_bajas_general > 0:
            bajas_obj = min(int(round(tasa_bajas_general * total_segmento)), int(total_segmento))
            probs = segmento / total_segmento
            bajas_seg_int = rng.multinomial(bajas_obj, probs)
            bajas_vec[2:10] = bajas_seg_int

        # NUEVA: Bajas por no continuidad jardín→primaria (afecta transición G1)
        # Esto simula las familias que no reinscriben entre nivel inicial y primaria
        jardin_egresados = Gk[k, 0] if k > 0 else 0  # Aproximación: G1 anterior
        bajas_no_continuidad[k] = jardin_egresados * (1.0 - par.tasa_continuidad_jardin_primaria)
        
        bajas_totales[k] = float(bajas_vec.sum()) + bajas_no_continuidad[k]

        # Egresados
        egresados[k] = Gk[k, 11]

        # CALIDAD: Incluye factores específicos del caso
        dep = par.tasa_depreciacion_anual * Act[k]
        inv_alum_norm = ((inv_calidad_alumno[k] / max(alumnos_k, 1e-9)) / max(par.ref_inv_alumno, 1e-9)) if alumnos_k > 0 else 0.0
        infra_norm = (inv_infra[k] / max(par.ref_infra, 1e-9))
        mant_norm = ((mantenimiento[k] - dep) / max(par.ref_mant, 1e-9))
        efecto_selectividad = - par.k_q_selectividad * selectividad[k]
        
        # Factores de decisión del caso
        efecto_articulacion = par.k_q_articulacion * par.nivel_articulacion
        efecto_comunicacion = par.k_q_comunicacion * par.nivel_comunicacion
        efecto_diferenciacion = par.k_q_diferenciacion * par.nivel_diferenciacion

        calidad_raw = (par.calidad_base
                       - par.beta_hacinamiento * hac_prom
                       + par.k_q_inv_alumno * inv_alum_norm
                       + par.k_q_infra_inversion * infra_norm
                       + par.k_q_mantenimiento_netodep * mant_norm
                       + efecto_selectividad
                       + efecto_articulacion
                       + efecto_comunicacion
                       + efecto_diferenciacion)
        calidad[k] = float(np.clip(calidad_raw, 0.0, 1.0))

        # OPEX y resultados
        costos_opex[k] = sueldos[k] + mantenimiento[k] + inv_infra[k] + inv_calidad_alumno[k] + marketing[k]
        resultado_operativo[k] = facturacion[k] - costos_opex[k]

        if k < T:
            # Pipeline
            build = construir_en_anio(k)
            capex_total[k] = par.costo_construccion_aula if build else 0.0

            # Financiamiento
            capex_financiado[k] = capex_total[k] * par.pct_capex_financiado
            capex_propio[k] = capex_total[k] - capex_financiado[k]

            # Deuda
            interes_deuda[k] = par.tasa_interes_deuda * Deuda[k]
            if par.anos_amortizacion_deuda > 0:
                amortizacion_deuda[k] = min(Deuda[k], Deuda[k] / par.anos_amortizacion_deuda)
            else:
                amortizacion_deuda[k] = 0.0

            resultado_neto[k] = resultado_operativo[k] - capex_propio[k] - interes_deuda[k] - amortizacion_deuda[k]

            # Evolución de stocks
            next_C = 0.0

            # Alumnos por grado
            next_G = np.zeros(G, dtype=float)
            next_G[0] = admitidos[k]
            for gi in range(1, 11):
                bajas_prev = bajas_vec[gi-1] if 2 <= gi-1 <= 9 else 0.0
                next_G[gi] = max(Gk[k, gi-1] - bajas_prev, 0.0)
            next_G[11] = max(Gk[k, 10], 0.0)

            # Divisiones
            next_D = Div[k, :].copy()
            if build:
                tramo = (k - par.pipeline_start_year) % 12 if par.pipeline_start_year >= 0 else 0
                next_D[tramo] += 1.0
                pipeline_construcciones[k] = 1.0

            # Límites de capacidad
            total_next = float(next_G.sum())
            cap_total_max_next = float((next_D * par.cupo_maximo).sum())
            poblacion_max = float(Demanda[k])
            allowed = min(cap_total_max_next, poblacion_max)
            if total_next > allowed and total_next > 0:
                factor = allowed / total_next
                next_G = next_G * factor

            # Activos
            dep = par.tasa_depreciacion_anual * Act[k]
            next_Act = Act[k] + capex_total[k] - dep

            # Deuda
            next_Deuda = max(Deuda[k] + capex_financiado[k] - amortizacion_deuda[k], 0.0)

            # Caja
            next_Caja = Caja[k] + resultado_neto[k]

            # Demanda
            next_Demanda = Demanda[k] * (1.0 - par.tasa_descenso_demanda)

            # Actualización
            Gk[k+1, :] = np.maximum(0.0, next_G)
            Div[k+1, :] = next_D
            Cand[k+1] = next_C
            Act[k+1] = max(next_Act, 0.0)
            Deuda[k+1] = next_Deuda
            Caja[k+1] = next_Caja
            Demanda[k+1] = next_Demanda
        else:
            capex_total[k] = 0.0
            capex_financiado[k] = 0.0
            capex_propio[k] = 0.0
            interes_deuda[k] = par.tasa_interes_deuda * Deuda[k]
            amortizacion_deuda[k] = min(Deuda[k], Deuda[k] / par.anos_amortizacion_deuda) if par.anos_amortizacion_deuda > 0 else 0.0
            resultado_neto[k] = resultado_operativo[k] - interes_deuda[k] - amortizacion_deuda[k]

    # Totales
    aulas = Div.sum(axis=1)

    def rint(a): return np.rint(a).astype(int)

    # KPIs
    margen_operativo = np.where(facturacion > 0, resultado_operativo / facturacion, 0.0)
    margen_neto = np.where(facturacion > 0, resultado_neto / facturacion, 0.0)
    costos_totales_cash = costos_opex + capex_propio + interes_deuda + amortizacion_deuda
    
    # Tasa de continuidad efectiva (admitidos / egresados jardín aproximado)
    tasa_continuidad_efectiva = np.zeros(T+1)
    for k in range(T+1):
        if k > 0 and Gk[k-1, 0] > 0:
            tasa_continuidad_efectiva[k] = min(1.0, Gk[k, 1] / Gk[k-1, 0])

    df = pd.DataFrame({
        "Año": t,
        "DemandaPotencial": Demanda,
        "AlumnosTotales": rint(Gk.sum(axis=1)),
        "Calidad": calidad,
        "TasaContinuidad": tasa_continuidad_efectiva,
        "AulasTotales": rint(aulas),
        "CapacidadMaxTotal": rint((Div * par.cupo_maximo).sum(axis=1)),
        "CapacidadOptTotal": rint((Div * par.cupo_optimo).sum(axis=1)),
        "Facturacion": facturacion,
        "Sueldos": sueldos,
        "InversionInfra": inv_infra,
        "InversionCalidadAlumno": inv_calidad_alumno,
        "Mantenimiento": mantenimiento,
        "Marketing": marketing,
        "CostosOPEX": costos_opex,
        "CostosTotalesCash": costos_totales_cash,
        "ResultadoOperativo": resultado_operativo,
        "CAPEX_Total": capex_total,
        "CAPEX_Propio": capex_propio,
        "CAPEX_Financiado": capex_financiado,
        "InteresDeuda": interes_deuda,
        "AmortizacionDeuda": amortizacion_deuda,
        "ResultadoNeto": resultado_neto,
        "Caja": Caja,
        "Deuda": Deuda,
        "MargenOperativo": margen_operativo,
        "MargenNeto": margen_neto,
        "CAC": cac,
        "CandidatosStock": rint(Cand),
        "NuevosCandidatos": rint(nuevos_candidatos),
        "NuevosCandidatosMkt": rint(nuevos_candidatos_mkt),
        "NuevosCandidatosQ": rint(nuevos_candidatos_q),
        "Admitidos": rint(admitidos),
        "Rechazados": rint(rechazados),
        "Selectividad": selectividad,
        "BajasTotales": rint(bajas_totales),
        "BajasNoContinuidad": rint(bajas_no_continuidad),
        "Egresados": rint(egresados),
        "PipelineConstrucciones": pipeline_construcciones,
        "Activos": Act
    })

    # Series por grado
    for gi in range(G):
        df[f"G{gi+1}"] = rint(Gk[:, gi])
        df[f"DivG{gi+1}"] = Div[:, gi]
        Cap_opt_series = Div[:, gi] * par.cupo_optimo
        with np.errstate(divide='ignore', invalid='ignore'):
            hac_series = np.maximum(0.0, (Gk[:, gi] - Cap_opt_series) / np.maximum(Cap_opt_series, 1.0))
        df[f"HacG{gi+1}"] = hac_series

    meta = {"params": asdict(par)}
    return df, meta
