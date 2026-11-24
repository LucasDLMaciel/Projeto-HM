import math
import random
from typing import Tuple

from problema import (
    InstanciaRCPSP,
    Solucao,
    avaliar_solucao,
    gerar_solucao_inicial,
    gerar_vizinho,
)


def simulated_annealing(
    inst: InstanciaRCPSP,
    T0: float = 1000.0,
    alpha: float = 0.95,
    iter_por_temp: int = 100,
    T_min: float = 0.1,
    seed: int = 0
) -> Tuple[Solucao, float]:
    rng = random.Random(seed)
    atual = gerar_solucao_inicial(inst, rng)
    custo_atual = avaliar_solucao(inst, atual)

    melhor = atual
    melhor_custo = custo_atual

    T = T0
    while T >= T_min:
        for _ in range(iter_por_temp):
            vizinho = gerar_vizinho(inst, atual, rng)
            custo_viz = avaliar_solucao(inst, vizinho)
            delta = custo_viz - custo_atual

            if delta < 0 or rng.random() < math.exp(-delta / T):
                atual = vizinho
                custo_atual = custo_viz
                if custo_atual < melhor_custo:
                    melhor = atual
                    melhor_custo = custo_atual
        T *= alpha

    return melhor, melhor_custo
