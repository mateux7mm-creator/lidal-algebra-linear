"""Wrappers SymPy para as operações de Álgebra Linear do laboratório.

Cada função de cálculo devolve sempre o par (resultado, passos), onde `passos`
é uma lista de `Passo` — o contrato comum usado por todos os módulos para
implementar o modo pedagógico "passo-a-passo" sem duplicar lógica de
apresentação.
"""
from __future__ import annotations  # permite usar tipos como "sp.Matrix" em anotações sem SymPy já estar totalmente carregado

from dataclasses import dataclass  # decorador que gera __init__/__repr__ automaticamente para a classe Passo
from typing import Optional  # anota parâmetros/retornos que podem ser None

import numpy as np  # cálculo numérico: os módulos da interface trabalham com arrays NumPy
import sympy as sp  # cálculo simbólico: motor de todas as operações de Álgebra Linear exatas (frações, não vírgula flutuante)
from sympy.parsing.sympy_parser import (  # utilitários para transformar texto livre (ex. "2x+4y") em expressões SymPy
    convert_xor,  # interpreta "^" como potência (em vez de XOR bit a bit, o significado por omissão em Python)
    implicit_multiplication_application,  # permite escrever "2x" em vez de "2*x"
    parse_expr,  # função que efetivamente converte uma string numa expressão SymPy
    standard_transformations,  # conjunto de transformações-base do parser (tokenização, etc.)
)

# combinação das transformações-base com as duas extras acima — usada em todo o parsing de equações do utilizador
_TRANSFORMACOES = standard_transformations + (implicit_multiplication_application, convert_xor)


@dataclass
class Passo:
    """Um passo do modo pedagógico passo-a-passo."""

    titulo: str  # título curto mostrado no cabeçalho do expander (ex. "Calcular c_11 = a_11 + b_11")
    detalhe: str = ""  # explicação textual opcional, mostrada por baixo do título
    latex: Optional[str] = None  # fórmula LaTeX opcional, renderizada com st.latex()


def para_sympy(m: np.ndarray) -> sp.Matrix:
    """Converte um array NumPy (matriz ou vetor) numa Matrix SymPy racional."""
    # sp.nsimplify troca floats (ex. 0.3333) por fracções exatas (ex. 1/3), para o cálculo simbólico não arrastar erro de vírgula flutuante
    return sp.Matrix(m.tolist()).applyfunc(sp.nsimplify)


def para_numpy(m: sp.Matrix) -> np.ndarray:
    """Converte uma Matrix SymPy num array NumPy de floats."""
    # .evalf() força a avaliação numérica (ex. 1/3 -> 0.333...) antes de passar para NumPy, que não entende fracções simbólicas
    return np.array(m.evalf().tolist(), dtype=float)


# --------------------------------------------------------------------------
# Matrizes
# --------------------------------------------------------------------------

def somar_matrizes(a: sp.Matrix, b: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    # a soma só é possível entre matrizes com exatamente a mesma forma (nº de linhas e colunas)
    if a.shape != b.shape:
        raise ValueError(f"Dimensões incompatíveis para soma: {a.shape} vs {b.shape}")
    resultado = a + b  # soma matricial nativa do SymPy: soma entrada a entrada
    n_linhas, n_colunas = a.shape
    # primeiro passo pedagógico: confirmar que a operação é válida antes de a mostrar
    passos = [
        Passo("Verificar dimensões", f"A e B são ambas {n_linhas}×{n_colunas} — a soma é possível."),
    ]
    # um passo por cada entrada da matriz resultado, mostrando a_ij + b_ij = c_ij em LaTeX
    for i in range(n_linhas):
        for j in range(n_colunas):
            passos.append(Passo(
                f"Calcular c_{i + 1}{j + 1} = a_{i + 1}{j + 1} + b_{i + 1}{j + 1}", "",
                latex=f"{sp.latex(a[i, j])} + {sp.latex(b[i, j])} = {sp.latex(resultado[i, j])}",
            ))
    # passo final: a matriz resultado completa
    passos.append(Passo("Matriz soma obtida", "", latex=f"A + B = {sp.latex(resultado)}"))
    return resultado, passos


def multiplicar_escalar(k: float, a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    k = sp.nsimplify(k)  # converte o escalar (float vindo do widget Streamlit) para uma forma simbólica exata
    resultado = k * a  # cada entrada de A multiplicada por k
    n_linhas, n_colunas = a.shape
    passos = []
    # um passo por entrada, mostrando k·a_ij = resultado_ij
    for i in range(n_linhas):
        for j in range(n_colunas):
            passos.append(Passo(
                f"Calcular a entrada ({i + 1}, {j + 1}) de k·A", "",
                latex=f"{sp.latex(k)} \\cdot {sp.latex(a[i, j])} = {sp.latex(resultado[i, j])}",
            ))
    # passo final com a matriz k·A completa
    passos.append(Passo("Matriz k·A obtida", "", latex=f"{sp.latex(k)} \\cdot A = {sp.latex(resultado)}"))
    return resultado, passos


def multiplicar_matrizes(a: sp.Matrix, b: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    # o produto A×B só é definido quando o nº de colunas de A == nº de linhas de B
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            f"Dimensões incompatíveis para produto: A é {a.shape}, B é {b.shape} "
            "(nº de colunas de A tem de ser igual ao nº de linhas de B)."
        )
    resultado = a * b  # produto matricial nativo do SymPy
    n_linhas, n_interno, n_colunas = a.shape[0], a.shape[1], b.shape[1]
    # passo inicial: justificar porque o produto é possível
    passos = [
        Passo("Verificar dimensões",
              f"A é {n_linhas}×{n_interno}, B é {n_interno}×{n_colunas} — "
              "colunas de A = linhas de B, o produto é possível."),
    ]
    # um passo por cada entrada c_ij, mostrando a soma dos produtos linha-de-A vezes coluna-de-B
    for i in range(n_linhas):
        for j in range(n_colunas):
            # constrói a string "(a_i1)(b_1j) + (a_i2)(b_2j) + ..." em LaTeX
            termos = " + ".join(f"({sp.latex(a[i, k])})({sp.latex(b[k, j])})" for k in range(n_interno))
            passos.append(Passo(
                f"Calcular c_{i + 1}{j + 1} (linha {i + 1} de A vezes coluna {j + 1} de B)", "",
                latex=f"{termos} = {sp.latex(resultado[i, j])}",
            ))
    # passo final com a matriz produto completa
    passos.append(Passo("Matriz produto obtida", "", latex=f"A \\times B = {sp.latex(resultado)}"))
    return resultado, passos


def transpor(a: sp.Matrix) -> tuple[sp.Matrix, list[Passo]]:
    resultado = a.T  # transposição nativa do SymPy: troca linhas por colunas
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
    m = a.copy()  # trabalha sobre uma cópia para nunca alterar a matriz original do chamador
    n_linhas, n_colunas = m.shape
    # se colunas_pivo não for dado, procura pivôs em todas as colunas de m
    limite = colunas_pivo if colunas_pivo is not None else n_colunas
    passos = [Passo("Matriz inicial", "", latex=sp.latex(m))]  # regista o ponto de partida
    linha_pivo = 0  # próxima linha disponível para receber um pivô
    for col in range(limite):
        if linha_pivo >= n_linhas:  # já não há mais linhas livres para pivotar
            break
        if m[linha_pivo, col] == 0:
            # procura, abaixo da linha atual, uma linha com entrada não-nula nesta coluna para trocar
            candidato = next((r for r in range(linha_pivo + 1, n_linhas) if m[r, col] != 0), None)
            if candidato is None:
                continue  # coluna toda a zeros abaixo do pivô: avança para a próxima coluna sem incrementar linha_pivo
            m.row_swap(linha_pivo, candidato)  # troca de linhas para trazer um pivô não-nulo
            passos.append(Passo(f"Trocar L{linha_pivo + 1} com L{candidato + 1}",
                                 "Para obter um pivô não-nulo nesta coluna.", latex=sp.latex(m)))
        pivo = m[linha_pivo, col]  # valor do pivô nesta coluna
        # anula todas as entradas abaixo do pivô, linha a linha
        for r in range(linha_pivo + 1, n_linhas):
            if m[r, col] != 0:
                fator = sp.nsimplify(m[r, col] / pivo)  # fator pelo qual a linha do pivô é multiplicada antes de subtrair
                m[r, :] = m[r, :] - fator * m[linha_pivo, :]  # operação elementar: L_r ← L_r − fator·L_pivo
                passos.append(Passo(
                    f"L{r + 1} ← L{r + 1} − ({sp.latex(fator)})·L{linha_pivo + 1}",
                    "Anular a entrada abaixo do pivô.", latex=sp.latex(m),
                ))
        linha_pivo += 1  # avança para a próxima linha disponível
    passos.append(Passo("Forma escalonada obtida", "", latex=sp.latex(m)))  # passo final com o resultado
    return m, passos


# --------------------------------------------------------------------------
# Determinantes e Inversa
# --------------------------------------------------------------------------

def determinante(a: sp.Matrix) -> tuple[sp.Expr, list[Passo]]:
    # o determinante só existe para matrizes quadradas
    if a.shape[0] != a.shape[1]:
        raise ValueError("O determinante só está definido para matrizes quadradas.")
    n = a.shape[0]
    valor = a.det()  # cálculo do determinante pelo SymPy (usado como valor de referência, independente do método didático mostrado abaixo)
    passos = [Passo("Confirmar que a matriz é quadrada", f"A é {n}×{n}.")]

    if n == 1:
        # caso trivial: o determinante de uma matriz 1×1 é a própria entrada
        passos.append(Passo("Determinante de uma matriz 1×1", "",
                             latex=f"\\det(A) = {sp.latex(a[0, 0])}"))
    elif n == 2:
        # fórmula direta 2×2: a11·a22 − a12·a21
        a11, a12, a21, a22 = a[0, 0], a[0, 1], a[1, 0], a[1, 1]
        p1, p2 = a11 * a22, a12 * a21
        passos.append(Passo(
            "Aplicar a fórmula 2×2", "det(A) = a₁₁·a₂₂ − a₁₂·a₂₁",
            latex=(f"({sp.latex(a11)})({sp.latex(a22)}) - ({sp.latex(a12)})({sp.latex(a21)}) "
                   f"= {sp.latex(p1)} - {sp.latex(p2)} = {sp.latex(valor)}"),
        ))
    elif n == 3:
        # regra de Sarrus: soma das 3 diagonais "descendentes" menos a soma das 3 "ascendentes"
        m = a
        # cada tuplo é uma diagonal descendente (incluindo as que "dão a volta" pelas bordas da matriz)
        termos_pos = [
            (m[0, 0], m[1, 1], m[2, 2]),
            (m[0, 1], m[1, 2], m[2, 0]),
            (m[0, 2], m[1, 0], m[2, 1]),
        ]
        # cada tuplo é uma diagonal ascendente
        termos_neg = [
            (m[0, 2], m[1, 1], m[2, 0]),
            (m[0, 0], m[1, 2], m[2, 1]),
            (m[0, 1], m[1, 0], m[2, 2]),
        ]
        produtos_pos = [x * y * z for x, y, z in termos_pos]  # produto de cada diagonal descendente
        produtos_neg = [x * y * z for x, y, z in termos_neg]  # produto de cada diagonal ascendente
        soma_pos, soma_neg = sum(produtos_pos), sum(produtos_neg)

        def fmt(termos, produtos):
            # formata uma lista de diagonais e os respetivos produtos como uma string LaTeX "(a)(b)(c) + ... = p1 + p2 + ..."
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
        # n >= 4: expansão de Laplace (cofatores) ao longo da 1ª linha, o único método que generaliza para qualquer ordem
        parcelas = []
        for j in range(n):
            menor = a.minor_submatrix(0, j)  # matriz menor: remove a linha 0 e a coluna j
            sinal = (-1) ** j  # sinal alternado do cofator, começando em + na coluna 0
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
    # a inversa só existe para matrizes quadradas
    if a.shape[0] != a.shape[1]:
        raise ValueError("A inversa só está definida para matrizes quadradas.")
    n = a.shape[0]
    det_a = a.det()
    passos: list[Passo] = []
    if det_a == 0:
        # matriz singular: não tem inversa, termina aqui devolvendo None
        passos.append(Passo("Verificar singularidade",
                             "det(A) = 0 → a matriz não é invertível (é singular)."))
        return None, passos

    if n == 2:
        # caso 2×2: a adjugada troca a diagonal principal e nega a secundária (atalho, mais rápido que cofatores genéricos)
        a11, a12, a21, a22 = a[0, 0], a[0, 1], a[1, 0], a[1, 1]
        adjugada = sp.Matrix([[a22, -a12], [-a21, a11]])
        passos.append(Passo(
            "Formar a adjugada (caso 2×2: trocar a diagonal principal e negar a secundária)", "",
            latex=f"adj(A) = {sp.latex(adjugada)}",
        ))
    else:
        # caso geral (n >= 3): calcula a matriz de cofatores e transpõe-na para obter a adjugada
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

    resultado = adjugada / det_a  # fórmula geral da inversa: A⁻¹ = (1/det A)·adj(A)
    passos.append(Passo(
        "Dividir a adjugada pelo determinante", "A⁻¹ = (1/det(A))·adj(A).",
        latex=f"A^{{-1}} = \\frac{{1}}{{{sp.latex(det_a)}}} {sp.latex(adjugada)} = {sp.latex(resultado)}",
    ))
    # passo de verificação pedagógica: confirma que A·A⁻¹ dá mesmo a identidade
    verificacao = sp.simplify(a * resultado)
    passos.append(Passo(
        "Verificar: A · A⁻¹ deve dar a matriz identidade", "",
        latex=f"A \\, A^{{-1}} = {sp.latex(verificacao)}",
    ))
    return resultado, passos


def matriz_com_entrada_variavel(a: np.ndarray, posicao: tuple[int, int], valor: float) -> np.ndarray:
    """Devolve uma cópia de `a` com a entrada em `posicao` substituída por `valor`."""
    b = a.astype(float).copy()  # cópia independente, para não alterar a matriz original passada pelo chamador
    b[posicao] = valor  # substitui só a entrada pedida (usado para animar "o que acontece se esta célula variar")
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
        # gera símbolos genéricos x1, x2, ..., x_n_vars quando o chamador não fornece nomes próprios
        simbolos = list(sp.symbols(f"x1:{n_vars + 1}"))
    # resolução simbólica do sistema A·x = b: devolve um FiniteSet de tuplos-solução (0, 1 ou infinitas soluções paramétricas)
    solucoes = sp.linsolve((a, b), simbolos)

    aumentada = a.row_join(b)  # matriz aumentada [A | b], usada só para mostrar o escalonamento pedagógico
    # calcula a forma escalonada da aumentada, limitando os pivôs às colunas de A (nunca a coluna de b)
    _, passos_escalonamento = escalonar(aumentada, colunas_pivo=n_vars)
    passos = [
        Passo("Montar a matriz aumentada [A | b]",
              "Cada linha de A·x = b passa a ser uma linha desta matriz, com b na última coluna.",
              latex=f"[A \\mid b] = {sp.latex(aumentada)}"),
    ]
    # passos_escalonamento[0] repete a matriz inicial, já mostrada no passo acima
    passos += passos_escalonamento[1:]

    if len(solucoes) == 0:
        # sistema impossível: nenhuma solução satisfaz todas as equações
        passos.append(Passo(
            "Interpretar a forma escalonada",
            "Uma linha do tipo 0 = c (com c ≠ 0) mostra que o sistema é impossível (sem solução).",
        ))
    else:
        classificacao = classificar_sistema(solucoes, simbolos)
        if classificacao == "indeterminado":
            # há variável(is) livre(s): infinitas soluções
            passos.append(Passo(
                "Interpretar a forma escalonada",
                "Há menos equações independentes do que incógnitas — pelo menos uma "
                "variável fica livre (sem pivô próprio), dando infinitas soluções.",
            ))
        else:
            # cada incógnita tem pivô próprio: solução única
            passos.append(Passo(
                "Interpretar a forma escalonada",
                "Cada incógnita tem uma linha com pivô próprio — a solução é única.",
            ))
        # último passo: a solução formatada como "x = ..., y = ..."
        passos.append(Passo("Solução", "", latex=formatar_solucao_sistema(solucoes, simbolos)))
    return solucoes, passos


def classificar_sistema(solucoes, simbolos: list[sp.Symbol]) -> str:
    """Classifica o sistema a partir do resultado de `linsolve`: "determinado"
    (solução única), "indeterminado" (infinitas soluções, com parâmetro livre)
    ou "impossivel" (sem solução)."""
    if len(solucoes) == 0:
        return "impossivel"  # linsolve devolveu um conjunto vazio: sistema sem solução
    tupla = next(iter(solucoes))  # linsolve devolve um FiniteSet com um único tuplo-solução (mesmo quando paramétrico)
    livres: set[sp.Symbol] = set()
    # percorre cada componente da solução, acumulando quaisquer símbolos-incógnita que sobrevivam como "livres" (parâmetros)
    for expr in tupla:
        livres |= expr.free_symbols & set(simbolos)
    return "indeterminado" if livres else "determinado"  # se sobra algum símbolo livre, a solução é paramétrica (infinitas soluções)


def formatar_solucao_sistema(solucoes, simbolos: list[sp.Symbol]) -> Optional[str]:
    """Devolve a solução em LaTeX como "x = ..., y = ...", ou None se o
    sistema não tiver solução (impossível)."""
    if len(solucoes) == 0:
        return None
    tupla = next(iter(solucoes))  # único tuplo-solução devolvido pelo linsolve
    # emparelha cada símbolo com o respetivo valor/expressão e formata "símbolo = valor" em LaTeX
    partes = [f"{sp.latex(s)} = {sp.latex(v)}" for s, v in zip(simbolos, tupla)]
    return r",\ \ ".join(partes)  # junta todas as igualdades numa só linha, separadas por vírgula e espaço


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
    resultado = sp.symbols(variaveis_texto)  # cria os símbolos SymPy a partir do texto (ex. "x, y" -> (x, y))
    # sp.symbols devolve um único Symbol se só houver um nome, ou um tuplo se houver vários — normaliza sempre para lista
    simbolos = list(resultado) if isinstance(resultado, tuple) else [resultado]
    if not all(isinstance(s, sp.Symbol) for s in simbolos):
        raise ValueError(f"Não consegui interpretar as incógnitas \"{variaveis_texto}\".")
    mapa_simbolos = {s.name: s for s in simbolos}  # dicionário nome->símbolo, usado pelo parser para reconhecer as incógnitas no texto

    passos = [Passo("Definir as incógnitas", f"Variáveis: {', '.join(s.name for s in simbolos)}")]
    linhas_a, valores_b = [], []
    for i, texto in enumerate(textos_equacoes, start=1):
        texto = texto.strip()
        if not texto:
            raise ValueError(f"A equação {i} está vazia.")
        if "=" not in texto:
            raise ValueError(f"Equação {i} inválida: falta o sinal \"=\" (ex.: 2x + 4y = 6).")
        lado_esq, lado_dir = texto.split("=", 1)  # separa a equação em lado esquerdo e direito pelo primeiro "="
        try:
            # interpreta cada lado como expressão SymPy, usando as transformações que aceitam "2x" e "x^2"
            expr_esq = parse_expr(lado_esq, local_dict=mapa_simbolos, transformations=_TRANSFORMACOES)
            expr_dir = parse_expr(lado_dir, local_dict=mapa_simbolos, transformations=_TRANSFORMACOES)
        except (sp.SympifyError, SyntaxError, TypeError, AttributeError) as erro:
            # qualquer erro de parsing é convertido numa mensagem amigável (o utilizador nunca vê um traceback do SymPy)
            raise ValueError(f"Equação {i} não foi entendida: \"{texto}\".") from erro
        equacao = sp.Eq(expr_esq, expr_dir)  # representa a equação como uma igualdade simbólica
        try:
            # extrai os coeficientes lineares desta equação, na ordem dos símbolos — falha se a equação não for linear
            linha, valor = sp.linear_eq_to_matrix([equacao], simbolos)
        except (ValueError, NotImplementedError) as erro:
            raise ValueError(
                f"Equação {i} não é linear nas incógnitas definidas "
                f"({', '.join(s.name for s in simbolos)})."
            ) from erro
        linhas_a.append(linha.tolist()[0])  # guarda a linha de coeficientes desta equação
        valores_b.append(valor.tolist()[0][0])  # guarda o termo independente (lado direito) desta equação
        passos.append(Passo(f"Equação {i}", "", latex=sp.latex(equacao)))

    a_matriz = sp.Matrix(linhas_a)  # monta a matriz de coeficientes A juntando todas as linhas recolhidas
    b_vetor = sp.Matrix(valores_b)  # monta o vetor de termos independentes b
    passos.append(Passo(
        "Montar a forma matricial A·x = b", "",
        latex=f"{sp.latex(a_matriz)} \\, {sp.latex(sp.Matrix(simbolos))} = {sp.latex(b_vetor)}",
    ))
    return a_matriz, b_vetor, simbolos, passos


# --------------------------------------------------------------------------
# Valores e Vetores Próprios
# --------------------------------------------------------------------------

def eigen(a: sp.Matrix) -> tuple[list, list, list[Passo]]:
    # valores/vetores próprios só estão definidos para matrizes quadradas
    if a.shape[0] != a.shape[1]:
        raise ValueError("Valores/vetores próprios só estão definidos para matrizes quadradas.")
    n = a.shape[0]
    lam = sp.Symbol("lambda")  # símbolo λ usado na equação característica
    matriz_caracteristica = a - lam * sp.eye(n)  # A − λI, cujo determinante nulo define os valores próprios
    polinomio = sp.expand(matriz_caracteristica.det())  # polinómio característico, expandido para forma legível

    eigenvects = a.eigenvects()  # lista de (valor_próprio, multiplicidade, [vetores_próprios]) calculada pelo SymPy
    valores, vetores = [], []
    # achata a estrutura agrupada por multiplicidade numa lista plana valor<->vetor, uma entrada por vetor próprio encontrado
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
    fatorado = sp.factor(polinomio)  # tenta fatorizar o polinómio característico, para uma leitura mais fácil das raízes
    if fatorado != polinomio:
        # só mostra este passo extra quando a fatorização realmente simplifica a expressão
        passos.append(Passo("Fatorizar o polinómio característico", "",
                             latex=f"{sp.latex(fatorado)} = 0"))
    passos.append(Passo(
        "Resolver a equação característica para λ", "",
        latex="\\lambda \\in \\{" + ", ".join(sp.latex(v) for v, _, _ in eigenvects) + "\\}",
    ))
    # para cada valor próprio, mostra a resolução do sistema homogéneo (A−λI)v=0 e uma verificação Av=λv
    for valor, multiplicidade, vecs in eigenvects:
        matriz_substituida = a - valor * sp.eye(n)  # A − λI com λ já substituído pelo valor próprio concreto
        # anota a multiplicidade algébrica apenas quando for maior que 1 (caso contrário a anotação seria redundante)
        rotulo_mult = f" \\ (\\text{{multiplicidade }} {multiplicidade})" if multiplicidade > 1 else ""
        passos.append(Passo(
            f"Para λ = {sp.latex(valor)}: resolver (A − λI)v = 0",
            "Substituir este valor de λ e resolver o sistema homogéneo para encontrar v.",
            latex=(f"{sp.latex(matriz_substituida)} \\, v = 0 \\ \\Rightarrow \\ "
                   f"v = {sp.latex(vecs[0])}{rotulo_mult}"),
        ))
        v0 = vecs[0]  # primeiro vetor próprio associado a este valor próprio, usado na verificação abaixo
        # passo de verificação pedagógica: confirma que A·v e λ·v coincidem
        passos.append(Passo(
            f"Verificar: A·v deve dar λ·v (λ = {sp.latex(valor)})", "",
            latex=f"A \\, v = {sp.latex(a * v0)} \\ , \\quad \\lambda v = {sp.latex(valor * v0)}",
        ))
    return valores, vetores, passos


def diagonalizar(a: sp.Matrix) -> tuple[Optional[tuple[sp.Matrix, sp.Matrix]], list[Passo]]:
    try:
        # a.diagonalize() falha (lança exceção) se A não tiver vetores próprios suficientes para preencher P
        p, d = a.diagonalize()  # P: colunas = vetores próprios; D: diagonal = valores próprios correspondentes
        verificacao = sp.simplify(p * d * p.inv() - a)  # deve simplificar para a matriz nula se A = P·D·P⁻¹
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
        # matriz não diagonalizável (vetores próprios insuficientes): devolve None em vez de propagar a exceção do SymPy
        passos = [Passo("Tentar diagonalizar", "A matriz não é diagonalizável "
                                                "(não tem vetores próprios suficientes).")]
        return None, passos
