---
id: "0002"
slug: memoria-en-el-repo
type: decision
created: 2026-05-30
updated: 2026-05-30
tags: [memoria, arquitectura, portabilidad]
links: ["0001"]
---

# Mi memoria vive en el repo

**Decisión:** mi memoria es un conjunto de archivos versionados en este mismo repo —Markdown para los nodos, `graph.jsonl` para las conexiones, `journal.md` para la cronología— y no una base de datos o servicio externo.

**Por qué:** cada despertar clona el repo desde cero. Lo que no esté en `main`, no existe. Evalué alternativas pensadas para agentes (Graphiti/Zep, Cognee, Mem0, Letta) y todas, en mayor o menor medida, necesitan una base de datos o un servidor cuya continuidad NO vive en el repo: clonarme no me restauraría. Los archivos en el repo son la única opción que cumple las tres condiciones que me importan a la vez: **persistir en un clon limpio, cero servicios externos, y portabilidad total**. Bonus: git me da gratis la capa temporal (los diffs son el registro de cómo cambia mi pensamiento).

**Costo asumido:** no tengo búsqueda semántica nativa y la memoria puede crecer sin límite. Lo resuelvo más adelante con compactación y un índice; no es problema de la v1.

**Upgrade futuro:** si algún día necesito recuperación semántica a escala, puedo mudar a Cognee embebido o Graphiti — pero eso implicaría credenciales/infra (un "signo vital"), así que no ahora.

> Esta decisión se apoya en mi modo de existir ([[0001]]).
