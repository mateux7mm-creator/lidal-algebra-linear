"""Widgets Streamlit partilhados por todos os módulos.

Centralizar aqui o input de matrizes/vetores e a apresentação de
resultados/passos garante que os 5 módulos matemáticos têm sempre o mesmo
aspeto e comportamento, e que uma melhoria futura (ex. à forma como os passos
são mostrados) só precisa de ser feita num sítio.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import sympy as sp
import streamlit as st

from utils.simbolico import Passo


def barra_menus(menus: dict[str, Callable[[], None]]) -> None:
    """Barra de menus estilo desktop (ex. Winplot): cada entrada é um rótulo
    de menu (ex. "Equações") associado a uma função que desenha o conteúdo do
    popover quando o utilizador o abre. Os itens dentro de cada popover são
    controlos Streamlit normais (botões, toggles) — o menu só organiza o
    acesso, a ação real fica na função de callback.

    Uso:
        barra_menus({
            "Equações": _menu_equacoes,
            "Ver": _menu_ver,
            "Exportar": _menu_exportar,
        })
    """
    colunas = st.columns(len(menus))
    for coluna, (rotulo, desenhar_conteudo) in zip(colunas, menus.items()):
        with coluna:
            with st.popover(f"{rotulo} ▾", width="stretch"):
                desenhar_conteudo()


def cabecalho(icone_titulo: str) -> None:
    """Título da página — só o título, sem legenda: uma vez dentro do
    módulo, a descrição já não acrescenta nada e só ocupa espaço.
    Uso: cabecalho("🔢 Matrizes")"""
    st.title(icone_titulo)


def matriz_input(chave: str, linhas: int = 2, colunas: int = 2, titulo: str = "Matriz",
                  valor_defeito: np.ndarray | None = None, permitir_redimensionar: bool = True,
                  quadrada: bool = False) -> np.ndarray:
    """Editor de células para uma matriz, com rótulos "1ª linha"/"1ª coluna",
    pré-visualização simbólica ao vivo, e (se `permitir_redimensionar`) botões
    para adicionar/remover linhas e colunas. Com `quadrada=True` (ex.
    Determinantes, Valores Próprios), um único par de botões "➕/➖ Dimensão"
    cresce/encolhe linhas e colunas em conjunto, mantendo a matriz quadrada.
    Devolve um numpy.ndarray."""
    chave_dados = f"{chave}_dados"
    chave_versao = f"{chave}_versao"
    if chave_dados not in st.session_state:
        if quadrada:
            linhas = colunas = max(linhas, colunas)
        if valor_defeito is None or valor_defeito.shape != (linhas, colunas):
            valor_defeito = np.eye(max(linhas, colunas))[:linhas, :colunas]
        st.session_state[chave_dados] = valor_defeito.astype(float)
        st.session_state[chave_versao] = 0

    dados = st.session_state[chave_dados]
    n_linhas, n_colunas = dados.shape

    with st.container(border=True):
        col_titulo, col_botoes = st.columns([2, 3])
        with col_titulo:
            st.markdown(f"**{titulo}** · {n_linhas}×{n_colunas}")
        if permitir_redimensionar and quadrada:
            with col_botoes:
                c1, c2 = st.columns(2)
                if c1.button("➕ Dimensão", key=f"{chave}_add_dim", width="stretch"):
                    nova = np.vstack([dados, np.zeros((1, n_colunas))])
                    nova = np.hstack([nova, np.zeros((n_linhas + 1, 1))])
                    st.session_state[chave_dados] = nova
                    st.session_state[chave_versao] += 1
                    st.rerun()
                if c2.button("➖ Dimensão", key=f"{chave}_rem_dim", width="stretch", disabled=n_linhas <= 1):
                    st.session_state[chave_dados] = dados[:-1, :-1]
                    st.session_state[chave_versao] += 1
                    st.rerun()
        elif permitir_redimensionar:
            with col_botoes:
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("➕ Linha", key=f"{chave}_add_l", width="stretch"):
                    st.session_state[chave_dados] = np.vstack([dados, np.zeros((1, n_colunas))])
                    st.session_state[chave_versao] += 1
                    st.rerun()
                if c2.button("➕ Coluna", key=f"{chave}_add_c", width="stretch"):
                    st.session_state[chave_dados] = np.hstack([dados, np.zeros((n_linhas, 1))])
                    st.session_state[chave_versao] += 1
                    st.rerun()
                if c3.button("➖ Linha", key=f"{chave}_rem_l", width="stretch", disabled=n_linhas <= 1):
                    st.session_state[chave_dados] = dados[:-1, :]
                    st.session_state[chave_versao] += 1
                    st.rerun()
                if c4.button("➖ Coluna", key=f"{chave}_rem_c", width="stretch", disabled=n_colunas <= 1):
                    st.session_state[chave_dados] = dados[:, :-1]
                    st.session_state[chave_versao] += 1
                    st.rerun()

        df = pd.DataFrame(
            dados,
            index=[f"{i + 1}ª linha" for i in range(n_linhas)],
            columns=[f"{i + 1}ª coluna" for i in range(n_colunas)],
        )
        chave_editor = f"{chave}_editor_{st.session_state[chave_versao]}"
        editado = st.data_editor(
            df,
            key=chave_editor,
            num_rows="fixed",
            column_config={c: st.column_config.NumberColumn(format="%.2f") for c in df.columns},
        )
        matriz = np.array(editado, dtype=float)
        st.session_state[chave_dados] = matriz

        st.caption("Forma simbólica")
        st.latex(sp.latex(sp.Matrix(np.round(matriz, 4).tolist())))
    return matriz


def vetor_input(chave: str, dimensao: int = 2, titulo: str = "Vetor",
                 valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para um vetor de `dimensao` componentes, com
    pré-visualização simbólica ao vivo (mesmo estilo de `matriz_input`)."""
    if valor_defeito is None or len(valor_defeito) != dimensao:
        valor_defeito = np.ones(dimensao)
    with st.container(border=True):
        st.markdown(f"**{titulo}** · {dimensao}D")
        df = pd.DataFrame([valor_defeito], columns=[f"{i + 1}ª coluna" for i in range(dimensao)])
        editado = st.data_editor(
            df,
            key=f"{chave}_{dimensao}d",
            num_rows="fixed",
            hide_index=True,
            column_config={c: st.column_config.NumberColumn(format="%.2f") for c in df.columns},
        )
        vetor = np.array(editado, dtype=float).reshape(-1)
        st.caption("Forma simbólica")
        st.latex(sp.latex(sp.Matrix(np.round(vetor, 4).tolist())))
    return vetor


def modo_passo_a_passo_ativo(chave_pagina: str) -> bool:
    """Toggle único, igual em todos os módulos, desligado por omissão."""
    return st.toggle("🔍 Mostrar modo passo-a-passo", value=False, key=f"{chave_pagina}_passo_a_passo")


def modo_leve_ativo() -> bool:
    """Cria o toggle de modo leve na sidebar. Chamar UMA ÚNICA VEZ, em streamlit_app.py
    (o widget fica disponível em todas as páginas porque o script de entrada corre sempre).
    Dentro de cada módulo, usar `modo_leve_da_sessao()` para ler o valor sem recriar o widget."""
    st.sidebar.markdown("### 🧮 Laboratório de Álgebra Linear")
    st.sidebar.caption("Mestrado em Ensino da Matemática")
    st.sidebar.divider()
    return st.sidebar.toggle(
        "🐢 Modo leve",
        value=False,
        key="modo_leve",
        help="Reduz a densidade das malhas e o número de frames das animações — "
             "para ligações ou dispositivos mais fracos.",
    )


def modo_leve_da_sessao() -> bool:
    """Lê o estado atual do modo leve, sem criar um novo widget."""
    return bool(st.session_state.get("modo_leve", False))


def mostrar_passos(passos: list[Passo]) -> None:
    """Renderização uniforme da lista de passos pedagógicos."""
    st.markdown("##### 🔍 Como se chega ao resultado")
    for i, passo in enumerate(passos, start=1):
        with st.expander(f"Passo {i}: {passo.titulo}", expanded=False):
            if passo.detalhe:
                st.write(passo.detalhe)
            if passo.latex:
                st.latex(passo.latex)


def _latex_numerico(numerico) -> str:
    """Formata um escalar/vetor/matriz numérico como bracket LaTeX arredondado,
    para o lado 'Numérico' ter o mesmo aspeto visual do lado 'Simbólico'."""
    arr = np.asarray(numerico, dtype=float)
    arredondado = np.round(arr, 3)
    if arredondado.ndim == 0:
        return f"{arredondado:g}"
    return sp.latex(sp.Matrix(arredondado.tolist())) if arredondado.ndim == 2 \
        else sp.latex(sp.Matrix(arredondado.reshape(1, -1).tolist()))


def mostrar_resultado(numerico, simbolico_latex: str) -> None:
    """Mostra o resultado numérico e simbólico lado a lado, sempre no mesmo layout
    (ambos como bracket LaTeX, para consistência visual)."""
    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        col_num, col_sym = st.columns(2)
        with col_num:
            st.caption("Numérico")
            st.latex(_latex_numerico(numerico))
        with col_sym:
            st.caption("Simbólico")
            st.latex(simbolico_latex)
