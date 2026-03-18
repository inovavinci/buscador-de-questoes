---
task: "Extrair Gabarito"
order: 2
input: "questões brutas"
output: "questões com gabarito"
---

## Process
1. Para cada questão encontrada, buscar o gabarito oficial.
2. Validar se o gabarito corresponde exatamente à questão pelo ano/banca.
3. Adicionar o campo `gabarito` ao objeto da questão.

## Output Format
YAML com campo `gabarito` adicionado.
