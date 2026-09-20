"""Wrappers SymPy para as operações de Álgebra Linear do laboratório.

Cada função de cálculo devolve sempre o par (resultado, passos), onde `passos`
é uma lista de `Passo` — o contrato comum usado por todos os módulos para
implementar o modo pedagógico "passo-a-passo" sem duplicar lógica de
apresentação.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMACOES = standard_transformations + (implicit_multiplication_application, convert_xor)


@dataclass
class Passo:
    """Um passo do modo pedagógico passo-a-passo."""

    titulo: str
    detalhe: str = ""
    latex: Optional[str] = None


def para_sympy(m: np.ndarray) -> sp.Matrix:
    """Converte um array NumPy (matriz ou vetor) numa Matrix SymPy racional."""
    return sp.Matrix(m.tolist()).applyfunc(sp.nsimplify)


def para_numpy(m: sp.Matrix) -> np.ndarray:
    """Converte uma Matrix SymPy num array NumPy de floats."""
    return np.array(m.evalf().tolist(), dtype=float)


# --------------------------------------------------------------------------
# Matrizes
# --------------------------------------------------------------------------

def somar_matrizes(a: sp.Matrix, b: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    if a.shape != b.shape:
        raise ValueError(f"Dimensões incompatíveis para soma: {a.shape} vs {b.shape}")
    resultado = a + b
    n_linhas, n_colunas = a.shape
    passos = [
        Passo("Verificar dimensões", f"A e B são ambas {n_linhas}×{n_colunas} — a soma é possível."),
    ]
    for i in range(n_linhas):
        for j in range(n_colunas):
            passos.append(Passo(
                f"Calcular c_{i + 1}{j + 1} = a_{i + 1}{j + 1} + b_{i + 1}{j + 1}", "",
                latex=f"{sp.latex(a[i, j])} + {sp.latex(b[i, j])} = {sp.latex(resultado[i, j])}",
            ))
    passos.append(Passo("Matriz soma obtida", "", latex=f"A + B = {sp.latex(resultado)}"))
    return resultado, passos


def multiplicar_escalar(k: float, a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    k = sp.nsimplify(k)
    resultado = k * a
    n_linhas, n_colunas = a.shape
    passos = []
    for i in range(n_linhas):
        for j in range(n_colunas):
            passos.append(Passo(
                f"Calcular a entrada ({i + 1}, {j + 1}) de k·A", "",
                latex=f"{sp.latex(k)} \\cdot {sp.latex(a[i, j])} = {sp.latex(resultado[i, j])}",
            ))
    passos.append(Passo("Matriz k·A obtida", "", latex=f"{sp.latex(k)} \\cdot A = {sp.latex(resultado)}"))
    return resultado, passos


def multiplicar_matrizes(a: sp.Matrix, b: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            f"Dimensões incompatíveis para produto: A é {a.shape}, B é {b.shape} "
            "(nº de colunas de A tem de ser igual ao nº de linhas de B)."
        )
    resultado = a * b
    n_linhas, n_interno, n_colunas = a.shape[0], a.shape[1], b.shape[1]
    passos = [
        Passo("Verificar dimensões",
              f"A é {n_linhas}×{n_interno}, B é {n_interno}×{n_colunas} — "
              "colunas de A = linhas de B, o produto é possível."),
    ]
    for i in range(n_linhas):
        for j in range(n_colunas):
            termos = " + ".join(f"({sp.latex(a[i, k])})({sp.latex(b[k, j])})" for k in range(n_interno))
            passos.append(Passo(
                f"Calcular c_{i + 1}{j + 1} (linha {i + 1} de A vezes coluna {j + 1} de B)", "",
                latex=f"{termos} = {sp.latex(resultado[i, j])}",
            ))
    passos.append(Passo("Matriz produto obtida", "", latex=f"A \\times B = {sp.latex(resultado)}"))
    return resultado, passos


def transpor(a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    resultado = a.T
    passos = [
        Passo("Trocar linhas por colunas", "A transposta troca a linha i com a coluna i.",
              latex=f"{sp.latex(a)}^T = {sp.latex(resultado)}"),
    ]
    return resultado, passos


def escalonar(a: sp.Matrix, colunas_pivo: Optional[int] = None) -> tuple[sp.Matrix, list[Passo]]:
    """Eliminação de Gauss até à forma escalonada (não reduzida), mostrando
    cada operação de linha — ao contrário de `.rref()`, que só devolve o
    resultado final.

    `colunas_pivo` limita a busca de pivôs às primeiras N colunas (usado por
    `resolver_sistema` sobre a matriz aumentada [A|b], para nunca escolher um
    pivô na coluna de b); por omissão usa todas as colunas de `a`."""
    m = a.copy()
    n_linhas, n_colunas = m.shape
    limite = colunas_pivo if colunas_pivo is not None else n_colunas
    passos = [Passo("Matriz inicial", "", latex=sp.latex(m))]
    linha_pivo = 0
    for col in range(limite):
        if linha_pivo >= n_linhas:
            break
        if m[linha_pivo, col] == 0:
            candidato = next((r for r in range(linha_pivo + 1, n_linhas) if m[r, col] != 0), None)
            if candidato is None:
                continue
            m.row_swap(linha_pivo, candidato)
            passos.append(Passo(f"Trocar L{linha_pivo + 1} com L{candidato + 1}",
                                 "Para obter um pivô não-nulo nesta coluna.", latex=sp.latex(m)))
        pivo = m[linha_pivo, col]
        for r in range(linha_pivo + 1, n_linhas):
            if m[r, col] != 0:
                fator = sp.nsimplify(m[r, col] / pivo)
                m[r, :] = m[r, :] - fator * m[linha_pivo, :]
                passos.append(Passo(
                    f"L{r + 1} ← L{r + 1} − ({sp.latex(fator)})·L{linha_pivo + 1}",
                    "Anular a entrada abaixo do pivô.", latex=sp.latex(m),
                ))
        linha_pivo += 1
    passos.append(Passo("Forma escalonada obtida", "", latex=sp.latex(m)))
    return m, passos


# --------------------------------------------------------------------------
# Determinantes e Inversa
# --------------------------------------------------------------------------

def determinante(a: sp.Matrix) -> tuple[sp.Expr, list[Passo]]:
    if a.shape[0] != a.shape[1]:
        raise ValueError("O determinante só está definido para matrizes quadradas.")
    n = a.shape[0]
    valor = a.det()
    passos = [Passo("Confirmar que a matriz é quadrada", f"A é {n}×{n}.")]

    if n == 1:
        passos.append(Passo("Determinante de uma matriz 1×1", "",
                             latex=f"\\det(A) = {sp.latex(a[0, 0])}"))
    elif n == 2:
        a11, a12, a21, a22 = a[0, 0], a[0, 1], a[1, 0], a[1, 1]
        p1, p2 = a11 * a22, a12 * a21
        passos.append(Passo(
            "Aplicar a fórmula 2×2", "det(A) = a₁₁·a₂₂ − a₁₂·a₂₁",
            latex=(f"({sp.latex(a11)})({sp.latex(a22)}) - ({sp.latex(a12)})({sp.latex(a21)}) "
                   f"= {sp.latex(p1)} - {sp.latex(p2)} = {sp.latex(valor)}"),
        ))
    elif n == 3:
        m = a
        termos_pos = [
            (m[0, 0], m[1, 1], m[2, 2]),
            (m[0, 1], m[1, 2], m[2, 0]),
            (m[0, 2], m[1, 0], m[2, 1]),
        ]
        termos_neg = [
            (m[0, 2], m[1, 1], m[2, 0]),
            (m[0, 0], m[1, 2], m[2, 1]),
            (m[0, 1], m[1, 0], m[2, 2]),
        ]
        produtos_pos = [x * y * z for x, y, z in termos_pos]
        produtos_neg = [x * y * z for x, y, z in termos_neg]
        soma_pos, soma_neg = sum(produtos_pos), sum(produtos_neg)

        def fmt(termos, produtos):
            fatores = " + ".join(f"({sp.latex(x)})({sp.latex(y)})({sp.latex(z)})" for x, y, z in termos)
            return f"{fatores} = " + " + ".join(sp.latex(p) for p in produtos)
        passos.append(Passo(
            "Diagonais principais (regra de Sarrus)",
            "Multiplicar cada diagonal descendente, incluindo as que \"dão a volta\" à matriz.",
            latex=f"{fmt(termos_pos, produtos_pos)} = {sp.latex(soma_pos)}",
        ))
        passos.append(Passo(
            "Diagonais secundárias",
            "Multiplicar cada diagonal ascendente, incluindo as que \"dão a volta\" à matriz.",
            latex=f"{fmt(termos_neg, produtos_neg)} = {sp.latex(soma_neg)}",
        ))
        passos.append(Passo(
            "Subtrair as diagonais secundárias às principais",
            "det(A) = (soma das diagonais principais) − (soma das diagonais secundárias).",
            latex=f"{sp.latex(soma_pos)} - ({sp.latex(soma_neg)}) = {sp.latex(valor)}",
        ))
    else:
        parcelas = []
        for j in range(n):
            menor = a.minor_submatrix(0, j)
            sinal = (-1) ** j
            cofator = sinal * menor.det()
            sinal_str = "+" if sinal == 1 else "-"
            parcelas.append(f"{sinal_str}({sp.latex(a[0, j])}) \\det{sp.latex(menor)}")
        passos.append(Passo(
            "Expansão de Laplace ao longo da 1ª linha",
            "det(A) = Σⱼ (−1)^(1+j) · a₁ⱼ · det(menor sem a linha 1 e a coluna j).",
            latex=" ".join(parcelas) + f" = {sp.latex(valor)}",
        ))
    return valor, passos


def inversa(a: sp.Matrix) -> tuple[Optional[sp.Matrix], list[Passo]]:
    """Assume que det(a) já foi calculado e mostrado (ex. via `determinante()`)
    — não repete esse passo, só verifica singularidade e, se possível, inverte
    mostrando a matriz dos cofatores e a adjugada."""
    if a.shape[0] != a.shape[1]:
        raise ValueError("A inversa só está definida para matrizes quadradas.")
    n = a.shape[0]
    det_a = a.det()
    passos: list[Passo] = []
    if det_a == 0:
        passos.append(Passo("Verificar singularidade",
                             "det(A) = 0 → a matriz não é invertível (é singular)."))
        return None, passos

    if n == 2:
        a11, a12, a21, a22 = a[0, 0], a[0, 1], a[1, 0], a[1, 1]
        adjugada = sp.Matrix([[a22, -a12], [-a21, a11]])
        passos.append(Passo(
            "Formar a adjugada (caso 2×2: trocar a diagonal principal e negar a secundária)", "",
            latex=f"adj(A) = {sp.latex(adjugada)}",
        ))
    else:
        cofatores = a.cofactor_matrix()
        adjugada = cofatores.T
        passos.append(Passo(
            "Calcular a matriz dos cofatores",
            "Cada cofator Cᵢⱼ = (−1)^(i+j) · det(menor sem a linha i e a coluna j).",
            latex=f"C = {sp.latex(cofatores)}",
        ))
        passos.append(Passo(
            "Transpor os cofatores para obter a adjugada", "adj(A) = Cᵗ.",
            latex=f"adj(A) = C^T = {sp.latex(adjugada)}",
        ))

    resultado = adjugada / det_a
    passos.append(Passo(
        "Dividir a adjugada pelo determinante", "A⁻¹ = (1/det(A))·adj(A).",
        latex=f"A^{{-1}} = \\frac{{1}}{{{sp.latex(det_a)}}} {sp.latex(adjugada)} = {sp.latex(resultado)}",
    ))
    verificacao = sp.simplify(a * resultado)
    passos.append(Passo(
        "Verificar: A · A⁻¹ deve dar a matriz identidade", "",
        latex=f"A \\, A^{{-1}} = {sp.latex(verificacao)}",
    ))
    return resultado, passos


def matriz_com_entrada_variavel(a: np.ndarray, posicao: tuple[int, int], valor: float) -> np.ndarray:
    """Devolve uma cópia de `a` com a entrada em `posicao` substituída por `valor`."""
    b = a.astype(float).copy()
    b[posicao] = valor
    return b


# --------------------------------------------------------------------------
# Sistemas Lineares
# --------------------------------------------------------------------------

def resolver_sistema(
    a: sp.Matrix, b: sp.Matrix, simbolos: Optional[list[sp.Symbol]] = None
) -> tuple[object, list[Passo]]:
    """Se `simbolos` não for dado, usa nomes genéricos x1, x2, ... — mas para
    que uma eventual solução indeterminada apareça com o(s) mesmo(s) nome(s)
    de variável escolhidos pelo utilizador (em vez de um parâmetro livre com
    nome genérico), o `linsolve` deve resolver diretamente sobre `simbolos`."""
    n_vars = a.shape[1]
    if simbolos is None:
        simbolos = list(sp.symbols(f"x1:{n_vars + 1}"))
    solucoes = sp.linsolve((a, b), simbolos)

    aumentada = a.row_join(b)
    _, passos_escalonamento = escalonar(aumentada, colunas_pivo=n_vars)
    passos = [
        Passo("Montar a matriz aumentada [A | b]",
              "Cada linha de A·x = b passa a ser uma linha desta matriz, com b na última coluna.",
              latex=f"[A \\mid b] = {sp.latex(aumentada)}"),
    ]
    # passos_escalonamento[0] repete a matriz inicial, já mostrada no passo acima
    passos += passos_escalonamento[1:]

    if len(solucoes) == 0:
        passos.append(Passo(
            "Interpretar a forma escalonada",
            "Uma linha do tipo 0 = c (com c ≠ 0) mostra que o sistema é impossível (sem solução).",
        ))
    else:
        classificacao = classificar_sistema(solucoes, simbolos)
        if classificacao == "indeterminado":
            passos.append(Passo(
                "Interpretar a forma escalonada",
                "Há menos equações independentes do que incógnitas — pelo menos uma "
                "variável fica livre (sem pivô próprio), dando infinitas soluções.",
            ))
        else:
            passos.append(Passo(
                "Interpretar a forma escalonada",
                "Cada incógnita tem uma linha com pivô próprio — a solução é única.",
            ))
        passos.append(Passo("Solução", "", latex=formatar_solucao_sistema(solucoes, simbolos)))
    return solucoes, passos


def classificar_sistema(solucoes, simbolos: list[sp.Symbol]) -> str:
    """Classifica o sistema a partir do resultado de `linsolve`: "determinado"
    (solução única), "indeterminado" (infinitas soluções, com parâmetro livre)
    ou "impossivel" (sem solução)."""
    if len(solucoes) == 0:
        return "impossivel"
    tupla = next(iter(solucoes))
    livres: set[sp.Symbol] = set()
    for expr in tupla:
        livres |= expr.free_symbols & set(simbolos)
    return "indeterminado" if livres else "determinado"


def formatar_solucao_sistema(solucoes, simbolos: list[sp.Symbol]) -> Optional[str]:
    """Devolve a solução em LaTeX como "x = ..., y = ...", ou None se o
    sistema não tiver solução (impossível)."""
    if len(solucoes) == 0:
        return None
    tupla = next(iter(solucoes))
    partes = [f"{sp.latex(s)} = {sp.latex(v)}" for s, v in zip(simbolos, tupla)]
    return r",\ \ ".join(partes)


def analisar_equacoes(
    variaveis_texto: str, textos_equacoes: list[str]
) -> tuple[sp.Matrix, sp.Matrix, list[sp.Symbol], list[Passo]]:
    """Interpreta equações escritas em texto livre (ex. "2x + 4y = 6") sobre as
    incógnitas dadas em `variaveis_texto` (ex. "x, y"), devolvendo a matriz de
    coeficientes A, o vetor b, os símbolos usados e os passos pedagógicos.

    Lança ValueError com uma mensagem amigável (nunca uma exceção crua do
    SymPy) se as incógnitas estiverem vazias, uma equação não puder ser
    interpretada, ou não for linear nas incógnitas indicadas.
    """
    if not variaveis_texto.strip():
        raise ValueError("Define pelo menos uma incógnita (ex.: x, y).")
    resultado = sp.symbols(variaveis_texto)
    simbolos = list(resultado) if isinstance(resultado, tuple) else [resultado]
    if not all(isinstance(s, sp.Symbol) for s in simbolos):
        raise ValueError(f"Não consegui interpretar as incógnitas \"{variaveis_texto}\".")
    mapa_simbolos = {s.name: s for s in simbolos}

    passos = [Passo("Definir as incógnitas", f"Variáveis: {', '.join(s.name for s in simbolos)}")]
    linhas_a, valores_b = [], []
    for i, texto in enumerate(textos_equacoes, start=1):
        texto = texto.strip()
        if not texto:
            raise ValueError(f"A equação {i} está vazia.")
        if "=" not in texto:
            raise ValueError(f"Equação {i} inválida: falta o sinal \"=\" (ex.: 2x + 4y = 6).")
        lado_esq, lado_dir = texto.split("=", 1)
        try:
            expr_esq = parse_expr(lado_esq, local_dict=mapa_simbolos, transformations=_TRANSFORMACOES)
            expr_dir = parse_expr(lado_dir, local_dict=mapa_simbolos, transformations=_TRANSFORMACOES)
        except (sp.SympifyError, SyntaxError, TypeError, AttributeError) as erro:
            raise ValueError(f"Equação {i} não foi entendida: \"{texto}\".") from erro
        equacao = sp.Eq(expr_esq, expr_dir)
        try:
            linha, valor = sp.linear_eq_to_matrix([equacao], simbolos)
        except (ValueError, NotImplementedError) as erro:
            raise ValueError(
                f"Equação {i} não é linear nas incógnitas definidas "
                f"({', '.join(s.name for s in simbolos)})."
            ) from erro
        linhas_a.append(linha.tolist()[0])
        valores_b.append(valor.tolist()[0][0])
        passos.append(Passo(f"Equação {i}", "", latex=sp.latex(equacao)))

    a_matriz = sp.Matrix(linhas_a)
    b_vetor = sp.Matrix(valores_b)
    passos.append(Passo(
        "Montar a forma matricial A·x = b", "",
        latex=f"{sp.latex(a_matriz)} \\, {sp.latex(sp.Matrix(simbolos))} = {sp.latex(b_vetor)}",
    ))
    return a_matriz, b_vetor, simbolos, passos


# --------------------------------------------------------------------------
# Valores e Vetores Próprios
# --------------------------------------------------------------------------

def eigen(a: sp.Matrix) -> tuple[list, list, list[Passo]]:
    if a.shape[0] != a.shape[1]:
        raise ValueError("Valores/vetores próprios só estão definidos para matrizes quadradas.")
    n = a.shape[0]
    lam = sp.Symbol("lambda")
    matriz_caracteristica = a - lam * sp.eye(n)
    polinomio = sp.expand(matriz_caracteristica.det())

    eigenvects = a.eigenvects()
    valores, vetores = [], []
    for valor, multiplicidade, vecs in eigenvects:
        for v in vecs:
            valores.append(valor)
            vetores.append(v)

    passos = [
        Passo("Montar a matriz característica A − λI", "",
              latex=f"A - \\lambda I = {sp.latex(matriz_caracteristica)}"),
        Passo("Calcular o determinante (polinómio característico)",
              "det(A − λI) = 0 dá os valores próprios λ.",
              latex=f"\\det(A - \\lambda I) = {sp.latex(polinomio)} = 0"),
    ]
    fatorado = sp.factor(polinomio)
    if fatorado != polinomio:
        passos.append(Passo("Fatorizar o polinómio característico", "",
                             latex=f"{sp.latex(fatorado)} = 0"))
    passos.append(Passo(
        "Resolver a equação característica para λ", "",
        latex="\\lambda \\in \\{" + ", ".join(sp.latex(v) for v, _, _ in eigenvects) + "\\}",
    ))
    for valor, multiplicidade, vecs in eigenvects:
        matriz_substituida = a - valor * sp.eye(n)
        rotulo_mult = f" \\ (\\text{{multiplicidade }} {multiplicidade})" if multiplicidade > 1 else ""
        passos.append(Passo(
            f"Para λ = {sp.latex(valor)}: resolver (A − λI)v = 0",
            "Substituir este valor de λ e resolver o sistema homogéneo para encontrar v.",
            latex=(f"{sp.latex(matriz_substituida)} \\, v = 0 \\ \\Rightarrow \\ "
                   f"v = {sp.latex(vecs[0])}{rotulo_mult}"),
        ))
        v0 = vecs[0]
        passos.append(Passo(
            f"Verificar: A·v deve dar λ·v (λ = {sp.latex(valor)})", "",
            latex=f"A \\, v = {sp.latex(a * v0)} \\ , \\quad \\lambda v = {sp.latex(valor * v0)}",
        ))
    return valores, vetores, passos


def diagonalizar(a: sp.Matrix) -> tuple[Optional[tuple[sp.Matrix, sp.Matrix]], list[Passo]]:
    try:
        p, d = a.diagonalize()
        verificacao = sp.simplify(p * d * p.inv() - a)
        passos = [
            Passo("Formar P (vetores próprios nas colunas) e D (valores próprios na diagonal)",
                  "A é diagonalizável porque tem vetores próprios suficientes para preencher P.",
                  latex=f"P = {sp.latex(p)}, \\quad D = {sp.latex(d)}"),
            Passo("Verificar que A = P·D·P⁻¹",
                  "A diferença entre P·D·P⁻¹ e A deve dar a matriz nula.",
                  latex=f"P \\, D \\, P^{{-1}} - A = {sp.latex(verificacao)}"),
        ]
        return (p, d), passos
    except Exception:
        passos = [Passo("Tentar diagonalizar", "A matriz não é diagonalizável "
                                                "(não tem vetores próprios suficientes).")]
        return None, passos
