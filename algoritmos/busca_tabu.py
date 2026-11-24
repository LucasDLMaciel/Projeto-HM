import random
from typing import Dict, Tuple

from problema import (
    InstanciaRCPSP,
    Solucao,
    avaliar_solucao,
    equipes_validas,
    gerar_solucao_inicial,
)


def busca_tabu(
    inst: InstanciaRCPSP,
    max_iter: int = 400,
    tam_vizinhanca: int = 45,
    tenure: int = 15,
    seed: int = 0
) -> Tuple[Solucao, float]:
    rng = random.Random(seed)
    atual = gerar_solucao_inicial(inst, rng)
    custo_atual = avaliar_solucao(inst, atual)

    melhor = atual
    melhor_custo = custo_atual
    lista_tabu: Dict[Tuple, int] = {}

    for it in range(max_iter):
        melhor_cand = None
        melhor_cand_custo = float("inf")
        melhor_mov = None

        perm, aloc = atual
        n = len(perm)

        for _ in range(tam_vizinhanca):
            nova_perm = perm[:]
            nova_aloc = aloc[:]

            if rng.random() < 0.5 and n >= 2:
                i, j = rng.sample(range(n), 2)
                nova_perm[i], nova_perm[j] = nova_perm[j], nova_perm[i]
                mov = ("swap", min(perm[i], perm[j]), max(perm[i], perm[j]))
            else:
                t_id = rng.randrange(n)
                validas = equipes_validas(inst, t_id)
                if len(validas) > 1:
                    nova_eq = rng.choice([e for e in validas if e != nova_aloc[t_id]])
                    nova_aloc[t_id] = nova_eq
                    mov = ("aloc", t_id, nova_eq)
                else:
                    continue

            cand = (nova_perm, nova_aloc)
            custo_cand = avaliar_solucao(inst, cand)

            eh_tabu = lista_tabu.get(mov, -1) > it
            if (not eh_tabu or custo_cand < melhor_custo) and custo_cand < melhor_cand_custo:
                melhor_cand = cand
                melhor_cand_custo = custo_cand
                melhor_mov = mov

        if melhor_cand is None:
            break

        atual = melhor_cand
        custo_atual = melhor_cand_custo
        lista_tabu[melhor_mov] = it + tenure

        if custo_atual < melhor_custo:
            melhor = atual
            melhor_custo = custo_atual

    return melhor, melhor_custo