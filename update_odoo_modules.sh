#!/bin/bash

# Configuración
ODOO_CONF="/home/prin/odoo16/odoo.conf"
ODOO_PATH="/home/prin/odoo16/odoo"
DB_NAME="TU_BD"
ADDONS_PATH="/opt/odoo16/custom_addons"

# Lista de repositorios locales
REPOS=(
    "/mnt/c/Users/justi/OneDrive/Documentos/repositorios/ODOOFEEDBIODEV"
    "/mnt/c/Users/justi/OneDrive/Documentos/repositorios/feedbio_base"
)

# Función para hacer pull y copiar
update_repo() {
    local repo_path="$1"
    local repo_name
    repo_name=$(basename "$repo_path")

    if [ -d "$repo_path" ]; then
        echo "📥 Actualizando $repo_name..."
        cd "$repo_path" || exit
        git pull origin main

        echo "📂 Copiando $repo_name a $ADDONS_PATH..."
        cp -r "$repo_path" "$ADDONS_PATH/"
    else
        echo "⚠️ El repositorio $repo_name no existe en $repo_path"
    fi
}

# Si el usuario pasa argumentos, solo actualizamos esos módulos
if [ "$#" -gt 0 ]; then
    for arg in "$@"; do
        for repo in "${REPOS[@]}"; do
            if [[ "$(basename "$repo")" == "$arg" ]]; then
                update_repo "$repo"
            fi
        done
    done
else
    # Si no hay argumentos, actualizamos todos
    for repo in "${REPOS[@]}"; do
        update_repo "$repo"
    done
fi

# Actualizar en Odoo
if [ "$#" -gt 0 ]; then
    MODULES=$(IFS=,; echo "$*")
    echo "🚀 Actualizando módulos: $MODULES en Odoo..."
    cd "$ODOO_PATH" || exit
    ./odoo-bin -c "$ODOO_CONF" -d "$DB_NAME" -u "$MODULES" --dev=all
else
    echo "🚀 Actualizando TODOS los módulos..."
    cd "$ODOO_PATH" || exit
    ./odoo-bin -c "$ODOO_CONF" -d "$DB_NAME" -u all --dev=all
fi

echo "✅ Proceso finalizado."
