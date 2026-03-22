"""
=============================================================================
SISTEMA BASADO EN CONOCIMIENTO -- CRM BANCARIO
=============================================================================
Curso   : Inteligencia Artificial / Sistemas Basados en Conocimiento
Institución: Universidad CENFOTEC

Descripción:
    Este módulo implementa un Sistema Basado en Conocimiento (SBC) para la
    gestión de clientes en un CRM bancario.  El conocimiento fue adquirido
    mediante entrevista con un Director de Marketing Bancario y está
    organizado en cuatro capas de decisión:

        Capa 1 -- Valor del cliente (RFM)
        Capa 2 -- Arquetipo del cliente
        Capa 3 -- Etapa del Customer Journey
        Capa 4 -- Afinidad de producto

    Estructura del módulo
    ----------------------
    1. FRAMES              -- representación estructurada del conocimiento
    2. BASE DE HECHOS      -- estado actual de un cliente concreto
    3. REGLAS DE PRODUCCIÓN-- lógica SI–ENTONCES derivada de la entrevista
    4. MOTOR DE INFERENCIA -- encadenamiento hacia adelante (forward chaining)
    5. INTERFAZ DE USUARIO -- entrada de datos y presentación de resultados
=============================================================================
"""

import argparse

############# FRAMES #############

FRAMES = {

    # -- Frame: Valor RFM ------------------------------------------------------
    "ValorRFM": {
        "descripcion": "Segmento de valor económico consolidado a partir de Recency, Frequency y Monetary.",
        "slots": {
            "valor_rfm": {
                "tipo": "categórico",
                "valores_posibles": ["alto", "medio", "bajo"],
                "descripcion": "Nivel de prioridad estratégica del cliente para el banco."
            },
            "recency": {
                "tipo": "categórico",
                "valores_posibles": ["muy_reciente", "reciente", "antiguo", "inactivo"],
                "descripcion": "Tiempo transcurrido desde la última interacción relevante."
            },
            "frequency": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Cantidad de interacciones con el banco en el período de análisis."
            },
            "monetary": {
                "tipo": "categórico",
                "valores_posibles": ["alto", "medio", "bajo"],
                "descripcion": "Valor económico generado (saldos, comisiones, intereses)."
            }
        }
    },

    # -- Frame: Arquetipo del cliente ------------------------------------------
    "ArquetipoCliente": {
        "descripcion": "Perfil comportamental del cliente derivado de sus patrones de uso financiero.",
        "slots": {
            "arquetipo": {
                "tipo": "categórico",
                "valores_posibles": [
                    "profesional_joven",
                    "familia_expansion",
                    "transaccional",
                    "patrimonial",
                    "emprendedor"
                ],
                "descripcion": "Tipología que explica cómo se comporta el cliente y qué necesita."
            }
        }
    },

    # -- Frame: Customer Journey ------------------------------------------------
    "CustomerJourney": {
        "descripcion": "Momento actual del cliente en su relación con el banco.",
        "slots": {
            "etapa_journey": {
                "tipo": "categórico",
                "valores_posibles": [
                    "adquisicion",
                    "activacion",
                    "crecimiento",
                    "madurez",
                    "riesgo_abandono",
                    "reactivacion"
                ],
                "descripcion": "Etapa que determina el objetivo de la interacción CRM."
            }
        }
    },

    # -- Frame: Afinidad de producto --------------------------------------------
    "AfinidadProducto": {
        "descripcion": "Probabilidad estimada de que el cliente adopte cada categoría de producto bancario.",
        "slots": {
            "afinidad_tarjeta_credito": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de tarjeta de crédito."
            },
            "afinidad_credito_personal": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de crédito personal."
            },
            "afinidad_credito_hipotecario": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de crédito hipotecario."
            },
            "afinidad_inversion": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de productos de inversión."
            },
            "afinidad_seguros": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de seguros."
            },
            "afinidad_cuenta_ahorro": {
                "tipo": "categórico",
                "valores_posibles": ["alta", "media", "baja"],
                "descripcion": "Probabilidad de adopción de cuenta de ahorro."
            }
        }
    },

    # -- Frame: Acción CRM (salida) --------------------------------------------
    "AccionCRM": {
        "descripcion": "Acción concreta que el CRM debe ejecutar sobre el cliente.",
        "slots": {
            "accion_crm": {
                "tipo": "categórico",
                "valores_posibles": [
                    "ofrecer_tarjeta_credito",
                    "ofrecer_asesoria_inversion",
                    "ofrecer_seguros",
                    "ofrecer_credito_hipotecario",
                    "ofrecer_credito_personal",
                    "campana_activacion_digital",
                    "campana_retencion",
                    "campana_reactivacion",
                    "sin_accion"
                ],
                "descripcion": "Resultado producido por el motor de inferencia."
            },
            "canal_preferido": {
                "tipo": "categórico",
                "valores_posibles": [
                    "digital",
                    "asesor_personal",
                    "mixto",
                    "automatizado",
                    "asesor_comercial"
                ],
                "descripcion": "Canal de comunicación recomendado para ejecutar la acción."
            }
        }
    }
}


############# CLASE BASEHECHOS #############

class BaseHechos:


    def __init__(self, datos_cliente: dict):
        """
        Parámetros
        ----------
        datos_cliente : dict
            Diccionario con los atributos iniciales del cliente.
            Las claves deben coincidir con los slots definidos en los FRAMES.
        """
        self._hechos = dict(datos_cliente)
        self._trazabilidad = []

    # -- Acceso a hechos --------------------------------------------------------

    def obtener(self, atributo: str, default=None):
        return self._hechos.get(atributo, default)

    def establecer(self, atributo: str, valor, fuente: str = ""):
        self._hechos[atributo] = valor
        if fuente:
            self._trazabilidad.append(f"[{fuente}] --> {atributo} = {valor}")

    def tiene(self, atributo: str) -> bool:
        """Indica si un atributo ya tiene valor en la base de hechos."""
        return atributo in self._hechos and self._hechos[atributo] is not None

    # -- Consulta --------------------------------------------------------------

    def todos_los_hechos(self) -> dict:
        return dict(self._hechos)

    def traza(self) -> list:
        return list(self._trazabilidad)

    def __repr__(self):
        lineas = ["BaseHechos {"]
        for k, v in self._hechos.items():
            lineas.append(f"  {k}: {v}")
        lineas.append("}")
        return "\n".join(lineas)



############# REGLAS DE PRODUCCIÓN #############

class Regla:
    # Representa una regla de producción SI–ENTONCES.

    def __init__(self, id_regla: str, nombre: str, condicion, accion, prioridad: int = 0):
        self.id       = id_regla
        self.nombre   = nombre
        self.condicion = condicion
        self.accion    = accion
        self.prioridad = prioridad

    def es_aplicable(self, base: BaseHechos) -> bool:
        try:
            return self.condicion(base)
        except Exception:
            return False

    def aplicar(self, base: BaseHechos):
        self.accion(base)
        base._trazabilidad.append(f"Regla disparada: {self.id} -- {self.nombre}")


# -- Definición de todas las reglas --------------------------------------------

REGLAS = [

    # -- Meta-regla: inactividad fuerza etapa reactivación --------------------
    Regla(
        id_regla  = "RN-03",
        nombre    = "Inactividad fuerza etapa reactivación",
        prioridad = 100,
        condicion = lambda b: b.obtener("recency") == "inactivo",
        accion    = lambda b: b.establecer("etapa_journey", "reactivacion", "RN-03")
    ),

    # -- Corrección: cliente inactivo de alto valor usa asesor personal --------
    Regla(
        id_regla  = "RN-03B",
        nombre    = "Reactivación de alto valor por asesor personal",
        prioridad = 100,
        condicion = lambda b: (
            b.obtener("recency") == "inactivo" and
            b.obtener("valor_rfm") == "alto"
        ),
        accion    = lambda b: (
            b.establecer("canal_preferido", "asesor_personal", "RN-03B"),
            b.establecer("accion_crm", "campana_reactivacion", "RN-03B")
        )
    ),

    # -- Corrección: bloqueo de oferta incompatible con arquetipo transaccional
    Regla(
        id_regla  = "RN-08B",
        nombre    = "Bloqueo de inversión y seguros para arquetipo transaccional",
        prioridad = 90,
        condicion = lambda b: b.obtener("arquetipo") == "transaccional",
        accion    = lambda b: (
            b.establecer("afinidad_inversion", "baja", "RN-08B"),
            b.establecer("afinidad_seguros", "baja", "RN-08B")
        )
    ),

    # -- Reglas combinadas (mayor especificidad) --------------------------------

    # RN-18: Cliente patrimonial en crecimiento con afinidad inversión alta
    Regla(
        id_regla  = "RN-18",
        nombre    = "Cliente patrimonial en crecimiento --> asesoría inversión",
        prioridad = 50,
        condicion = lambda b: (
            b.obtener("valor_rfm") == "alto" and
            b.obtener("arquetipo") == "patrimonial" and
            b.obtener("etapa_journey") == "crecimiento" and
            b.obtener("afinidad_inversion") == "alta"
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_asesoria_inversion", "RN-18")
    ),

    # RN-19: Profesional joven en activación con alta afinidad tarjeta
    Regla(
        id_regla  = "RN-19",
        nombre    = "Profesional joven en activación --> ofrecer tarjeta de crédito",
        prioridad = 50,
        condicion = lambda b: (
            b.obtener("valor_rfm") in ("medio", "alto") and
            b.obtener("arquetipo") == "profesional_joven" and
            b.obtener("etapa_journey") == "activacion" and
            b.obtener("afinidad_tarjeta_credito") == "alta"
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_tarjeta_credito", "RN-19")
    ),

    # RN-20: Familia en expansión en madurez con alta afinidad seguros
    Regla(
        id_regla  = "RN-20",
        nombre    = "Familia en expansión en madurez --> ofrecer seguros",
        prioridad = 50,
        condicion = lambda b: (
            b.obtener("valor_rfm") == "alto" and
            b.obtener("arquetipo") == "familia_expansion" and
            b.obtener("etapa_journey") == "madurez" and
            b.obtener("afinidad_seguros") == "alta"
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_seguros", "RN-20")
    ),

    # RN-21: Transaccional en riesgo de abandono
    Regla(
        id_regla  = "RN-21",
        nombre    = "Transaccional en riesgo de abandono --> campaña retención",
        prioridad = 50,
        condicion = lambda b: (
            b.obtener("valor_rfm") == "bajo" and
            b.obtener("arquetipo") == "transaccional" and
            b.obtener("etapa_journey") == "riesgo_abandono"
        ),
        accion    = lambda b: b.establecer("accion_crm", "campana_retencion", "RN-21")
    ),

    # RN-22: Emprendedor en crecimiento con alta afinidad crédito personal
    Regla(
        id_regla  = "RN-22",
        nombre    = "Emprendedor en crecimiento --> ofrecer crédito personal",
        prioridad = 50,
        condicion = lambda b: (
            b.obtener("valor_rfm") == "alto" and
            b.obtener("arquetipo") == "emprendedor" and
            b.obtener("etapa_journey") == "crecimiento" and
            b.obtener("afinidad_credito_personal") == "alta"
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_credito_personal", "RN-22")
    ),

    # -- Reglas de Capa 3 -- Customer Journey (acción directa) ------------------

    # RN-09: Adquisición --> activación digital
    Regla(
        id_regla  = "RN-09",
        nombre    = "Adquisición --> campaña activación digital",
        prioridad = 30,
        condicion = lambda b: b.obtener("etapa_journey") == "adquisicion",
        accion    = lambda b: b.establecer("accion_crm", "campana_activacion_digital", "RN-09")
    ),

    # RN-10: Riesgo de abandono --> campaña retención
    Regla(
        id_regla  = "RN-10",
        nombre    = "Riesgo de abandono --> campaña retención",
        prioridad = 30,
        condicion = lambda b: b.obtener("etapa_journey") == "riesgo_abandono",
        accion    = lambda b: b.establecer("accion_crm", "campana_retencion", "RN-10")
    ),

    # RN-11: Reactivación --> campaña reactivación
    Regla(
        id_regla  = "RN-11",
        nombre    = "Reactivación --> campaña reactivación",
        prioridad = 30,
        condicion = lambda b: b.obtener("etapa_journey") == "reactivacion",
        accion    = lambda b: b.establecer("accion_crm", "campana_reactivacion", "RN-11")
    ),

    # RN-11B: Madurez de alto valor sin afinidad alta --> asesoría inversión por defecto
    Regla(
        id_regla  = "RN-11B",
        nombre    = "Madurez + alto valor + sin afinidad alta --> asesoría inversión por defecto",
        prioridad = 35,
        condicion = lambda b: (
            b.obtener("etapa_journey") == "madurez" and
            b.obtener("valor_rfm") == "alto" and
            b.obtener("afinidad_tarjeta_credito") != "alta" and
            b.obtener("afinidad_credito_personal") != "alta" and
            b.obtener("afinidad_credito_hipotecario") != "alta" and
            b.obtener("afinidad_inversion") != "alta" and
            b.obtener("afinidad_seguros") != "alta"
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_asesoria_inversion", "RN-11B")
    ),

    # -- Reglas de Capa 2 -- Arquetipo --> Canal preferido ------------------------

    # RN-04: Profesional joven --> digital
    Regla(
        id_regla  = "RN-04",
        nombre    = "Profesional joven --> canal digital",
        prioridad = 20,
        condicion = lambda b: (
            b.obtener("arquetipo") == "profesional_joven" and
            not b.tiene("canal_preferido")
        ),
        accion    = lambda b: b.establecer("canal_preferido", "digital", "RN-04")
    ),

    # RN-05: Patrimonial --> asesor personal
    Regla(
        id_regla  = "RN-05",
        nombre    = "Patrimonial --> canal asesor personal",
        prioridad = 20,
        condicion = lambda b: (
            b.obtener("arquetipo") == "patrimonial" and
            not b.tiene("canal_preferido")
        ),
        accion    = lambda b: b.establecer("canal_preferido", "asesor_personal", "RN-05")
    ),

    # RN-06: Familia en expansión --> mixto
    Regla(
        id_regla  = "RN-06",
        nombre    = "Familia en expansión --> canal mixto",
        prioridad = 20,
        condicion = lambda b: (
            b.obtener("arquetipo") == "familia_expansion" and
            not b.tiene("canal_preferido")
        ),
        accion    = lambda b: b.establecer("canal_preferido", "mixto", "RN-06")
    ),

    # RN-07: Transaccional --> automatizado
    Regla(
        id_regla  = "RN-07",
        nombre    = "Transaccional --> canal automatizado",
        prioridad = 20,
        condicion = lambda b: (
            b.obtener("arquetipo") == "transaccional" and
            not b.tiene("canal_preferido")
        ),
        accion    = lambda b: b.establecer("canal_preferido", "automatizado", "RN-07")
    ),

    # RN-08: Emprendedor --> asesor comercial
    Regla(
        id_regla  = "RN-08",
        nombre    = "Emprendedor --> canal asesor comercial",
        prioridad = 20,
        condicion = lambda b: (
            b.obtener("arquetipo") == "emprendedor" and
            not b.tiene("canal_preferido")
        ),
        accion    = lambda b: b.establecer("canal_preferido", "asesor_comercial", "RN-08")
    ),

    # -- Reglas de Capa 4 -- Afinidad de producto --------------------------------
    #    Solo se disparan si accion_crm aún no fue establecida.

    # RN-13: Alta afinidad tarjeta de crédito
    Regla(
        id_regla  = "RN-13",
        nombre    = "Alta afinidad tarjeta crédito --> ofrecer tarjeta",
        prioridad = 10,
        condicion = lambda b: (
            b.obtener("afinidad_tarjeta_credito") == "alta" and
            not b.tiene("accion_crm")
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_tarjeta_credito", "RN-13")
    ),

    # RN-14: Alta afinidad crédito hipotecario
    Regla(
        id_regla  = "RN-14",
        nombre    = "Alta afinidad crédito hipotecario --> ofrecer crédito hipotecario",
        prioridad = 10,
        condicion = lambda b: (
            b.obtener("afinidad_credito_hipotecario") == "alta" and
            not b.tiene("accion_crm")
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_credito_hipotecario", "RN-14")
    ),

    # RN-15: Alta afinidad crédito personal
    Regla(
        id_regla  = "RN-15",
        nombre    = "Alta afinidad crédito personal --> ofrecer crédito personal",
        prioridad = 10,
        condicion = lambda b: (
            b.obtener("afinidad_credito_personal") == "alta" and
            not b.tiene("accion_crm")
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_credito_personal", "RN-15")
    ),

    # RN-16: Alta afinidad inversión
    Regla(
        id_regla  = "RN-16",
        nombre    = "Alta afinidad inversión --> ofrecer asesoría inversión",
        prioridad = 10,
        condicion = lambda b: (
            b.obtener("afinidad_inversion") == "alta" and
            not b.tiene("accion_crm")
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_asesoria_inversion", "RN-16")
    ),

    # RN-17: Alta afinidad seguros
    Regla(
        id_regla  = "RN-17",
        nombre    = "Alta afinidad seguros --> ofrecer seguros",
        prioridad = 10,
        condicion = lambda b: (
            b.obtener("afinidad_seguros") == "alta" and
            not b.tiene("accion_crm")
        ),
        accion    = lambda b: b.establecer("accion_crm", "ofrecer_seguros", "RN-17")
    ),

    # -- Reglas de Capa 1 -- RFM general ----------------------------------------

    # RN-01: Cliente de alto valor --> priorizar atención personalizada
    Regla(
        id_regla  = "RN-01",
        nombre    = "Cliente de alto valor --> priorizar atención personalizada",
        prioridad = 5,
        condicion = lambda b: b.obtener("valor_rfm") == "alto",
        accion    = lambda b: b._trazabilidad.append(
            "[RN-01] Cliente de alto valor: priorizar en campañas de retención o expansión."
        )
    ),

    # RN-02: Cliente de bajo valor --> estrategia automatizada
    Regla(
        id_regla  = "RN-02",
        nombre    = "Cliente de bajo valor --> gestión automatizada de bajo costo",
        prioridad = 5,
        condicion = lambda b: b.obtener("valor_rfm") == "bajo",
        accion    = lambda b: b._trazabilidad.append(
            "[RN-02] Cliente de bajo valor: gestionar con estrategias automatizadas."
        )
    ),

    # -- Regla de cierre --------------------------------------------------------

    # RN-23: Sin acción por defecto
    Regla(
        id_regla  = "RN-23",
        nombre    = "Sin acción por defecto",
        prioridad = 0,
        condicion = lambda b: not b.tiene("accion_crm"),
        accion    = lambda b: b.establecer("accion_crm", "sin_accion", "RN-23")
    ),
]

############# MOTOR DE INFERENCIA #############

class MotorInferencia:

    def __init__(self, reglas: list):
        # Ordenar una sola vez por prioridad descendente
        self.reglas = sorted(reglas, key=lambda r: r.prioridad, reverse=True)

    def ejecutar(self, base: BaseHechos) -> BaseHechos:
        """
        Ejecuta el ciclo de inferencia sobre la base de hechos proporcionada.
        Modifica la base en el lugar y la devuelve.
        """
        disparadas = set()

        # Iterar hasta punto fijo (ninguna regla nueva aplicable)
        cambio = True
        while cambio:
            cambio = False
            for regla in self.reglas:
                if regla.id not in disparadas and regla.es_aplicable(base):
                    regla.aplicar(base)
                    disparadas.add(regla.id)
                    cambio = True
                    # Volver a empezar desde la regla de mayor prioridad
                    break

        return base

############# INTERFAZ DE USUARIO #############

# -- Clientes de ejemplo (basados en la entrevista) ----------------------------

CLIENTES_EJEMPLO = [
    {
        "cliente_id"                  : "CLI-001",
        "valor_rfm"                   : "alto",
        "recency"                     : "muy_reciente",
        "frequency"                   : "alta",
        "monetary"                    : "alto",
        "arquetipo"                   : "patrimonial",
        "etapa_journey"               : "crecimiento",
        "afinidad_tarjeta_credito"    : "media",
        "afinidad_credito_personal"   : "baja",
        "afinidad_credito_hipotecario": "baja",
        "afinidad_inversion"          : "alta",
        "afinidad_seguros"            : "media",
        "afinidad_cuenta_ahorro"      : "baja",
        # Acción esperada según entrevista: ofrecer_asesoria_inversion
    },
    {
        "cliente_id"                  : "CLI-002",
        "valor_rfm"                   : "medio",
        "recency"                     : "reciente",
        "frequency"                   : "media",
        "monetary"                    : "medio",
        "arquetipo"                   : "profesional_joven",
        "etapa_journey"               : "activacion",
        "afinidad_tarjeta_credito"    : "alta",
        "afinidad_credito_personal"   : "media",
        "afinidad_credito_hipotecario": "baja",
        "afinidad_inversion"          : "baja",
        "afinidad_seguros"            : "baja",
        "afinidad_cuenta_ahorro"      : "media",
        # Acción esperada según entrevista: ofrecer_tarjeta_credito
    },
    {
        "cliente_id"                  : "CLI-003",
        "valor_rfm"                   : "alto",
        "recency"                     : "reciente",
        "frequency"                   : "alta",
        "monetary"                    : "alto",
        "arquetipo"                   : "familia_expansion",
        "etapa_journey"               : "madurez",
        "afinidad_tarjeta_credito"    : "media",
        "afinidad_credito_personal"   : "media",
        "afinidad_credito_hipotecario": "baja",
        "afinidad_inversion"          : "baja",
        "afinidad_seguros"            : "alta",
        "afinidad_cuenta_ahorro"      : "baja",
        # Acción esperada según entrevista: ofrecer_seguros
    },
    {
        "cliente_id"                  : "CLI-004",
        "valor_rfm"                   : "bajo",
        "recency"                     : "antiguo",
        "frequency"                   : "baja",
        "monetary"                    : "bajo",
        "arquetipo"                   : "transaccional",
        "etapa_journey"               : "riesgo_abandono",
        "afinidad_tarjeta_credito"    : "baja",
        "afinidad_credito_personal"   : "baja",
        "afinidad_credito_hipotecario": "baja",
        "afinidad_inversion"          : "media",  # debe ser bloqueada por RN-08B
        "afinidad_seguros"            : "media",  # debe ser bloqueada por RN-08B
        "afinidad_cuenta_ahorro"      : "media",
        # Acción esperada según entrevista: campana_retencion
    },
]


# -- Función auxiliar: imprimir separador --------------------------------------

def separador(titulo: str = "", ancho: int = 65):
    if titulo:
        print(f"\n{'--' * ancho}")
        print(f"  {titulo}")
        print(f"{'--' * ancho}")
    else:
        print(f"{'--' * ancho}")


# -- Función principal: ejecutar el sistema ------------------------------------

def ejecutar_sistema(mostrar_traza: bool):
    motor = MotorInferencia(REGLAS)

    print("\n" + "═" * 65)
    print("  SISTEMA BASADO EN CONOCIMIENTO -- CRM BANCARIO")
    print("  Universidad CENFOTEC")
    print("═" * 65)

    for datos in CLIENTES_EJEMPLO:
        base = BaseHechos(datos)
        motor.ejecutar(base)

        separador(f"Cliente: {base.obtener('cliente_id')}")

        print(f"\n  PERFIL DE ENTRADA")
        print(f"  {'Valor RFM':<30}: {base.obtener('valor_rfm')}")
        print(f"  {'Recency':<30}: {base.obtener('recency')}")
        print(f"  {'Frequency':<30}: {base.obtener('frequency')}")
        print(f"  {'Monetary':<30}: {base.obtener('monetary')}")
        print(f"  {'Arquetipo':<30}: {base.obtener('arquetipo')}")
        print(f"  {'Etapa Journey (entrada)':<30}: {datos.get('etapa_journey')}")

        print(f"\n  RESULTADO DE INFERENCIA")
        etapa_final = base.obtener("etapa_journey")
        if etapa_final != datos.get("etapa_journey"):
            print(f"  {'Etapa Journey (ajustada)':<30}: {etapa_final}  <- modificada por motor")
        print(f"  {'Canal preferido':<30}: {base.obtener('canal_preferido', '(no asignado)')}")
        print(f"  {'Acción CRM recomendada':<30}: {base.obtener('accion_crm')}")

        if mostrar_traza:
            print(f"\n  TRAZA DE RAZONAMIENTO")
            for paso in base.traza():
                print(f"  * {paso}")

    separador()
    print("\n  Sistema ejecutado correctamente.\n")


# ------------------------------------------------------------------------------
# PUNTO DE ENTRADA
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sistema Basado en Conocimiento -- CRM Bancario"
    )
    parser.add_argument(
        "-t", "--traza",
        action="store_true",
        help="Muestra la traza completa de razonamiento para cada cliente"
    )
    args = parser.parse_args()

    ejecutar_sistema(mostrar_traza=args.traza)