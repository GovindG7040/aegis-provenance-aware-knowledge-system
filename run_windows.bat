@echo off
python -m app.cli ingest --data-dir data\aegis-dataset\aegis-dataset --out-dir artifacts
python -m app.cli evaluate --data-dir data\aegis-dataset\aegis-dataset --out-dir artifacts
python -m app.cli ask "What is the current normal operating pressure for the HPU?"
pause
