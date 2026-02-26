# Auditoria Guardrails

## Estado

- Status: `PASS`

## Reglas

| Regla | Estado | Detalle |
|---|---|---|
| `snippets_p1_must_be_zero` | `PASS` | snippets_p1=0 |
| `links_p1_must_be_zero` | `PASS` | links_p1=0 |
| `cierre_p1_must_be_zero` | `PASS` | cierre_p1=0 |
| `plantilla_p1_must_be_zero` | `PASS` | plantilla_p1=0 |
| `continuidad_p1_must_not_regress` | `PASS` | baseline=9, current=0 |
| `saltos_p1_must_not_regress` | `PASS` | baseline=8, current=0 |
| `mermaid_p1_must_not_regress` | `PASS` | baseline=33, current=0 |
| `scaffold_p1_must_not_regress` | `PASS` | baseline=22, current=0 |

## Metricas actuales

```json
{
  "continuidad_p1": 0,
  "continuidad_p2": 9,
  "saltos_p1": 0,
  "saltos_p2": 10,
  "mermaid_p1": 0,
  "mermaid_p2": 0,
  "snippets_p1": 0,
  "snippets_p2": 0,
  "scaffold_p1": 0,
  "scaffold_p2": 0,
  "links_p1": 0,
  "links_p2": 0,
  "cierre_p1": 0,
  "cierre_p2": 0,
  "plantilla_p1": 0,
  "plantilla_p2": 62
}
```
