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
    passos = [
        Passo("Verificar dimensões", f"A e B são ambas {a.shape[0]}×{a.shape[1]} — a soma é possível."),
        Passo("Somar elemento a elemento", "Cada entrada de C = A + B é c_ij = a_ij + b_ij.",
              latex=f"{sp.latex(a)} + {sp.latex(b)} = {sp.latex(resultado)}"),
    ]
    return resultado, passos


def multiplicar_escalar(k: float, a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    k = sp.nsimplify(k)
    resultado = k * a
    passos = [
        Passo("Multiplicar cada entrada por k", "Cada entrada de k·A é k·a_ij.",
              latex=f"{sp.latex(k)} \\cdot {sp.latex(a)} = {sp.latex(resultado)}"),
    ]
    return resultado, passos


def multiplicar_matrizes(a: sp.Matrix, b: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            f"Dimensões incompatíveis para produto: A é {a.shape}, B é {b.shape} "
            "(nº de colunas de A tem de ser igual ao nº de linhas de B)."
        )
    resultado = a * b
    passos = [
        Passo("Verificar dimensões",
              f"A é {a.shape[0]}×{a.shape[1]}, B é {b.shape[0]}×{b.shape[1]} — "
              "colunas de A = linhas de B, o produto é possível."),
        Passo("Calcular cada entrada",
              "Cada entrada c_ij é o produto interno da linha i de A pela coluna j de B.",
              latex=f"{sp.latex(a)} \\times {sp.latex(b)} = {sp.latex(resultado)}"),
    ]
    return resultado, passos


def transpor(a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    resultado = a.T
    passos = [
        Passo("Trocar linhas por colunas", "A transposta troca a linha i com a coluna i.",
              latex=f"{sp.latex(a)}^T = {sp.latex(resultado)}"),
    ]
    return resultado, passos


def escalonar(a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    """Eliminação de Gauss até à forma escalonada (não reduzida), mostrando
    cada operação de linha — ao contrário de `.rref()`, que só devolve o
    resultado final."""
    m = a.copy()
    n_linhas, n_colunas = m.shape
    passos = [Passo("Matriz inicial", "", latex=sp.latex(m))]
    linha_pivo = 0
    for col in range(n_colunas):
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
    valor = a.det()
    metodo = "regra de Sarrus" if a.shape[0] in (2, 3) else "expansão de Laplace/eliminação"
    passos = [
        Passo("Confirmar que a matriz é quadrada", f"A é {a.shape[0]}×{a.shape[1]}."),
        Passo(f"Calcular o determinante ({metodo})", "", latex=f"\\det{sp.latex(a)} = {sp.latex(valor)}"),
    ]
    return valor, passos


def inversa(a: sp.Matrix) -> tuple[Optional[sp.Matrix], list[Passo]]:
    """Assume que det(a) já foi calculado e mostrado (ex. via `determinante()`)
    — não repete esse passo, só verifica singularidade e, se possível, inverte."""
    if a.shape[0] != a.shape[1]:
        raise ValueError("A inversa só está definida para matrizes quadradas.")
    det_a = a.det()
    passos: list[Passo] = []
    if det_a == 0:
        passos.append(Passo("Verificar singularidade",
                             "det(A) = 0 → a matriz não é invertível (é singular)."))
        return None, passos
    resultado = a.inv()
    passos.append(Passo("Calcular a inversa (Gauss-Jordan / matriz adjunta)",
                         "Como det(A) ≠ 0, a inversa existe.",
                         latex=f"A^{{-1}} = {sp.latex(resultado)}"))
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
    passos = [
        Passo("Montar o sistema", "Cada linha de A·x = b é uma equação linear.",
              latex=f"{sp.latex(a)} \\, {sp.latex(sp.Matrix(simbolos))} = {sp.latex(b)}"),
        Passo("Resolver (eliminação de Gauss / regra de Cramer)",
              "SymPy resolve o sistema de forma simbólica, cobrindo os casos "
              "de solução única, indeterminada ou impossível."),
    ]
    if len(solucoes) == 0:
        passos.append(Passo("Interpretar o resultado", "O sistema é impossível (sem solução)."))
    else:
        passos.append(Passo("Interpretar o resultado", f"Solução: {solucoes}"))
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
    eigenvects = a.eigenvects()
    valores = []
    vetores = []
    for valor, multiplicidade, vecs in eigenvects:
        for v in vecs:
            valores.append(valor)
            vetores.append(v)
    passos = [
        Passo("Montar a equação característica", "det(A - λI) = 0 dá os valores próprios λ.",
              latex=f"\\det({sp.latex(a)} - \\lambda I) = 0"),
        Passo("Resolver para λ", "", latex=f"\\lambda \\in \\{{{', '.join(sp.latex(v) for v in valores)}\\}}"),
        Passo("Calcular os vetores próprios", "Para cada λ, resolver (A - λI)v = 0."),
    ]
    return valores, vetores, passos


def diagonalizar(a: sp.Matrix) -> tuple[Optional[tuple[sp.Matrix, sp.Matrix]], list[Passo]]:
    try:
        p, d = a.diagonalize()
        passos = [
            Passo("Formar P (vetores próprios) e D (valores próprios)",
                  "A é diagonalizável: A = P·D·P⁻¹.",
                  latex=f"P = {sp.latex(p)}, \\quad D = {sp.latex(d)}"),
        ]
        return (p, d), passos
    except Exception:
        passos = [Passo("Tentar diagonalizar", "A matriz não é diagonalizável "
                                                "(não tem vetores próprios suficientes).")]
        return None, passos
