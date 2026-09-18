# Estado Operativo de Codex (codex-universe)

## Rol y Límites
* Motor de ejecución técnica y métricas para Universe Sent Me.
* Se rige estrictamente por `schemas/` y `tests/`.

## Estado Actual
* **Fase:** Inventario consolidado con métricas reales de septiembre 2026.
* **Publicaciones reales:** 79 posts conciliados desde Meta Graph API (5 al 17 de septiembre).
* **Métricas acumuladas del periodo:** 30,660 reacciones | 17,327 compartidos | 594 comentarios.
* **Top 1:** Post 1036844829507460_122161648767072582 (6,747 reacciones, 3,961 compartidos).

## Decisiones Técnicas Congeladas
* Contrato CSV en `data/ingest/content_inventory.csv` con columnas: id, title, type, description, tags, author, status.
* Conservación obligatoria de IDs nativos con prefijo de plataforma (FB-...).
* Filtro de aprobación: `status == 'aprobado'`.
