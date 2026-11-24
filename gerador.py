import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from problema import InstanciaRCPSP, Tarefa, Solucao, detalhar_cronograma


def salvar_instancia_txt(
    inst: InstanciaRCPSP,
    caminho_arquivo: Path,
    seed: Optional[int] = None,
    descricao: str = "Base Sintetica RCPSP"
) -> Path:
    """Salva toda a instância (metadados, tarefas, R_j e C_ij) em arquivo .txt."""
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    linhas = [
        f"# {descricao}",
        f"# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"NUM_TAREFAS={len(inst.tarefas)}",
        f"NUM_EQUIPES={inst.num_equipes}",
        f"SEED={seed if seed is not None else 'N/A'}",
        "",
        "[DISPONIBILIDADE_EQUIPES]",
        " ".join(f"{r:.2f}" for r in inst.disponibilidade),
        "",
        "[TAREFAS]",
        "id;tipo;impacto;sla;duracao;complexidade;relevancia;peso",
    ]

    for t in inst.tarefas:
        linhas.append(
            f"{t.id};{t.tipo};{t.impacto};{t.sla:.2f};{t.duracao:.2f};"
            f"{t.complexidade};{t.relevancia};{t.peso:.2f}"
        )

    linhas.append("")
    linhas.append("[MATRIZ_CAPACIDADE]")
    for linha_cap in inst.capacidade:
        linhas.append(" ".join(str(v) for v in linha_cap))

    caminho_arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho_arquivo


def carregar_instancia_txt(caminho_arquivo: Path) -> InstanciaRCPSP:
    """Lê um arquivo .txt salvo por salvar_instancia_txt e reconstrói a instância."""
    linhas = [l.strip() for l in Path(caminho_arquivo).read_text(encoding="utf-8").splitlines()]
    secao = None
    num_equipes = 0
    disponibilidade = []
    tarefas = []
    capacidade = []

    for linha in linhas:
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("NUM_EQUIPES="):
            num_equipes = int(linha.split("=")[1])
            continue
        if linha in ("[DISPONIBILIDADE_EQUIPES]", "[TAREFAS]", "[MATRIZ_CAPACIDADE]"):
            secao = linha
            continue

        if secao == "[DISPONIBILIDADE_EQUIPES]":
            disponibilidade = [float(x) for x in linha.split()]
        elif secao == "[TAREFAS]":
            if linha.startswith("id;"):
                continue
            p = linha.split(";")
            tarefas.append(Tarefa(
                id=int(p[0]),
                tipo=p[1],
                impacto=p[2],
                sla=float(p[3]),
                duracao=float(p[4]),
                complexidade=int(p[5]),
                relevancia=int(p[6]),
                peso=float(p[7]),
            ))
        elif secao == "[MATRIZ_CAPACIDADE]":
            capacidade.append([int(x) for x in linha.split()])

    return InstanciaRCPSP(
        tarefas=tarefas,
        num_equipes=num_equipes,
        capacidade=capacidade,
        disponibilidade=disponibilidade,
    )


def gerar_instancia_sintetica(
    n_tarefas: int = 42,
    n_equipes: int = 6,
    prob_capacidade: float = 1.0,
    seed: int = 42,
    pasta_saida: str = "dados_sinteticos",
    nome_arquivo: Optional[str] = None
) -> Tuple[InstanciaRCPSP, Path]:
    """Gera a base sintética e obrigatoriamente a persiste em arquivo .txt."""
    rng = random.Random(seed)

    tipos_complexidade = {
        "MANUT. CORRETIVA": 4,
        "REMANEJAMENTO": 3,
        "GERENCIAL": 2,
        "MANUT. PREVENTIVA": 2,
    }
    impactos_sla = {
        "URGENTE": 2.0,
        "ALTO": 3.0,
        "MEDIO": 4.0,
        "BAIXO": 5.0,
    }

    tarefas = []
    for i in range(n_tarefas):
        tipo = rng.choice(list(tipos_complexidade.keys()))
        impacto = rng.choice(list(impactos_sla.keys()))
        complexidade = tipos_complexidade[tipo]
        sla = impactos_sla[impacto]
        relevancia = rng.randint(1, 5)
        peso = float(complexidade * relevancia)
        duracao = round(rng.uniform(0.5, 1.25) * complexidade, 2)

        tarefas.append(Tarefa(
            id=i,
            tipo=tipo,
            impacto=impacto,
            sla=sla,
            duracao=duracao,
            complexidade=complexidade,
            relevancia=relevancia,
            peso=peso,
        ))

    capacidade = []
    for _ in range(n_tarefas):
        linha = [1 if rng.random() <= prob_capacidade else 0 for _ in range(n_equipes)]
        if sum(linha) == 0:
            linha[rng.randrange(n_equipes)] = 1
        capacidade.append(linha)

    disponibilidade = [0.0 for _ in range(n_equipes)]
    inst = InstanciaRCPSP(tarefas, n_equipes, capacidade, disponibilidade)

    if nome_arquivo is None:
        nome_arquivo = f"instancia_{n_tarefas}t_{n_equipes}e_seed{seed}.txt"

    caminho = salvar_instancia_txt(
        inst,
        Path(pasta_saida) / nome_arquivo,
        seed=seed,
        descricao=f"Instancia Sintetica ({n_tarefas} tarefas, {n_equipes} equipes)"
    )
    return inst, caminho


def criar_instancia_tabela3(pasta_saida: str = "dados_sinteticos") -> Tuple[InstanciaRCPSP, Path]:
    """Reconstrói o cenário da Tabela 3 (ótimo = 58.00) e salva em .txt."""
    tarefas = [
        Tarefa(0, "MANUT. CORRETIVA", "URGENTE", sla=2.0, duracao=3.0, complexidade=4, relevancia=3, peso=12.0),
        Tarefa(1, "MANUT. PREVENTIVA", "URGENTE", sla=2.0, duracao=5.0, complexidade=1, relevancia=5, peso=5.0),
        Tarefa(2, "MANUT. CORRETIVA", "URGENTE", sla=2.0, duracao=4.0, complexidade=4, relevancia=2, peso=8.0),
    ]
    inst = InstanciaRCPSP(
        tarefas=tarefas,
        num_equipes=2,
        capacidade=[[1, 1], [1, 1], [1, 1]],
        disponibilidade=[0.0, 0.0],
    )
    caminho = salvar_instancia_txt(
        inst,
        Path(pasta_saida) / "validacao_tabela3.txt",
        descricao="Validacao Tabela 3 (SBPO 2025 - Otimo conhecido = 58.00)"
    )
    return inst, caminho

def salvar_alocacao_txt(
    caminho_arquivo: Path,
    nome_algoritmo: str,
    inst: InstanciaRCPSP,
    sol: Solucao,
    custo_total: float
) -> None:
    """Anexa ao .txt da instância as tarefas alocadas para cada equipe."""
    perm, aloc = sol
    _, por_equipe = detalhar_cronograma(inst, sol)

    linhas = [
        "",
        f"[RESULTADO_ALOCACAO - {nome_algoritmo}]",
        f"Custo total (penalidade): {custo_total:.2f}",
        f"Permutacao (ordem das tarefas): {perm}",
        f"Alocacao (tarefas as equipes): {aloc}",
        "",
        "--- Contagem de Tarefas por Equipe ---",
    ]

    for eq in range(inst.num_equipes):
        ids_eq = [item["id"] for item in por_equipe[eq]]
        linhas.append(f"Equipe {eq + 1} (ID {eq}): {len(ids_eq)} tarefas -> {ids_eq}")

    linhas.append("")
    linhas.append("--- Detalhamento das Tarefas por Equipe ---")
    linhas.append("equipe;tarefa_id;tipo;impacto;inicio;fim;sla;atraso;penalidade")

    for eq in range(inst.num_equipes):
        if not por_equipe[eq]:
            linhas.append(f"Equipe {eq + 1} (ID {eq});SEM_TAREFAS;-;-;-;-;-;-;-")
            continue

        for item in por_equipe[eq]:
            linhas.append(
                f"Equipe {eq + 1} (ID {eq});{item['id']};{item['tipo']};{item['impacto']};"
                f"{item['inicio']:.2f};{item['fim']:.2f};{item['sla']:.2f};"
                f"{item['atraso']:.2f};{item['penalidade']:.2f}"
            )

    with Path(caminho_arquivo).open("a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")