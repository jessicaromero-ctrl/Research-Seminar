esc
#!/bin/bash
# Ejecuta los scripts de una semana, guarda sus salidas y publica en GitHub.
# Uso: ./scripts/publicar_semana.sh <carpeta_semana> "<mensaje del commit>"
set -euo pipefail

# Ubica la ejecución en la raíz del repositorio, sin importar desde dónde se llame
cd "$(dirname "$0")/.."

SEMANA="${1:-}"
MENSAJE="${2:-}"

if [ -z "$SEMANA" ] || [ -z "$MENSAJE" ]; then
echo "Uso: $0 <carpeta_semana> \"<mensaje del commit>\""
exit 1
fi

if [ ! -f "$SEMANA/README.md" ]; then
echo "Error: falta $SEMANA/README.md. Escribe la bitácora antes de publicar."
exit 1
fi

# Orden de ejecución: el diagnóstico lee el original, la corrección genera
# datos/sepsis/procesado/ y la verificación lee ese archivo procesado.
SCRIPTS=(
"scripts/fase1_diagnostico_casos.py"
"scripts/fase1_traza_sin_identificador.py"
"scripts/fase1_corregir_identificador.py"
"scripts/fase1_verificacion.py"
)

RESULTADOS="$SEMANA/resultados"
mkdir -p "$RESULTADOS"

for script in "${SCRIPTS[@]}"; do
nombre=$(basename "$script" .py)
echo "==> Ejecutando $script"
# Si Python falla, pipefail detiene el script y no se publica nada incompleto
python3 "$script" 2>&1 | tee "$RESULTADOS/$nombre.txt"
done

git add -- "$SEMANA" scripts datos/sepsis .gitignore

if git diff --cached --quiet; then
echo "No hay cambios nuevos que publicar."
exit 0
fi

git commit -m "$MENSAJE"
git pull --rebase origin main
git push
echo "Publicado: $(git log -1 --oneline)"
