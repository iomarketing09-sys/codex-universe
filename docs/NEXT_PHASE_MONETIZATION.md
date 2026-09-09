# Siguiente fase Codex: monetización y experimento Wilfred

**Propósito:** Definir la implementación mínima para registrar publicaciones, contexto de monetización e hipótesis sin automatizar publicación ni modificar cuentas.

**Estado:** Draft  
**Fecha de creación:** 2026-09-09  
**Última actualización:** 2026-09-09  
**Versión:** 1.0  
**Autor:** Manus AI (CGO)  
**Documentos relacionados:** [Contrato Codex–Growth OS](CONTRACT.md), [Autorización de captura](REAL_CAPTURE_AUTHORIZATION_20260908.json), `GrowthOS/16_00_Contrato_Codex_Metricas.md`, `GrowthOS/17_00_Protocolo_Primera_Captura_Real.md`  
**Organización:** `docs/`

## Decisión

Codex no debe rehacerse. Debe añadir una capa de contexto experimental y monetización sobre los esquemas actuales. La publicación seguirá siendo manual; Codex solo registra, valida, exporta y compara.

## Cambios mínimos

Añadir a la publicación o a un registro experimental:

| Campo | Regla |
|---|---|
| `experiment_id` | ID estable del experimento |
| `hypothesis_id` | ID estable de la hipótesis |
| `monetization_active` | Booleano observado, nunca inferido |
| `monetization_source` | `user_reported`, `meta_reported` o `missing` |
| `character_role` | `test` o `control` |
| `content_family` | Taxonomía editorial existente |
| `manual_publication` | Booleano observado |
| `revenue_amount` | Número o `null`; no estimar |
| `revenue_currency` | `USD` o `null` |
| `revenue_window` | Ventana explícita o `null` |
| `revenue_source` | Fuente y fecha del dato |

No mezclar ingreso acumulado de la cuenta con ingreso atribuible a una publicación. Si Meta no entrega atribución por post, registrar el monto como `account_total`, no como revenue del contenido.

## Experimento inicial

`experiment_id`: `EXP-2026-09-WILFRED-MON-01`  
`hypothesis_id`: `H-WILFRED-MON-01`  
Hipótesis: con monetización activa, posts comparables de Wilfred con humor seco o irreverente generan más ingreso por publicación que controles comparables de otros personajes.

La muestra mínima para un veredicto es **3 posts de Wilfred y 3 controles**. Antes de esa muestra el estado debe ser `insufficient_data` o `inconclusive`; nunca `supported`.

## Registro inicial

Los dos posts del 5 de septiembre ya deben importarse como publicaciones observadas, pero sin inventar métricas. El post de Wilfred del 6 de septiembre y sus USD 1.48 se registran como `user_reported` hasta que exista evidencia nativa exportable. Los USD 2.25 se registran como total acumulado de cuenta al momento del reporte, no como suma atribuida a posts.

## Criterios de aceptación

Codex debe probar con fixtures sintéticos que: los campos nuevos son opcionales o `null`; una fuente `user_reported` no se convierte en `meta_reported`; el ingreso acumulado no se asigna a un post; faltantes permanecen `null`; los controles y tests se cuentan por separado; y un experimento con menos de 3+3 publicaciones queda como insuficiente.

No implementar todavía conectores, publicación automática, recomendaciones automáticas ni captura recurrente.
