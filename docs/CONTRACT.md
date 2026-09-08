# Contrato Codex–Growth OS: estructura mínima de métricas

**Propósito:** Definir lo mínimo que Codex debe implementar antes de recoger datos reales de Universe Sent Me.

**Estado:** Draft  
**Fecha de creación:** 2026-09-08  
**Última actualización:** 2026-09-08  
**Versión:** 1.1  
**Autor:** Manus AI (CGO)  
**Documentos relacionados:** [Estado histórico de Universe 2026](15_00_Estado_Historico_Universe_2026.md), [Fuente maestra y ledgers](14_00_Fuente_Maestra_y_Ledgers.md), [Reglas de aprendizaje](06_00_Reglas_Aprendizaje_Tendencias.md), [Studio Governance](../Studio_Governance.md)  
**Organización:** `GrowthOS/`

## 1. Decisión de arquitectura

Codex debe tener un repositorio operativo propio. El repositorio `universe-sent-me-growth-os` conserva estrategia, contratos, decisiones y documentación de negocio. El repositorio de Codex contiene implementación, validadores, esquemas, pruebas y conectores. Codex no puede modificar el canon narrativo ni emitir conclusiones estratégicas por sí solo.

| Sistema | Responsabilidad |
|---|---|
| Growth OS | Qué medir, por qué medirlo, hipótesis, criterios de decisión y documentación permanente |
| Codex | Cómo registrar, validar, calcular y devolver datos reproducibles |
| Meta/API/otras fuentes | Evidencia externa; lectura solamente hasta autorización explícita |

## 2. Entregable mínimo de Codex

Antes de conectar cuentas o recoger información real, Codex debe entregar: esquemas versionados; validación de filas; IDs únicos; estados de publicación y medición; cálculo de E0/E24/E72; pruebas con datos sintéticos; exportación CSV/JSON; y logs de errores sin secretos.

No debe incluir todavía automatización de publicación, recomendaciones automáticas, scraping, conexiones reales ni modelos de atribución.

## 3. Estructura mínima del repositorio Codex

```text
codex-universe/
├── README.md
├── schemas/
│   ├── publication.schema.json
│   ├── experiment.schema.json
│   ├── metric_snapshot.schema.json
│   └── hypothesis.schema.json
├── data/
│   ├── examples/
│   └── fixtures/
├── src/
│   ├── validate.py
│   ├── normalize.py
│   ├── windows.py
│   └── ids.py
├── tests/
├── docs/
│   └── CONTRACT.md
└── outputs/
```

## 4. Contratos de datos

Cada publicación debe incluir, como mínimo: `publication_id`, `platform`, `account_id`, `meta_post_id` cuando exista, `asset_ref`, `published_at_utc`, `format`, `character`, `circle`, `experiment_id`, `hypothesis_id` y `status`.

Cada snapshot debe incluir: `snapshot_id`, `publication_id`, `captured_at_utc`, `window_type` (`E0`, `E24`, `E72`, `lifetime`), `impressions`, `reach`, `views`, `interactions`, `reactions`, `comments`, `shares`, `saves`, `clicks`, `raw_source`, `source_version` y `quality_status`.

Los valores desconocidos deben ser `null`, nunca cero. Cada métrica debe distinguir entre `observed`, `missing`, `estimated` y `invalid`. Codex no puede inventar datos ni convertir un dato faltante en cero.

## 5. Reglas de validación

`publication_id` y `snapshot_id` son únicos. `E24` no puede existir sin un `E0` válido. `captured_at_utc` debe ser posterior a la publicación. Los snapshots duplicados deben rechazarse o marcarse idempotentemente. Las métricas negativas son inválidas. La fuente y la versión del esquema son obligatorias. Los secretos nunca se guardan en archivos, logs, commits o outputs.

## 6. Estados obligatorios

| Campo | Valores iniciales |
|---|---|
| Publicación | `draft`, `approved`, `scheduled`, `published`, `cancelled`, `failed` |
| Calidad del snapshot | `observed`, `missing`, `estimated`, `invalid` |
| Estado del experimento | `planned`, `running`, `closed`, `insufficient_data` |
| Veredicto de hipótesis | `pending`, `supported`, `unsupported`, `inconclusive` |

`inconclusive` no significa `unsupported`. La falta de muestra debe conservarse como insuficiencia de datos.

## 7. Pruebas sintéticas obligatorias

Codex debe probar: una publicación válida; un snapshot E0 válido; E24 y E72 válidos; duplicado de snapshot; métrica faltante; métrica negativa; timestamp incorrecto; publicación sin `hypothesis_id`; y experimento con muestra insuficiente. Las pruebas deben ejecutarse sin credenciales ni red.

## 8. Criterio de aceptación del CGO

Codex queda listo para la siguiente fase solo cuando todas las pruebas sintéticas pasan, los esquemas están versionados, los outputs son reproducibles, los faltantes se conservan como `null`, los IDs son estables y ningún componente requiere acceso real a plataformas.

Después de esa aprobación se diseña una única captura real de bajo riesgo. No antes.

## 9. Auditoría inicial — 2026-09-08

La implementación inicial fue auditada contra este contrato. Se corrigieron tres defectos: expectativa incorrecta del self-test para `E24`, comparación de ventanas sensible a mayúsculas y falta de comprobación de que `window_type` coincidiera con los timestamps. También se añadió `requirements-dev.txt`.

Resultado: **12 pruebas sintéticas pasan**, los módulos compilan y los self-tests de ventanas y validación pasan. No se conectaron cuentas, no se usaron datos reales y no se modificó ninguna plataforma externa.

## 10. Qué necesita Codex del CGO

Codex necesita únicamente: nombres finales de campos; taxonomía de plataformas, formatos, personajes y círculos; definición exacta de ventanas E0/E24/E72; criterios de calidad; política de faltantes; ejemplos sintéticos; y aprobación de cada transición de fase. No necesita todavía tokens, contraseñas, acceso a cuentas ni permiso para publicar.

**Estado operativo:** No recoger datos reales hasta que este contrato esté implementado, probado y aprobado.

[Estado histórico de Universe 2026]: 15_00_Estado_Historico_Universe_2026.md
[Fuente maestra y ledgers]: 14_00_Fuente_Maestra_y_Ledgers.md
[Reglas de aprendizaje]: 06_00_Reglas_Aprendizaje_Tendencias.md
[Studio Governance]: ../Studio_Governance.md
