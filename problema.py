import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class Tarefa:
    id: int
    tipo: str
    impacto: str
    sla: float         # SLA_i (em dias)
    duracao: float     # p_i (em dias)
    complexidade: int  # a_i (Tabela 2)
    relevancia: int    # b_i (Tabela 1)
    peso: float        # w_i = a_i * b_i (Equação 9)


@dataclass
class InstanciaRCPSP:
    tarefas: List[Tarefa]
    num_equipes: int
    capacidade: List[List[int]]   # C_ij: 1 se equipe j pode executar tarefa i
    disponibilidade: List[float]  # R_j: disponibilidade inicial da equipe j


# Solução = (permutacao_de_tarefas, alocacao_por_id_de_tarefa)
Solucao = Tuple[List[int], List[int]]


def equipes_validas(inst: InstanciaRCPSP, tarefa_id: int) -> List[int]:
    return [j for j in range(inst.num_equipes) if inst.capacidade[tarefa_id][j] == 1]


def gerar_solucao_inicial(inst: InstanciaRCPSP, rng: random.Random) -> Solucao:
    n = len(inst.tarefas)
    perm = list(range(n))
    rng.shuffle(perm)
    aloc = [rng.choice(equipes_validas(inst, i)) for i in range(n)]
    return perm, aloc


def avaliar_solucao(inst: InstanciaRCPSP, sol: Solucao) -> float:
    """Função objetivo: min sum(w_i * max(0, f_i - SLA_i))."""
    perm, aloc = sol
    tempo_equipe = list(inst.disponibilidade)
    penalidade_total = 0.0

    for tarefa_id in perm:
        equipe = aloc[tarefa_id]
        tarefa = inst.tarefas[tarefa_id]

        inicio = tempo_equipe[equipe]
        fim = inicio + tarefa.duracao
        tempo_equipe[equipe] = fim

        atraso = max(0.0, fim - tarefa.sla)
        penalidade_total += tarefa.peso * atraso

    return penalidade_total


def gerar_vizinho(inst: InstanciaRCPSP, sol: Solucao, rng: random.Random) -> Solucao:
    """Perturbação: troca de ordem na permutação ou troca de equipe alocada."""
    perm, aloc = sol
    nova_perm = perm[:]
    nova_aloc = aloc[:]
    n = len(perm)

    if rng.random() < 0.5 and n >= 2:
        i, j = rng.sample(range(n), 2)
        nova_perm[i], nova_perm[j] = nova_perm[j], nova_perm[i]
    else:
        t_id = rng.randrange(n)
        validas = equipes_validas(inst, t_id)
        if len(validas) > 1:
            outras = [e for e in validas if e != nova_aloc[t_id]]
            nova_aloc[t_id] = rng.choice(outras)
        elif n >= 2:
            i, j = rng.sample(range(n), 2)
            nova_perm[i], nova_perm[j] = nova_perm[j], nova_perm[i]

    return nova_perm, nova_aloc

def detalhar_cronograma(
    inst: InstanciaRCPSP,
    sol: Solucao
) -> Tuple[float, Dict[int, List[dict]]]:
    """
    Reconstrói o cronograma detalhado da solução, agrupando as tarefas
    em ordem de execução para cada equipe.
    """
    perm, aloc = sol
    tempo_equipe = list(inst.disponibilidade)
    penalidade_total = 0.0
    por_equipe: Dict[int, List[dict]] = {j: [] for j in range(inst.num_equipes)}

    for tarefa_id in perm:
        equipe = aloc[tarefa_id]
        tarefa = inst.tarefas[tarefa_id]

        inicio = tempo_equipe[equipe]
        fim = inicio + tarefa.duracao
        tempo_equipe[equipe] = fim

        atraso = max(0.0, fim - tarefa.sla)
        penalidade = tarefa.peso * atraso
        penalidade_total += penalidade

        por_equipe[equipe].append({
            "id": tarefa.id,
            "tipo": tarefa.tipo,
            "impacto": tarefa.impacto,
            "inicio": inicio,
            "fim": fim,
            "sla": tarefa.sla,
            "atraso": atraso,
            "peso": tarefa.peso,
            "penalidade": penalidade,
        })

    return penalidade_total, por_equipe