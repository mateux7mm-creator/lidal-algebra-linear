"""Launcher usado pelo executável PyInstaller: arranca o servidor Streamlit local.

Sem --server.headless=true: mantém-se o comportamento por omissão do
Streamlit de abrir automaticamente o browser predefinido — dá a experiência
de "duplo-clique e a app abre".
"""
import os
import sys

from streamlit.web import cli as stcli


def main() -> None:
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "streamlit_app.py")
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
