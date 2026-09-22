"""Módulo Conteúdo: e-book por tópico (teoria + exemplo resolvido + figura).

O texto teórico vive em `app/content/*.md`, separado do código, para poder
ser editado pelo grupo sem tocar em Python. O exemplo resolvido e a figura
reutilizam sempre as mesmas funções de `simbolico.py`/`visualizacao.py` já
usadas nos módulos de cálculo — zero lógica nova.
"""
from __future__ import annotations  # permite anotações de tipo mais modernas em versões antigas do Python

from pathlib import Path  # manipulação de caminhos de ficheiros/pastas

import numpy as np  # arrays numéricos para os exemplos fixos de cada tópico
import sympy as sp  # cálculo simbólico e conversão para LaTeX
import streamlit as st  # widgets de interface

from utils import simbolico  # funções de cálculo partilhadas com os módulos matemáticos
from utils.componentes import cabecalho, mostrar_passos  # título da página + lista de passos pedagógicos
from utils.visualizacao import figura_retas_2d, figura_transformacao_parametrizada, figura_vetores_2d  # gráficos Plotly reutilizados

# pasta onde vivem os ficheiros de teoria em Markdown (app/content/*.md)
PASTA_CONTEUDO = Path(__file__).resolve().parent.parent / "content"

# nome apresentado ao utilizador -> nome do ficheiro .md correspondente (sem extensão)
TOPICOS = {
    "Matrizes": "matrizes",
    "Determinantes e Matriz Inversa": "determinantes",
    "Sistemas Lineares": "sistemas",
    "Vetores": "vetores",
    "Valores e Vetores Próprios": "valores_proprios",
}


def _exemplo_matrizes() -> None:
    # duas matrizes fixas (A e a identidade B) só para ilustrar a soma passo a passo
    a = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([[1.0, 0.0], [0.0, 1.0]])
    resultado, passos = simbolico.somar_matrizes(simbolico.para_sympy(a), simbolico.para_sympy(b))
    st.latex(f"A + B = {sp.latex(resultado)}")  # mostra a soma em notação matemática
    mostrar_passos(passos)  # explica como se chega ao resultado, passo a passo
    # gráfico animado: mostra k·A a variar entre k=-2 e k=2 (20 fotogramas)
    fig = figura_transformacao_parametrizada(lambda k: k * a, np.linspace(-2, 2, 20), rotulo_parametro="k")
    st.plotly_chart(fig, width="stretch")


def _exemplo_determinantes() -> None:
    a = np.array([[2.0, 1.0], [1.0, 3.0]])  # matriz fixa de exemplo
    det_sp, passos = simbolico.determinante(simbolico.para_sympy(a))
    st.latex(f"\\det(A) = {sp.latex(det_sp)}")  # valor do determinante
    mostrar_passos(passos)
    # anima a entrada (1,1) da matriz entre -3 e 3, mostrando a área do paralelogramo a variar
    fig = figura_transformacao_parametrizada(
        lambda x: simbolico.matriz_com_entrada_variavel(a, (1, 1), x),
        np.linspace(-3, 3, 20), mostrar_area=True,
    )
    st.plotly_chart(fig, width="stretch")


def _exemplo_sistemas() -> None:
    # sistema fixo de 2 equações e 2 incógnitas: x+y=3, x-y=1
    a = np.array([[1.0, 1.0], [1.0, -1.0]])
    b = np.array([3.0, 1.0])
    simbolos = list(sp.symbols(f"x1:{a.shape[1] + 1}"))  # gera os símbolos x1, x2, ...
    solucoes, passos = simbolico.resolver_sistema(
        simbolico.para_sympy(a), simbolico.para_sympy(b.reshape(-1, 1)), simbolos
    )
    solucao_latex = simbolico.formatar_solucao_sistema(solucoes, simbolos)
    if solucao_latex is not None:
        st.latex(solucao_latex)  # mostra "x = ..., y = ..." só quando há solução para formatar
    mostrar_passos(passos)
    # desenha as duas retas do sistema e a sua interseção
    fig = figura_retas_2d([(a[0, 0], a[0, 1], b[0]), (a[1, 0], a[1, 1], b[1])])
    st.plotly_chart(fig, width="stretch")


def _exemplo_vetores() -> None:
    v, w = np.array([2.0, 1.0]), np.array([1.0, 2.0])  # dois vetores fixos de exemplo
    st.write(f"v · w = {float(np.dot(v, w)):g}")  # produto interno (escalar) entre v e w
    # desenha os dois vetores no plano, cada um com a sua cor
    fig = figura_vetores_2d([("v", v, "#e15759"), ("w", w, "#4e79a7")])
    st.plotly_chart(fig, width="stretch")


def _exemplo_valores_proprios() -> None:
    a = np.array([[2.0, 0.0], [0.0, 3.0]])  # matriz diagonal fixa (valores próprios óbvios: 2 e 3)
    valores, _vetores, passos = simbolico.eigen(simbolico.para_sympy(a))  # vetores próprios não usados aqui, só os valores
    st.write("Valores próprios: " + ", ".join(sp.latex(v) for v in valores))
    mostrar_passos(passos)
    # anima a transformação a "construir-se" gradualmente: de identidade (t=0) até A completa (t=1)
    fig = figura_transformacao_parametrizada(lambda t: (1 - t) * np.eye(2) + t * a, np.linspace(0, 1, 20))
    st.plotly_chart(fig, width="stretch")


# liga cada slug de tópico à função que desenha o respetivo exemplo resolvido
EXEMPLOS = {
    "matrizes": _exemplo_matrizes,
    "determinantes": _exemplo_determinantes,
    "sistemas": _exemplo_sistemas,
    "vetores": _exemplo_vetores,
    "valores_proprios": _exemplo_valores_proprios,
}


def render() -> None:
    cabecalho("📖 Conteúdo")
    nome_topico = st.selectbox("Tópico", list(TOPICOS.keys()))  # menu para escolher o tópico a consultar
    slug = TOPICOS[nome_topico]

    # lê o ficheiro Markdown de teoria correspondente a este tópico
    texto = (PASTA_CONTEUDO / f"{slug}.md").read_text(encoding="utf-8")
    marcador = f"<!-- exemplo:{slug} -->"
    # separa o texto em "antes do marcador" e "depois do marcador" — o exemplo
    # resolvido (código Python) é inserido no lugar exato do marcador
    antes, _separador, depois = texto.partition(marcador)

    st.divider()
    st.markdown(antes)  # parte teórica antes do exemplo (definição, propriedades, etc.)
    with st.container(border=True):
        st.markdown("##### 📝 Exemplo resolvido")
        EXEMPLOS[slug]()  # chama a função de exemplo correspondente a este tópico
    st.markdown(depois)  # parte teórica depois do exemplo (aplicações, "ver também", etc.)
