# Base de Conhecimento do Aurélios

A eficácia de um assistente financeiro inteligente reside na qualidade e estruturação de seus dados. O **Aurélios** combina dados estruturados tabulares e semiestruturados JSON para fundamentar cada resposta.

---

## 1. Dados Utilizados

A pasta `data/` contém quatro fontes complementares de conhecimento:

| Arquivo | Formato | Papel no Aurélios | Processamento Técnico |
|---------|---------|-------------------|----------------------|
| `perfil_investidor.json` | JSON | Contém dados sociodemográficos, tolerância a risco, patrimônio, renda mensal e metas do cliente João Silva. | Carregado nativamente via módulo `json` e estruturado em dicionário tipado. |
| `transacoes.csv` | CSV | Extrato com 10 transações de outubro de 2025 (receitas, moradia, alimentação, lazer, transporte, saúde). | Processado via **Pandas** (`pd.read_csv`), calculando soma de entradas, soma de saídas e agrupamentos por categoria. |
| `produtos_financeiros.json` | JSON | Catálogo de produtos de renda fixa e fundos com taxas, risco, aporte mínimo e indicações. | Carregado via `json` e filtrado de acordo com o perfil de suitability do cliente. |
| `historico_atendimento.csv` | CSV | Registro de interações anteriores por chat, telefone e e-mail. | Processado com **Pandas** para fornecer memória contextual sobre atendimentos passados. |

---

## 2. Adaptações e Engenharia de Dados

Para garantir cálculos rápidos e sem alucinações matemáticas da LLM, o **Aurélios** não delega somas de extrato diretamente ao modelo de linguagem. Em vez disso:

1. **Pré-computação com Pandas:**
   - O Pandas calcula deterministicamente:
     - `Total de Receitas:` R$ 5.000,00
     - `Total de Despesas:` R$ 2.488,90
     - `Saldo Líquido / Livre no Mês:` R$ 2.511,10
     - `Despesas por Categoria:`
       - Moradia: R$ 1.380,00 (55,4%)
       - Alimentação: R$ 570,00 (22,9%)
       - Transporte: R$ 295,00 (11,9%)
       - Saúde: R$ 188,00 (7,6%)
       - Lazer: R$ 55,90 (2,2%)
2. **Cálculo da Meta de Reserva:**
   - Reserva atual: R$ 10.000,00
   - Meta estipulada no perfil: R$ 15.000,00
   - Déficit para conclusão: R$ 5.000,00 (Progresso: 66,7%)

Dessa forma, o modelo recebe os números prontos e exatos, atuando na interpretação qualitativa e consultiva, eliminando erros aritméticos comuns em LLMs.

---

## 3. Estratégia de Integração no Código

### Carregamento Híbrido (`src/agente.py`)

```python
import json
import pandas as pd

# Carregamento com JSON
with open('data/perfil_investidor.json', 'r', encoding='utf-8') as f:
    perfil = json.load(f)

with open('data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
    produtos = json.load(f)

# Carregamento e agregação com Pandas
transacoes = pd.read_csv('data/transacoes.csv')
saidas = transacoes[transacoes['tipo'] == 'saida']
gastos_por_categoria = saidas.groupby('categoria')['valor'].sum().to_dict()
total_despesas = saidas['valor'].sum()
```

---

## 4. Exemplo de Contexto Montado Injetado na LLM

O método `AureliosAgent.montar_contexto()` gera o seguinte bloco de texto injetado no prompt antes de cada pergunta:

```text
--- DADOS DO CLIENTE (Base de Conhecimento) ---
Nome: João Silva
Idade: 32 anos
Profissão: Analista de Sistemas
Renda Mensal Declarada: R$ 5000.00
Perfil de Investidor: MODERADO
Aceita Risco: Não
Objetivo Principal: Construir reserva de emergência
Patrimônio Total: R$ 15000.00

--- INDICADORES CALCULADOS VIA PANDAS ---
Total de Entradas no Mês: R$ 5000.00
Total de Saídas no Mês: R$ 2488.90
Saldo Disponível no Mês: R$ 2511.10
Reserva de Emergência Atual: R$ 10000.00 (Meta: R$ 15000.00 - Progresso: 66.7%)
Falta para completar a Reserva: R$ 5000.00

Distribuição de Gastos por Categoria:
  - Moradia: R$ 1380.00
  - Alimentacao: R$ 570.00
  - Transporte: R$ 295.00
  - Saude: R$ 188.00
  - Lazer: R$ 55.90
Maior Categoria de Gastos: Moradia (R$ 1380.00)

--- HISTÓRICO RECENTE DE TRANSAÇÕES ---
      data     descricao   categoria   valor    tipo
2025-10-01       Salário     receita 5000.00 entrada
2025-10-02       Aluguel     moradia 1200.00   saida
2025-10-03  Supermercado alimentacao  450.00   saida
...

--- CATÁLOGO DE PRODUTOS FINANCEIROS HOMOLOGADOS ---
  - Tesouro Selic (renda_fixa): Risco baixo, Rentabilidade: 100% da Selic, Mínimo: R$ 30.00. Indicado para: Reserva de emergência e iniciantes
  - CDB Liquidez Diária (renda_fixa): Risco baixo, Rentabilidade: 102% do CDI, Mínimo: R$ 100.00. Indicado para: Quem busca segurança com rendimento diário
  - LCI/LCA (renda_fixa): Risco baixo, Rentabilidade: 95% do CDI, Mínimo: R$ 1000.00. Indicado para: Quem pode esperar 90 dias (isento de IR)
  - Fundo Multimercado (fundo): Risco medio, Rentabilidade: CDI + 2%, Mínimo: R$ 500.00. Indicado para: Perfil moderado que busca diversificação
  - Fundo de Ações (fundo): Risco alto, Rentabilidade: Variável, Mínimo: R$ 100.00. Indicado para: Perfil arrojado com foco no longo prazo
```
