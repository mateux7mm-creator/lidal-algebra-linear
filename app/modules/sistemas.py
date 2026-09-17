"""Módulo Sistemas Lineares: resolução e interpretação geométrica."""
import numpy as np
import streamlit as st

from utils import simbolico
from utils.componentes import (
    cabecalho,
    matriz_input,
    modo_leve_da_sessao,
    modo_passo_a_passo_ativo,
    mostrar_passos,
    vetor_input,
)
from utils.visualizacao import figura_retas_2d, figura_sistema_2d_animado, n_frames


def render() -> None:
    cabecalho("📐 Sistemas Lineares", "Resolução e interpretação geométrica.")

    col_dim, col_toggle = st.columns([2, 1])
    with col_dim:
        n_variaveis = st.radio("Número de variáveis", [2, 3], horizontal=True)
    with col_toggle:
        mostrar_passo_a_passo = modo_passo_a_passo_ativo("sistemas")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        a = matriz_input("sistemas_A", linhas=n_variaveis, colunas=n_variaveis, titulo="Matriz de coeficientes A",
                          valor_defeito=np.array([[1.0, 1.0], [1.0, -1.0]]) if n_variaveis == 2
                          else np.array([[1.0, 1.0, 1.0], [1.0, -1.0, 2.0], [2.0, 1.0, -1.0]]))
    with col_b:
        b = vetor_input("sistemas_b", dimensao=n_variaveis, titulo="Termos independentes b",
                         valor_defeito=np.array([3.0, 1.0]) if n_variaveis == 2 else np.array([6.0, 5.0, 3.0]))

    a_sp = simbolico.para_sympy(a)
    b_sp = simbolico.para_sympy(b.reshape(-1, 1))
    solucoes, passos = simbolico.resolver_sistema(a_sp, b_sp)

    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        st.markdown(f"**Solução simbólica (SymPy):** {solucoes}")
        if n_variaveis == 2 and abs(np.linalg.det(a)) > 1e-9:
            solucao_numerica = np.linalg.solve(a, b)
            st.markdown(f"**Solução numérica (NumPy):** x = {solucao_numerica[0]:.4g}, "
                        f"y = {solucao_numerica[1]:.4g}")

    if mostrar_passo_a_passo:
        mostrar_passos(passos)

    if n_variaveis == 2:
        st.divider()
        st.markdown("##### 📈 Interpretação gráfica")
        equacoes = [(a[0, 0], a[0, 1], b[0]), (a[1, 0], a[1, 1], b[1])]
        st.plotly_chart(figura_retas_2d(equacoes), width="stretch")

        st.markdown("##### 🎬 Ver a reta e a interseção a variar em tempo real")
        coef_variavel = st.selectbox("Coeficiente da 2ª equação a variar", ["a21 (x)", "a22 (y)"], index=1)
        valores = np.linspace(-3, 3, n_frames(modo_leve_da_sessao()))
        if coef_variavel.startswith("a21"):
            calcular_eq = lambda p: (p, a[1, 1], b[1])
        else:
            calcular_eq = lambda p: (a[1, 0], p, b[1])
        fig_anim = figura_sistema_2d_animado(
            equacao_fixa=(a[0, 0], a[0, 1], b[0]),
            calcular_equacao_variavel=calcular_eq,
            valores_parametro=valores,
            modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig_anim, width="stretch")
    else:
        st.info("A visualização 3D da interseção de planos ficará disponível numa iteração seguinte "
                 "— a resolução simbólica acima já funciona para 3 variáveis.")
