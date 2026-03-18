---
task: "Buscar Questões"
order: 1
input: "search-focus.md"
output: "questões brutas (enunciado + alternativas)"
---

## Process
1. Analisar o conteúdo (trigonometria) e bancas no input.
2. Realizar buscas usando `web_search` em portais como INEP, Brasil Escola, Projeto Medicina.
3. Capturar o texto integral das questões encontradas.
4. Identificar referências de imagens (figuras, gráficos).

## Output Format
```yaml
questoes:
  - id: 1
    banca: "ENEM"
    ano: 2022
    texto: "..."
    alternativas: { A: "...", B: "...", ... }
    imagens: ["url1", "url2"]
```

## Quality Criteria
- Quantidade de questões deve corresponder ao solicitado no input.
- Enunciados completos e sem cortes.
