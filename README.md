# Sistema Basado en Conocimiento — CRM Bancario

Implementación en Python de un Sistema Basado en Conocimiento (SBC) para la gestión de clientes en un CRM bancario. El conocimiento fue adquirido mediante entrevista con un Director de Marketing Bancario y formalizado como parte del Mini Proyecto 1 del curso de Inteligencia Artificial en la Universidad CENFOTEC.

---

## ¿Qué hace el sistema?

Recibe el perfil de un cliente bancario y produce automáticamente la acción CRM recomendada, simulando el razonamiento del experto entrevistado. La decisión se toma en cuatro capas en orden obligatorio:

1. **Valor del cliente (RFM)** — ¿Cuánto vale este cliente para el banco?
2. **Arquetipo del cliente** — ¿Qué tipo de relación financiera tiene con el banco?
3. **Customer Journey** — ¿En qué momento de su relación está?
4. **Afinidad de producto** — ¿Qué producto tiene más probabilidad de adoptar?

---

## Requisitos

- Python 3.11 o superior
- No requiere librerías externas

---

## Cómo ejecutarlo

```bash
# Solo resultados
python sistema_experto_crm.py

# Con traza completa de razonamiento
python sistema_experto_crm.py -t

# También funciona con el nombre largo
python sistema_experto_crm.py --traza

# Ver todos los argumentos disponibles
python sistema_experto_crm.py --help
```

---

## Salida esperada

Sin traza:
```
═════════════════════════════════════════════════════════════
  SISTEMA BASADO EN CONOCIMIENTO -- CRM BANCARIO
  Universidad CENFOTEC
═════════════════════════════════════════════════════════════

  Cliente: CLI-001
  ────────────────────────────────────────────────────────

  PERFIL DE ENTRADA
  Valor RFM                     : alto
  Arquetipo                     : patrimonial
  Etapa Journey (entrada)       : crecimiento

  RESULTADO DE INFERENCIA
  Canal preferido               : asesor_personal
  Acción CRM recomendada        : ofrecer_asesoria_inversion
```

Con `-t`:
```
  TRAZA DE RAZONAMIENTO
  * [RN-18] --> accion_crm = ofrecer_asesoria_inversion
  * Regla disparada: RN-18 -- Cliente patrimonial en crecimiento
  * [RN-05] --> canal_preferido = asesor_personal
  ...
```

---

## Estructura del código

| Sección | Descripción |
|---|---|
| `FRAMES` | Representación declarativa del dominio: 5 frames con sus slots, tipos y valores posibles |
| `BaseHechos` | Memoria de trabajo del motor: almacena el perfil del cliente y registra la trazabilidad |
| `Regla` + `REGLAS` | 23 reglas de producción SI–ENTONCES organizadas por prioridad |
| `MotorInferencia` | Encadenamiento hacia adelante con condición de punto fijo |
| `CLIENTES_EJEMPLO` + `ejecutar_sistema()` | 4 casos de prueba extraídos de la entrevista e interfaz de resultados |

---

## Reglas implementadas

| ID | Descripción | Prioridad |
|---|---|---|
| RN-03 | Inactividad fuerza etapa reactivación | 100 |
| RN-03B | Reactivación de alto valor por asesor personal | 100 |
| RN-08B | Bloqueo de inversión y seguros para arquetipo transaccional | 90 |
| RN-18 | Cliente patrimonial en crecimiento → asesoría inversión | 50 |
| RN-19 | Profesional joven en activación → ofrecer tarjeta de crédito | 50 |
| RN-20 | Familia en expansión en madurez → ofrecer seguros | 50 |
| RN-21 | Transaccional en riesgo de abandono → campaña retención | 50 |
| RN-22 | Emprendedor en crecimiento → ofrecer crédito personal | 50 |
| RN-11B | Madurez + alto valor + sin afinidad alta → asesoría inversión | 35 |
| RN-09 | Adquisición → campaña activación digital | 30 |
| RN-10 | Riesgo de abandono → campaña retención | 30 |
| RN-11 | Reactivación → campaña reactivación | 30 |
| RN-04 a RN-08 | Arquetipo → canal preferido | 20 |
| RN-13 a RN-17 | Afinidad de producto → acción CRM | 10 |
| RN-01, RN-02 | Nivel estratégico del cliente (nota en traza) | 5 |
| RN-23 | Sin acción por defecto | 0 |

---

## Casos de prueba incluidos

Todos los casos fueron extraídos directamente de los ejemplos dados por el experto en la entrevista.

| Cliente | Arquetipo | Journey | Acción esperada |
|---|---|---|---|
| CLI-001 | patrimonial | crecimiento | ofrecer_asesoria_inversion |
| CLI-002 | profesional_joven | activacion | ofrecer_tarjeta_credito |
| CLI-003 | familia_expansion | madurez | ofrecer_seguros |
| CLI-004 | transaccional | riesgo_abandono | campana_retencion |

---

## Autores

Edward Cerdas Rodríguez
Angelica Saenz Lacayo
Isabel Galeano Hernandez