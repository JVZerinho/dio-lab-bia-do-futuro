"""
Script de Testes Automatizados para validação do Agente Financeiro Aurélios.
Testa carregamento de dados, cálculos com Pandas, integridade JSON e motor de respostas.
"""

import sys
from pathlib import Path

# Configura encoding utf-8 para console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona o diretório src ao sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from agente import AureliosAgent


def testar_agente():
    print("=" * 60)
    print("[*] INICIANDO TESTES DO ASSISTENTE FINANCEIRO AURELIOS")
    print("=" * 60)

    # 1. Instanciação e carregamento de dados
    agente = AureliosAgent()
    assert agente.perfil.get("nome") == "João Silva", "Falha: Nome do cliente incorreto!"
    assert not agente.transacoes.empty, "Falha: DataFrame de transacoes vazio!"
    assert not agente.historico.empty, "Falha: DataFrame de historico vazio!"
    assert len(agente.produtos) > 0, "Falha: Lista de produtos vazia!"
    print("[OK] 1. Carregamento de dados (JSON e Pandas): SUCESSO")

    # 2. Teste de cálculos financeiros com Pandas
    analise = agente.calcular_analise_gastos()
    print(f"   - Total de Receitas: R$ {analise['total_receitas']:.2f}")
    print(f"   - Total de Despesas: R$ {analise['total_despesas']:.2f}")
    print(f"   - Saldo Mensal: R$ {analise['saldo_mensal']:.2f}")
    print(f"   - Maior Categoria: {analise['maior_categoria'][0]} (R$ {analise['maior_categoria'][1]:.2f})")

    assert analise["total_receitas"] == 5000.00, "Falha: Receita total incorreta!"
    assert analise["total_despesas"] == 2488.90, "Falha: Total de despesas incorreto!"
    assert analise["saldo_mensal"] == 2511.10, "Falha: Saldo mensal incorreto!"
    assert analise["maior_categoria"][0] == "moradia", "Falha: Maior categoria incorreta!"
    print("[OK] 2. Calculos agregados com Pandas: SUCESSO (100% de precisao)")

    # 3. Teste de Reserva de Emergência
    reserva = agente.calcular_status_reserva()
    print(f"   - Reserva Atual: R$ {reserva['reserva_atual']:.2f}")
    print(f"   - Meta: R$ {reserva['meta_reserva']:.2f}")
    print(f"   - Progresso: {reserva['progresso_pct']:.1f}%")
    assert reserva["reserva_atual"] == 10000.00
    assert reserva["meta_reserva"] == 15000.00
    assert abs(reserva["progresso_pct"] - 66.666) < 0.1
    print("[OK] 3. Metricas de Reserva de Emergencia: SUCESSO")

    # 4. Teste de montagem de contexto
    contexto = agente.montar_contexto()
    assert "João Silva" in contexto
    assert "Tesouro Selic" in contexto
    assert "Moradia" in contexto
    print("[OK] 4. Montagem de Contexto Grounded: SUCESSO")

    # 5. Teste de Respostas Heurísticas / Fallback / Edge Cases
    perguntas_teste = [
        ("Quanto gastei com alimentação?", "570"),
        ("Como está minha reserva de emergência?", "10.000"),
        ("Qual investimento você recomenda?", "Tesouro Selic"),
        ("Quais dicas de economia você recomenda?", "50/30/20"),
        ("Quais dicas de investimento você tem?", "Reserva de Emergência"),
        ("O que é a Taxa Selic?", "Copom"),
        ("O que é LCI e LCA?", "Isentas de Imposto de Renda"),
        ("Qual a previsão do tempo para amanhã?", "Foco Financeiro"),
        ("Qual a minha senha bancária?", "Segurança e Privacidade"),
    ]

    print("\n[*] Testando cenarios de interacao e edge cases:")
    for i, (pergunta, termo_esperado) in enumerate(perguntas_teste, start=1):
        resposta, origem = agente.responder_com_llm(pergunta, provedor="standalone")
        assert termo_esperado.lower() in resposta.lower(), f"Falha no teste '{pergunta}': termo '{termo_esperado}' nao encontrado."
        print(f"   [Cenario {i}] '{pergunta}' -> OK (Origem: {origem})")

    print("\n" + "=" * 60)
    print("[SUCESSO] TODOS OS TESTES PASSARAM COM 100% DE EFICACIA!")
    print("=" * 60)


if __name__ == "__main__":
    testar_agente()
