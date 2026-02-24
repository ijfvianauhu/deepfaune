#!/bin/bash

DOCKER_IMAGE_NAME="deepfaune"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

# Verificar que el .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: No se encontró el fichero .env en $SCRIPT_DIR"
    exit 1
fi

# Cargar variables del .env
set -a
source "$ENV_FILE"
set +a

# USERID / GROUPID: si no están definidas o están vacías, usar las del usuario actual
if [ -z "${USERID:-}" ]; then
    USERID="$(id -u)"
fi

if [ -z "${GROUPID:-}" ]; then
    GROUPID="$(id -g)"
fi

VERSION="${VERSION:-v1.4.1}"
REPO="${REPO:-https://plmlab.math.cnrs.fr/deepfaune/software.git}"
CUDA="${CUDA:-0}"

usage() {
    echo "Uso: $0 build [--no-cache] | run | shell | destroy"
    exit 1
}

build_image() {
    cd "$SCRIPT_DIR" || exit 1

    REPO_DIR=$(basename "$REPO" .git)

    if [ ! -d "$REPO_DIR" ]; then
        git clone --branch "$VERSION" --single-branch "$REPO"
    else
        echo "Repositorio ya existe, se omite clonación"
    fi

    # Detectar opción --no-cache (compose build lo soporta)
    NO_CACHE_FLAG=""
    if [ "$2" == "--no-cache" ]; then
        echo "⚠️  Construcción sin cache activada"
        NO_CACHE_FLAG="--no-cache"
    fi

    # Selección CPU / CUDA (igual que en run/shell)
    if [ "$CUDA" = "1" ]; then
        PROFILE="gpu"
        SERVICE="deepfaune-gpu"
        echo "🔨 Construyendo imagen (compose) para $SERVICE (profile: $PROFILE)"
    else
        PROFILE="cpu"
        SERVICE="deepfaune-cpu"
        echo "🔨 Construyendo imagen (compose) para $SERVICE (profile: $PROFILE)"
    fi

    docker compose --profile "$PROFILE" build $NO_CACHE_FLAG "$SERVICE"
}

run_container() {
    cd "$SCRIPT_DIR" || exit 1

    if [ "$CUDA" = "1" ]; then
        PROFILE="gpu"
        SERVICE="deepfaune-gpu"
    else
        PROFILE="cpu"
        SERVICE="deepfaune-cpu"
    fi

    echo "🚀 Ejecutando servicio $SERVICE (profile: $PROFILE)"
    xhost +local:docker
    docker compose --profile "$PROFILE" up --build "$SERVICE"
}

shell_container() {
    cd "$SCRIPT_DIR" || exit 1

    if [ "$CUDA" = "1" ]; then
        PROFILE="gpu"
        SERVICE="deepfaune-gpu"
    else
        PROFILE="cpu"
        SERVICE="deepfaune-cpu"
    fi

    echo "🐚 Abriendo shell en $SERVICE (profile: $PROFILE)"

    docker compose --profile "$PROFILE" run --rm "$SERVICE" /bin/bash
}

destroy_stack() {
    cd "$SCRIPT_DIR" || exit 1

    if [ "$CUDA" = "1" ]; then
        PROFILE="gpu"
    else
        PROFILE="cpu"
    fi

    echo "💣 Eliminando stack (profile: $PROFILE)"

    docker compose --profile "$PROFILE" down --rmi local --volumes
}

# Comprobar argumento
case "$1" in
    build)
        build_image "$@"
        ;;
    run)
        run_container
        ;;
    shell)
        shell_container
        ;;
    destroy)
        destroy_stack
        ;;
    *)
        usage
        ;;
esac
