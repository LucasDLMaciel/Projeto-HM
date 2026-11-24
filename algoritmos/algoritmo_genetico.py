import random
from typing import List, Tuple

from problema import (
    InstanciaRCPSP,
    Solucao,
    avaliar_solucao,
    gerar_solucao_inicial,
    gerar_vizinho,
)


def _crossover_ox(p1: List[int], p2: List[int], rng: random.Random) -> List[int]:
    n = len(p1)
    if n < 2:
        return p1[:]
    a, b = sorted(rng.sample(range(n), 2))
    filho = [-1] * n
    filho[a:b] = p1[a:b]
    usados = set(filho[a:b])
    restantes = [x for x in p2 if x not in usados]
    idx = 0
    for i in range(n):
        if filho[i] == -1:
            filho[i] = restantes[idx]
            idx += 1
    return filho


def algoritmo_genetico(
    inst: InstanciaRCPSP,
    tam_pop: int = 60,
    geracoes: int = 300,
    taxa_mutacao: float = 0.25,
    elitismo: int = 4,
    seed: int = 0
) -> Tuple[Solucao, float]:
    rng = random.Random(seed)
    populacao = [gerar_solucao_inicial(inst, rng) for _ in range(tam_pop)]
    custos = [avaliar_solucao(inst, ind) for ind in populacao]

    melhor_idx = min(range(tam_pop), key=lambda i: custos[i])
    melhor = populacao[melhor_idx]
    melhor_custo = custos[melhor_idx]

    def torneio(k: int = 3) -> Solucao:
        cand = rng.sample(range(tam_pop), k)
        return populacao[min(cand, key=lambda i: custos[i])]

    for _ in range(geracoes):
        ordenados = sorted(range(tam_pop), key=lambda i: custos[i])
        nova_pop = [populacao[i] for i in ordenados[:elitismo]]

        while len(nova_pop) < tam_pop:
            pai1 = torneio()
            pai2 = torneio()

            filho_perm = _crossover_ox(pai1[0], pai2[0], rng)
            filho_aloc = [
                pai1[1][i] if rng.random() < 0.5 else pai2[1][i]
                for i in range(len(inst.tarefas))
            ]
            filho = (filho_perm, filho_aloc)

            if rng.random() < taxa_mutacao:
                filho = gerar_vizinho(inst, filho, rng)

            nova_pop.append(filho)

        populacao = nova_pop
        custos = [avaliar_solucao(inst, ind) for ind in populacao]

        idx_gen = min(range(tam_pop), key=lambda i: custos[i])
        if custos[idx_gen] < melhor_custo:
            melhor = populacao[idx_gen]
            melhor_custo = custos[idx_gen]

    return melhor, melhor_custo