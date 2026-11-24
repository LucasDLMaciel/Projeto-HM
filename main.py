import statistics
import time
from pathlib import Path

from algoritmos.simulated_annealing import simulated_annealing
from gerador import criar_instancia_tabela3, gerar_instancia_sintetica
from problema import InstanciaRCPSP

from gerador import (
    criar_instancia_tabela3,
    gerar_instancia_sintetica,
    salvar_alocacao_txt,
)
from problema import InstanciaRCPSP


def executar_benchmark(
    inst: InstanciaRCPSP,
    caminho_base: Path,
    nome_cenario: str,
    n_execucoes: int = 10
) -> None:
    algoritmos = {
        "Simulated Annealing (Artigo)": lambda s: simulated_annealing(inst, seed=s),
    }

    print(f"\n{'='*80}")
    print(f"CENÁRIO: {nome_cenario} ({len(inst.tarefas)} tarefas, {inst.num_equipes} equipes)")
    print(f"Base salva em: {caminho_base} | Execuções por algoritmo: {n_execucoes}")
    print(f"{'='*80}")
    print(f"{'Algoritmo':<30} | {'Melhor':>10} | {'Média':>10} | {'Desvio':>8} | {'Tempo (s)':>9}")
    print("-" * 80)

    for nome, func in algoritmos.items():
        custos = []
        tempos = []
        melhor_sol = None
        melhor = float("inf")

        for run in range(n_execucoes):
            t0 = time.perf_counter()
            sol, custo = func(run)
            tempos.append(time.perf_counter() - t0)
            custos.append(custo)

            if custo < melhor:
                melhor = custo
                melhor_sol = sol

        media = statistics.mean(custos)
        desvio = statistics.stdev(custos) if len(custos) > 1 else 0.0
        tempo_med = statistics.mean(tempos)

        print(f"{nome:<30} | {melhor:10.2f} | {media:10.2f} | {desvio:8.2f} | {tempo_med:9.4f}")

        if melhor_sol is not None:
            salvar_alocacao_txt(caminho_base, nome, inst, melhor_sol, melhor)


def main() -> None:
    # 1) Cenário de validação da Tabela 3 (3 tarefas, 2 equipes, ótimo = 58.00)
    inst_val, arq_val = criar_instancia_tabela3()
    executar_benchmark(inst_val, arq_val, "Validação Tabela 3", n_execucoes=5)

    # 2) Cenário principal do artigo (42 tarefas, 6 equipes)
    inst_42, arq_42 = gerar_instancia_sintetica(
        n_tarefas=42,
        n_equipes=6,
        prob_capacidade=1.0,
        seed=42
    )
    executar_benchmark(inst_42, arq_42, "Sintético Principal (Artigo)", n_execucoes=10)

    # 3) Exemplo de cenário extra com especialização de equipes (C_ij parcial)
    inst_esp, arq_esp = gerar_instancia_sintetica(
        n_tarefas=60,
        n_equipes=8,
        prob_capacidade=0.65,
        seed=100
    )
    executar_benchmark(inst_esp, arq_esp, "Sintético Especializado (60t, 8e)", n_execucoes=10)


if __name__ == "__main__":
    main()