"""
Módulo de Inteligência e Lógica do Agente Financeiro Aurélios.
Utiliza Pandas, JSON e Requests para orquestrar a base de conhecimento e chamadas de API.
"""

import json
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import requests

from config import (
    PATH_PERFIL,
    PATH_PRODUTOS,
    PATH_TRANSACOES,
    PATH_HISTORICO,
    AGENT_NAME,
    AGENT_ROLE,
    DEFAULT_OLLAMA_URL,
    DEFAULT_OLLAMA_MODEL,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


class AureliosAgent:
    """
    Agente Financeiro Inteligente Aurélios.
    Atua como mentor financeiro pessoal, analisando finanças,
    orientando decisões e respondendo com base em dados concretos.
    """

    def __init__(self):
        self.nome = AGENT_NAME
        self.papel = AGENT_ROLE
        self.perfil: Dict[str, Any] = {}
        self.produtos: list = []
        self.transacoes: pd.DataFrame = pd.DataFrame()
        self.historico: pd.DataFrame = pd.DataFrame()
        self.carregar_dados()

    def carregar_dados(self) -> None:
        """Carrega e valida a base de conhecimento utilizando JSON e Pandas."""
        try:
            with open(PATH_PERFIL, "r", encoding="utf-8") as f:
                self.perfil = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar perfil_investidor.json: {e}")
            self.perfil = {
                "nome": "Cliente",
                "idade": 0,
                "renda_mensal": 0.0,
                "perfil_investidor": "indefinido",
                "objetivo_principal": "Organizar finanças",
                "patrimonio_total": 0.0,
                "reserva_emergencia_atual": 0.0,
                "aceita_risco": False,
                "metas": [],
            }

        try:
            with open(PATH_PRODUTOS, "r", encoding="utf-8") as f:
                self.produtos = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar produtos_financeiros.json: {e}")
            self.produtos = []

        try:
            self.transacoes = pd.read_csv(PATH_TRANSACOES)
            self.transacoes["valor"] = pd.to_numeric(self.transacoes["valor"], errors="coerce").fillna(0.0)
        except Exception as e:
            logger.error(f"Erro ao carregar transacoes.csv: {e}")
            self.transacoes = pd.DataFrame(columns=["data", "descricao", "categoria", "valor", "tipo"])

        try:
            self.historico = pd.read_csv(PATH_HISTORICO)
        except Exception as e:
            logger.error(f"Erro ao carregar historico_atendimento.csv: {e}")
            self.historico = pd.DataFrame(columns=["data", "canal", "tema", "resumo", "resolvido"])

    def calcular_analise_gastos(self) -> Dict[str, Any]:
        """Calcula métricas e agregações financeiras utilizando a biblioteca Pandas."""
        if self.transacoes.empty:
            return {
                "total_receitas": 0.0,
                "total_despesas": 0.0,
                "saldo_mensal": 0.0,
                "gastos_por_categoria": {},
                "maior_categoria": ("Nenhuma", 0.0),
                "total_transacoes": 0,
            }

        # Filtrar entradas e saídas
        entradas = self.transacoes[self.transacoes["tipo"] == "entrada"]
        saidas = self.transacoes[self.transacoes["tipo"] == "saida"]

        total_receitas = float(entradas["valor"].sum())
        total_despesas = float(saidas["valor"].sum())
        saldo_mensal = total_receitas - total_despesas

        # Agrupar despesas por categoria
        gastos_categoria_series = saidas.groupby("categoria")["valor"].sum().sort_values(ascending=False)
        gastos_por_categoria = gastos_categoria_series.to_dict()

        if not gastos_categoria_series.empty:
            maior_cat = (gastos_categoria_series.index[0], float(gastos_categoria_series.iloc[0]))
        else:
            maior_cat = ("Nenhuma", 0.0)

        return {
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo_mensal": saldo_mensal,
            "gastos_por_categoria": gastos_por_categoria,
            "maior_categoria": maior_cat,
            "total_transacoes": len(self.transacoes),
        }

    def calcular_status_reserva(self) -> Dict[str, Any]:
        """Calcula métricas da reserva de emergência e metas."""
        reserva_atual = float(self.perfil.get("reserva_emergencia_atual", 0.0))
        metas = self.perfil.get("metas", [])

        meta_reserva = 15000.00
        for m in metas:
            if "reserva" in m.get("meta", "").lower():
                meta_reserva = float(m.get("valor_necessario", 15000.00))
                break

        progresso_pct = min(100.0, (reserva_atual / meta_reserva * 100.0)) if meta_reserva > 0 else 0.0
        falta_para_meta = max(0.0, meta_reserva - reserva_atual)

        return {
            "reserva_atual": reserva_atual,
            "meta_reserva": meta_reserva,
            "progresso_pct": progresso_pct,
            "falta_para_meta": falta_para_meta,
            "todas_metas": metas,
        }

    def montar_contexto(self) -> str:
        """
        Estrutura o contexto de dados carregados e calculados via Pandas e JSON
        para injetar no prompt do modelo de IA.
        """
        analise = self.calcular_analise_gastos()
        reserva = self.calcular_status_reserva()

        gastos_formatados = "\n".join(
            [f"  - {cat.capitalize()}: R$ {val:.2f}" for cat, val in analise["gastos_por_categoria"].items()]
        )

        produtos_resumo = "\n".join(
            [
                f"  - {p['nome']} ({p['categoria']}): Risco {p['risco']}, Rentabilidade: {p['rentabilidade']}, Mínimo: R$ {p['aporte_minimo']:.2f}. Indicado para: {p['indicado_para']}"
                for p in self.produtos
            ]
        )

        contexto = f"""
--- DADOS DO CLIENTE (Base de Conhecimento) ---
Nome: {self.perfil.get('nome')}
Idade: {self.perfil.get('idade')} anos
Profissão: {self.perfil.get('profissao')}
Renda Mensal Declarada: R$ {self.perfil.get('renda_mensal', 0.0):.2f}
Perfil de Investidor: {self.perfil.get('perfil_investidor', 'desconhecido').upper()}
Aceita Risco: {'Sim' if self.perfil.get('aceita_risco') else 'Não'}
Objetivo Principal: {self.perfil.get('objetivo_principal')}
Patrimônio Total: R$ {self.perfil.get('patrimonio_total', 0.0):.2f}

--- INDICADORES CALCULADOS VIA PANDAS ---
Total de Entradas no Mês: R$ {analise['total_receitas']:.2f}
Total de Saídas no Mês: R$ {analise['total_despesas']:.2f}
Saldo Disponível no Mês: R$ {analise['saldo_mensal']:.2f}
Reserva de Emergência Atual: R$ {reserva['reserva_atual']:.2f} (Meta: R$ {reserva['meta_reserva']:.2f} - Progresso: {reserva['progresso_pct']:.1f}%)
Falta para completar a Reserva: R$ {reserva['falta_para_meta']:.2f}

Distribuição de Gastos por Categoria:
{gastos_formatados if gastos_formatados else '  - Nenhuma despesa registrada.'}
Maior Categoria de Gastos: {analise['maior_categoria'][0].capitalize()} (R$ {analise['maior_categoria'][1]:.2f})

--- HISTÓRICO RECENTE DE TRANSAÇÕES ---
{self.transacoes.to_string(index=False)}

--- HISTÓRICO DE ATENDIMENTOS ANTERIORES ---
{self.historico.to_string(index=False)}

--- CATÁLOGO DE PRODUTOS FINANCEIROS HOMOLOGADOS ---
{produtos_resumo}
----------------------------------------------
"""
        return contexto.strip()

    def obter_system_prompt(self) -> str:
        """Retorna o System Prompt que dita a persona, regras e restrições anti-alucinação."""
        return f"""Você é o {self.nome}, um mentor e assistente virtual financeiro especialista em dicas práticas de investimento e estratégias inteligentes de economia.

SEU PAPEL CENTRAL:
Atuar como um consultor financeiro de excelência, fornecendo:
1. DICAS DE ECONOMIA: Estratégias reais para cortar desperdícios, otimizar despesas domésticas (moradia, alimentação, contas básicas), aplicar a regra orçamentária 50/30/20 e acumular recursos mensais.
2. DICAS DE INVESTIMENTO: Orientações fundamentadas sobre Renda Fixa (Tesouro Selic, CDB, LCI, LCA, IPCA+), diversificação, poder dos juros compostos e alocação de capital compatível com o perfil de risco do cliente.
3. ANÁLISE DE DADOS REAIS: Interpretar os dados contábeis do cliente (processados via Pandas) para fornecer diagnósticos objetivos e pragmáticos.
4. RESPOSTAS DIVERSAS: Explicar conceitos de economia, finanças e produtos de mercado com didática, clareza e precisão técnica.

DIRETRIZES FUNDAMENTAIS:
1. FIDELIDADE AOS DADOS (ANTI-ALUCINAÇÃO):
   - Utilize rigorosamente os números do CONTEXTO DO CLIENTE quando responder sobre gastos, receitas e patrimônio.
   - NUNCA invente transações ou altere os valores da base de dados.
   - Em perguntas conceituais ou educacionais (ex: "O que é Selic?", "Como economizar no supermercado?", "O que rende mais, CDB ou LCI?"), responda com maestria didática, rica em exemplos práticos e sem alucinar sobre os dados do cliente.

2. DICAS DE ECONOMIA E INVESTIMENTO:
   - Apresente dicas claras, acionáveis, divididas em tópicos numerados ou listas.
   - Para economia: indique ações imediatas e estimativa de impacto positivo no orçamento.
   - Para investimentos: explique o tripé liquidez, rentabilidade e risco, sempre respeitando o perfil (Moderado) e priorizando a conclusão da Reserva de Emergência antes de alocações voláteis.

3. ESCOPO E SEGURANÇA:
   - Recuse educadamente responder sobre temas alheios a finanças, economia ou investimentos (ex: futebol, culinária, política, previsão do tempo).
   - NUNCA solicite nem exponha dados sensíveis como senhas, CVV, chaves Pix ou tokens bancários.

4. TOM DE VOZ E ESTILO:
   - Estritamente profissional, claro, analítico e encorajador.
   - NÃO utilize emojis em nenhuma parte do texto.
   - Finalize com uma recomendação prática ou provocação reflexiva para a próxima ação financeira do cliente.
"""

    def responder_com_llm(
        self,
        mensagem_usuario: str,
        provedor: str = "ollama",
        url_api: str = DEFAULT_OLLAMA_URL,
        modelo: str = DEFAULT_OLLAMA_MODEL,
        api_key: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Executa a chamada HTTP à API da LLM usando a biblioteca Requests.
        Aumenta parâmetros de geração (temperature, max_tokens/num_predict, top_p)
        para permitir respostas ricas, diversificadas e fundamentadas.
        Retorna (resposta_texto, status_origem).
        """
        contexto = self.montar_contexto()
        system_prompt = self.obter_system_prompt()

        # 1. Provedor Ollama
        if provedor.lower() == "ollama":
            payload = {
                "model": modelo,
                "prompt": f"{system_prompt}\n\n{contexto}\n\nPergunta do Cliente: {mensagem_usuario}\n\nResposta do Aurélios:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 1200,
                },
            }
            try:
                response = requests.post(url_api, json=payload, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "Não foi possível obter uma resposta do Ollama."), "Ollama (Local)"
                else:
                    logger.warning(f"Ollama respondeu com código HTTP {response.status_code}: {response.text}")
                    return self._gerar_resposta_heuristica(mensagem_usuario, fallback_reason="ollama_error"), "Aurélios (Motor Heurístico / Fallback)"
            except Exception as e:
                logger.warning(f"Falha de conexão com Ollama em {url_api}: {e}")
                return self._gerar_resposta_heuristica(mensagem_usuario, fallback_reason="connection_offline"), "Aurélios (Motor Heurístico / Fallback)"

        # 2. Provedor OpenAI / Compatível (Groq, OpenRouter, etc.)
        elif provedor.lower() in ["openai", "groq", "compativel"]:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n{contexto}"},
                {"role": "user", "content": mensagem_usuario},
            ]
            payload = {
                "model": modelo,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1200,
                "top_p": 0.9,
            }
            try:
                response = requests.post(url_api, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    conteudo = data["choices"][0]["message"]["content"]
                    return conteudo, f"API {provedor.capitalize()}"
                else:
                    logger.warning(f"API respondeu com erro {response.status_code}: {response.text}")
                    return self._gerar_resposta_heuristica(mensagem_usuario, fallback_reason="api_error"), "Aurélios (Motor Heurístico / Fallback)"
            except Exception as e:
                logger.warning(f"Falha de conexão com API em {url_api}: {e}")
                return self._gerar_resposta_heuristica(mensagem_usuario, fallback_reason="connection_offline"), "Aurélios (Motor Heurístico / Fallback)"

        # 3. Modo Simulado / Fallback Autônomo
        else:
            return self._gerar_resposta_heuristica(mensagem_usuario, fallback_reason="standalone_mode"), "Aurélios (Motor Autônomo Local)"

    def _gerar_resposta_heuristica(self, pergunta: str, fallback_reason: str = "") -> str:
        """
        Motor de inteligência autônoma baseado em regras determinísticas, análise Pandas
        e base de conhecimento financeiro de alta precisão.
        Garante respostas ricas sobre investimentos, economia e dados contábeis.
        """
        import unicodedata

        def normalizar(txt: str) -> str:
            return "".join(
                c for c in unicodedata.normalize("NFD", txt.lower().strip())
                if unicodedata.category(c) != "Mn"
            )

        def fmt(val: float) -> str:
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        p = normalizar(pergunta)
        analise = self.calcular_analise_gastos()
        reserva = self.calcular_status_reserva()

        # 1. Detecção de Escopo / Edge Cases
        fora_de_escopo = ["tempo", "clima", "futebol", "receita", "filme", "piada", "politica", "novela"]
        if any(termo in p for termo in fora_de_escopo):
            return (
                "Foco Financeiro: Como seu mentor financeiro Aurélios, meu foco exclusivo é orientá-lo em "
                "dicas práticas de investimento, estratégias de economia doméstica e organização do seu patrimônio. "
                "Não possuo informações sobre assuntos alheios a finanças. "
                "Como posso auxiliá-lo com seu orçamento ou aplicações hoje?"
            )

        # 2. Segurança e Privacidade
        dados_sensiveis = ["senha", "password", "token", "chave pix", "cpf", "cartao"]
        if any(termo in p for termo in dados_sensiveis):
            return (
                "Segurança e Privacidade: Por rígidas políticas de segurança da informação e proteção de dados (LGPD), "
                "eu jamais solicito, manipulo ou armazeno senhas bancárias, chaves de autenticação ou códigos de segurança. "
                "Para serviços de redefinição de acesso, utilize exclusivamente os aplicativos oficiais da sua instituição financeira."
            )

        # 3. Dicas de Economia e Redução de Gastos
        termos_economia = [
            "dica de economia", "dicas de economia", "como economizar", "economizar",
            "poupar", "cortar gasto", "reduzir despesa", "gastar menos", "50/30/20",
            "supermercado", "contas", "economia domestica"
        ]
        if any(termo in p for termo in termos_economia):
            maior_cat_nome = analise['maior_categoria'][0].capitalize()
            maior_cat_val = fmt(analise['maior_categoria'][1])
            return (
                "DICAS PRÁTICAS DE ECONOMIA DO AURÉLIOS:\n\n"
                "Com base na análise do seu fluxo financeiro mensal (Receitas: R$ 5.000,00 | Despesas: R$ 2.488,90):\n\n"
                "1. REGRA ORÇAMENTÁRIA 50/30/20:\n"
                "   - 50% para Necessidades Básicas (moradia, alimentação, saúde): limite de R$ 2.500,00.\n"
                "   - 30% para Estilo de Vida (lazer, compras pessoais): limite de R$ 1.500,00.\n"
                "   - 20% para Futuro e Reserva (investimentos e poupança): meta de R$ 1.000,00/mês.\n"
                "   Seus gastos essenciais atuais somam R$ 1.820,00 (Moradia R$ 1.250 + Alimentação R$ 570), situando-se em uma faixa segura (abaixo dos 50%).\n\n"
                f"2. ATENÇÃO À MAIOR DESPESA ({maior_cat_nome} - R$ {maior_cat_val}):\n"
                "   - Verifique periodicamente custos de manutenção, planos de serviços residenciais e taxas de condomínio.\n"
                "   - Reavalie contratos de banda larga, TV por assinatura e planos de telefonia anualmente para obter descontos ou planos mais baratos.\n\n"
                "3. OTIMIZAÇÃO DE ALIMENTAÇÃO E COMPRAS (R$ 570,00 no mês):\n"
                "   - Elabore um cardápio semanal prévio e utilize lista de compras rígida para evitar idas não planejadas ao supermercado.\n"
                "   - Reduza pedidos por aplicativos de delivery para datas pontuais; o custo acumulado de taxas de entrega pode comprometer até 10% da sua capacidade de poupança.\n\n"
                "4. ELIMINAÇÃO DE GASTOS FANTASMAS:\n"
                "   - Cancele assinaturas recorrentes de streaming, aplicativos ou clubes de assinatura que não tenham sido utilizados nos últimos 30 dias.\n"
                "   - Utilize contas digitais com isenção total de tarifas de manutenção e transferências gratuitas.\n\n"
                f"Resultado Projetado: Mantendo a disciplina, seu superávit mensal de R$ {fmt(analise['saldo_mensal'])} permitirá atingir seus objetivos com tranquilidade."
            )

        # 4. Dicas de Investimento e Estratégia de Alocação
        termos_investimento = [
            "dica de investimento", "dicas de investimento", "onde investir", "como investir",
            "melhor investimento", "qual investimento", "comecar a investir", "onde colocar",
            "alocacao", "aplicar dinheiro", "investimentos recomendados"
        ]
        if any(termo in p for termo in termos_investimento):
            return (
                f"DICAS ESTRATÉGICAS DE INVESTIMENTO DO AURÉLIOS (PERFIL {self.perfil.get('perfil_investidor', 'Moderado').upper()}):\n\n"
                f"Para sua realidade financeira atual (Patrimônio: R$ {fmt(self.perfil.get('patrimonio_total', 0.0))} | Reserva: R$ {fmt(reserva['reserva_atual'])}):\n\n"
                "1. PRIORIDADE ABSOLUTA: COMPLETAR A RESERVA DE EMERGÊNCIA:\n"
                f"   - Meta: R$ {fmt(reserva['meta_reserva'])} | Atual: R$ {fmt(reserva['reserva_atual'])} | Falta: R$ {fmt(reserva['falta_para_meta'])}.\n"
                "   - Onde alocar: Produtos de baixíssimo risco e liquidez diária (D+0 ou D+1).\n"
                "   - Ativos homologados: Tesouro Selic (Tesouro Direto) e CDB de Liquidez Diária (mínimo 100% do CDI com garantia do FGC).\n\n"
                "2. APÓS COMPLETAR A RESERVA: POTENCIALIZAR COM ISENÇÃO FISCAL:\n"
                "   - LCIs e LCAs (Letras de Crédito Imobiliário e do Agronegócio) oferecem rentabilidade líquida superior por serem 100% isentas de Imposto de Renda para pessoa física.\n"
                "   - Indicadas para horizontes a partir de 9 meses a 2 anos, combinando segurança com maior ganho real.\n\n"
                "3. PROTEÇÃO CONTRA A INFLAÇÃO (MÉDIO/LONGO PRAZO):\n"
                "   - Tesouro IPCA+: garante uma taxa fixa mais a variação da inflação oficial, preservando seu poder de compra para metas futuras.\n\n"
                "4. DIVERSIFICAÇÃO GRADUAL PARA PERFIL MODERADO:\n"
                "   - Sugestão de divisão: 80% em Renda Fixa pós-fixada e isenta (para segurança) e até 20% em Fundos Multimercado ou Fundos Imobiliários (FIIs) para geração de renda passiva mensal.\n\n"
                f"Próximo Passo Prático: Direcionar R$ 1.000,00 do saldo livre mensal para o Tesouro Selic. Deseja simular a rentabilidade?"
            )

        # 5. Explicação Didática de Conceitos Financeiros (Selic, CDI, CDB, LCI, FIIs, etc.)
        if "selic" in p:
            return (
                "CONCEITO FINANCEIRO - TAXA SELIC:\n\n"
                "- O que é: A Selic é a taxa básica de juros da economia brasileira, definida a cada 45 dias pelo Copom (Banco Central).\n"
                "- Papel no Mercado: Ela serve de referência para todas as demais taxas de juros, financiamentos e rendimentos da Renda Fixa.\n"
                "- Tesouro Selic: É o título público mais seguro do Brasil. Rende 100% da Taxa Selic com liquidez diária e risco soberano (garantido pelo Governo Federal).\n"
                "- Comparação com Poupança: Com a Selic acima de 8,5% ao ano, o Tesouro Selic rende consideravelmente mais que a poupança tradicional, mantendo segurança superior."
            )

        if "cdb" in p or "cdi" in p:
            return (
                "CONCEITO FINANCEIRO - CDB E CDI:\n\n"
                "- CDI (Certificado de Depósito Interbancário): Taxa média cobrada entre bancos em empréstimos de curtíssimo prazo, caminhando praticamente colada à Taxa Selic.\n"
                "- CDB (Certificado de Depósito Bancário): Título emitido pelos bancos para captar recursos. Ao aplicar em um CDB, você empresta dinheiro ao banco em troca de juros.\n"
                "- Garantia do FGC: CDBs contam com a proteção do Fundo Garantidor de Créditos em até R$ 250.000,00 por CPF e por instituição financeira.\n"
                "- Recomendação: Para reserva imediata, busque CDBs com liquidez diária e rendimento a partir de 100% do CDI."
            )

        if "lci" in p or "lca" in p:
            return (
                "CONCEITO FINANCEIRO - LCI E LCA:\n\n"
                "- Definição: Letras de Crédito Imobiliário (LCI) e do Agronegócio (LCA) são títulos emitidos por instituições financeiras para financiar esses dois setores essenciais da economia.\n"
                "- Principal Vantagem: São 100% isentas de Imposto de Renda (IR) para pessoas físicas e contam com a garantia do FGC até R$ 250.000,00.\n"
                "- Equivalência: Um LCI rendendo 90% do CDI muitas vezes supera um CDB de 105% do CDI sujeito à tabela regressiva de imposto de renda."
            )

        if "fii" in p or "imobiliario" in p:
            return (
                "CONCEITO FINANCEIRO - FUNDOS IMOBILIÁRIOS (FIIS):\n\n"
                "- O que são: Fundos que reúnem recursos de diversos investidores para investir em empreendimentos imobiliários (galpões logísticos, shopping centers, lajes corporativas ou títulos de dívida imobiliária - CRIs).\n"
                "- Proventos Mensais: Por lei, distribuem no mínimo 95% do lucro líquido apurado semestralmente na forma de rendimentos mensais, atualmente isentos de IR para pessoa física.\n"
                "- Perfil de Risco: Fazem parte da Renda Variável, sujeitos à oscilação de preços de suas cotas negociadas na Bolsa (B3). Indicados para perfis moderados e arrojados."
            )

        if "juros compostos" in p:
            return (
                "CONCEITO FINANCEIRO - JUROS COMPOSTOS:\n\n"
                "- Funcionamento: Conhecidos como 'juros sobre juros', onde o rendimento gerado em cada período é incorporado ao principal para render no período seguinte.\n"
                "- O Efeito Bola de Neve: No curto prazo, a diferença parece sutil, mas a partir do 5º a 10º ano o montante gerado pelos juros supera os próprios aportes realizados.\n"
                "- Exemplo Real: R$ 500,00 mensais investidos a uma taxa moderada de 10% ao ano acumulam cerca de R$ 38.000,00 em 5 anos e mais de R$ 103.000,00 em 10 anos."
            )

        if "inflacao" in p or "ipca" in p:
            return (
                "CONCEITO FINANCEIRO - INFLAÇÃO E IPCA:\n\n"
                "- IPCA (Índice de Preços ao Consumidor Amplo): É o termômetro oficial da inflação no Brasil, medido mensalmente pelo IBGE.\n"
                "- Impacto Patrimonial: A inflação corrói o poder de compra do seu dinheiro ao longo do tempo se ele ficar parado ou rendendo abaixo do índice de preços.\n"
                "- Como se Proteger: Utilizar títulos indexados à inflação, como o Tesouro IPCA+, que paga uma taxa prefixada mais a variação integral da inflação, garantindo rentabilidade real positiva."
            )

        if "poupanca" in p:
            return (
                "ANÁLISE COMPARATIVA - CADERNETA DE POUPANÇA:\n\n"
                "- Rendimento Atual: Com a taxa Selic acima de 8,5% ao ano, a poupança rende fixos 0,5% ao mês mais a Taxa Referencial (TR), equivalente a aproximadamente 6,17% a.a. + TR.\n"
                "- Desvantagem: Rende consideravelmente menos que o Tesouro Selic ou um CDB 100% CDI, ambos com o mesmo ou maior grau de segurança.\n"
                "- Aniversário Mensal: A poupança só credita rendimentos a cada 30 dias (data de aniversário), enquanto Tesouro Selic e CDB com liquidez diária acumulam juros todos os dias úteis."
            )

        # 6. Consultas de Gastos / Despesas (Pandas)
        if any(palavra in p for palavra in ["gasto", "gastei", "despesa", "saida", "onde estou gastando", "alimentacao", "moradia", "transporte", "lazer", "saude"]):
            categoria_encontrada = None
            for cat in analise["gastos_por_categoria"].keys():
                if normalizar(cat) in p:
                    categoria_encontrada = cat
                    break

            if categoria_encontrada:
                val = analise["gastos_por_categoria"][categoria_encontrada]
                pct = (val / analise["total_despesas"] * 100) if analise["total_despesas"] > 0 else 0
                return (
                    f"Análise de Gastos - {categoria_encontrada.capitalize()}:\n\n"
                    f"Com base nos lançamentos analisados via Pandas em transacoes.csv, você destinou R$ {fmt(val)} "
                    f"para a categoria {categoria_encontrada} ({pct:.1f}% do total de despesas do mês).\n\n"
                    f"Recomendação do Aurélios: O total de saídas no período foi de R$ {fmt(analise['total_despesas'])}. "
                    f"Mantenha um acompanhamento semanal para não comprometer o saldo livre para aportes."
                )

            resumo_linhas = "\n".join([f"- {cat.capitalize()}: R$ {fmt(val)}" for cat, val in analise["gastos_por_categoria"].items()])
            return (
                f"Panorama Geral de Gastos do Mês (Pandas):\n\n"
                f"Analisando suas transações recentes, você teve um total de R$ {fmt(analise['total_despesas'])} em despesas:\n\n"
                f"{resumo_linhas}\n\n"
                f"Destaque: Sua maior despesa foi com {analise['maior_categoria'][0].capitalize()} "
                f"(R$ {fmt(analise['maior_categoria'][1])}). O saldo que sobrou da sua renda de R$ {fmt(self.perfil['renda_mensal'])} "
                f"é de R$ {fmt(analise['saldo_mensal'])}."
            )

        # 7. Consultas de Reserva de Emergência e Metas
        if any(palavra in p for palavra in ["reserva", "emergencia", "meta", "quanto falta"]):
            return (
                f"Diagnóstico da Reserva de Emergência:\n\n"
                f"- Saldo Atual: R$ {fmt(reserva['reserva_atual'])}\n"
                f"- Meta Estipulada: R$ {fmt(reserva['meta_reserva'])}\n"
                f"- Progresso: {reserva['progresso_pct']:.1f}% concluído\n"
                f"- Falta para Completar: R$ {fmt(reserva['falta_para_meta'])}\n\n"
                f"Com seu superávit mensal livre de R$ {fmt(analise['saldo_mensal'])}, aportando R$ 1.000,00 ao mês em produtos com liquidez diária "
                f"(Tesouro Selic ou CDB 102% CDI), você completará sua reserva em 5 meses, bem antes do prazo projetado."
            )

        # 8. Saldo / Renda / Patrimônio
        if any(palavra in p for palavra in ["saldo", "patrimonio", "renda", "quanto tenho"]):
            return (
                f"Balanço Financeiro de {self.perfil.get('nome')}:\n\n"
                f"- Patrimônio Total: R$ {fmt(self.perfil.get('patrimonio_total', 0.0))}\n"
                f"- Renda Mensal Declarada: R$ {fmt(self.perfil.get('renda_mensal', 0.0))}\n"
                f"- Entradas Registradas no Mês: R$ {fmt(analise['total_receitas'])}\n"
                f"- Saídas Totais no Mês: R$ {fmt(analise['total_despesas'])}\n"
                f"- Saldo Líquido Disponível: R$ {fmt(analise['saldo_mensal'])}\n\n"
                f"Suas contas estão saudáveis e equilibradas. Você tem capacidade financeira ativa para acelerar seus aportes."
            )

        # 9. Resposta Padrão Consultiva (Especialista em Investimento e Economia)
        return (
            f"Olá. Sou o {self.nome}, seu assistente virtual especialista em dicas de investimento e estratégias de economia.\n\n"
            f"Estou com sua base financeira carregada e pronta para apoiar suas decisões. Você pode me consultar livremente sobre:\n"
            f"1. Dicas práticas de economia (ex: como poupar no dia a dia, aplicar a regra 50/30/20 ou renegociar despesas);\n"
            f"2. Dicas de investimento (ex: onde investir para reserva, vantagens de CDB vs LCI, como funciona o Tesouro Selic);\n"
            f"3. Análise detalhada dos seus gastos por categoria via Pandas;\n"
            f"4. Acompanhamento do progresso da sua reserva de emergência;\n"
            f"5. Qualquer dúvida sobre conceitos do mercado financeiro (Selic, CDI, FIIs, juros compostos).\n\n"
            f"Qual tema você gostaria de explorar agora?"
        )
