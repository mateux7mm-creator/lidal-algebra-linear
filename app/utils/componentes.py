"""Widgets Streamlit partilhados por todos os módulos.

Centralizar aqui o input de matrizes/vetores e a apresentação de
resultados/passos garante que os 5 módulos matemáticos têm sempre o mesmo
aspeto e comportamento, e que uma melhoria futura (ex. à forma como os passos
são mostrados) só precisa de ser feita num sítio.
"""
from __future__ import annotations

import numpy as np
import streamlit as st

from utils.simbolico import Passo


def matriz_input(chave: str, linhas: int = 2, colunas: int = 2, titulo: str = "Matriz",
                  valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para uma matriz linhas×colunas, devolvendo um numpy.ndarray."""
    st.markdown(f"**{titulo}** ({linhas}×{colunas})")
    if valor_defeito is None or valor_defeito.shape != (linhas, colunas):
        valor_defeito = np.eye(max(linhas, colunas))[:linhas, :colunas]
    editado = st.data_editor(
        valor_defeito,
        key=f"{chave}_{linhas}x{colunas}",
        num_rows="fixed",
        use_container_width=False,
    )
    return np.array(editado, dtype=float)


def vetor_input(chave: str, dimensao: int = 2, titulo: str = "Vetor",
                 valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para um vetor de `dimensao` componentes."""
    st.markdown(f"**{titulo}** ({dimensao}D)")
    if valor_defeito is None or len(valor_defeito) != dimensao:
        valor_defeito = np.ones(dimensao)
    editado = st.data_editor(
        valor_defeito.reshape(1, -1),
        key=f"{chave}_{dimensao}d",
        num_rows="fixed",
        use_container_width=False,
    )
    return np.array(editado, dtype=float).reshape(-1)


def modo_passo_a_passo_ativo(chave_pagina: str) -> bool:
    """Toggle único, igual em todos os módulos, ligado por omissão."""
    return st.toggle("Mostrar modo passo-a-passo", value=True, key=f"{chave_pagina}_passo_a_passo")


def modo_leve_ativo() -> bool:
    """Cria o toggle de modo leve na sidebar. Chamar UMA ÚNICA VEZ, em streamlit_app.py
    (o widget fica disponível em todas as páginas porque o script de entrada corre sempre).
    Dentro de cada módulo, usar `modo_leve_da_sessao()` para ler o valor sem recriar o widget."""
    return st.sidebar.toggle(
        "Modo leve (para ligações/dispositivos mais fracos)",
        value=False,
        key="modo_leve",
        help="Reduz a densidade das malhas e o número de frames das animações.",
    )


def modo_leve_da_sessao() -> bool:
    """Lê o estado atual do modo leve, sem criar um novo widget."""
    return bool(st.session_state.get("modo_leve", False))


def mostrar_passos(passos: list[Passo]) -> None:
    """Renderização uniforme da lista de passos pedagógicos."""
    for i, passo in enumerate(passos, start=1):
        with st.expander(f"Passo {i}: {passo.titulo}", expanded=True):
            if passo.detalhe:
                st.write(passo.detalhe)
            if passo.latex:
                st.latex(passo.latex)


def mostrar_resultado(numerico, simbolico_latex: str) -> None:
    """Mostra o resultado numérico e simbólico lado a lado, sempre no mesmo layout."""
    col_num, col_sym = st.columns(2)
    with col_num:
        st.markdown("**Resultado numérico**")
        st.write(numerico)
    with col_sym:
        st.markdown("**Resultado simbólico**")
        st.latex(simbolico_latex)
