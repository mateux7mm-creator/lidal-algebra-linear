"""Launcher usado pelo executável PyInstaller: arranca o servidor Streamlit local.

Sem --server.headless=true: mantém-se o comportamento por omissão do
Streamlit de abrir automaticamente o browser predefinido — dá a experiência
de "duplo-clique e a app abre".
"""
import os
import sys

if getattr(sys, "frozen", False):
    # O PyInstaller extrai os pacotes para sys._MEIPASS/streamlit/..., sem o
    # segmento "site-packages" no caminho. O Streamlit usa esse segmento para
    # detetar se foi "instalado normalmente"; a ausência liga automaticamente
    # o global.developmentMode, que faz o servidor NÃO montar os ficheiros
    # estáticos do frontend (espera um dev-server Node em localhost:3000) —
    # e por isso "/" devolve 404 dentro do executável empacotado.
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")

from streamlit.web import cli as stcli


def _skip_onboarding_prompt() -> None:
    """Evita o prompt "Welcome to Streamlit! Email:" na primeira execução,
    que bloqueia para sempre num .exe sem terminal interativo."""
    config_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
    credentials_path = os.path.join(config_dir, "credentials.toml")
    if not os.path.exists(credentials_path):
        os.makedirs(config_dir, exist_ok=True)
        with open(credentials_path, "w", encoding="utf-8") as f:
            f.write("[general]\nemail = \"\"\n")


def main() -> None:
    _skip_onboarding_prompt()
    if getattr(sys, "frozen", False):
        # Executável PyInstaller: --add-data "app;app" coloca a pasta app/ na raiz
        # do bundle extraído (sys._MEIPASS), não um nível acima deste ficheiro.
        base_dir = sys._MEIPASS  # type: ignore[attr-defined]
        app_path = os.path.join(base_dir, "app", "streamlit_app.py")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, "..", "app", "streamlit_app.py")
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
