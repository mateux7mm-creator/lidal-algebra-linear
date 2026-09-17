# Gera o executável desktop (Windows) a partir do mesmo código Streamlit.
# Requer bastante espaço temporário livre em disco (algumas centenas de MB).
# Uso: a partir da raiz do projeto, ./venv/Scripts/Activate.ps1 ; ./desktop/build_exe.ps1

pip install -r requirements-desktop.txt

pyinstaller --onefile --name LaboratorioAlgebraLinear `
  --add-data "app;app" `
  --add-data ".streamlit;.streamlit" `
  --collect-all streamlit `
  --collect-all pkg_resources `
  desktop/run_app.py

Write-Host "Executável gerado em dist/LaboratorioAlgebraLinear.exe"
