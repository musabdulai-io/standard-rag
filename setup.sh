#!/usr/bin/env bash
#
# setup.sh - Local development setup script
#   - Copies .env.example to .env
#   - Sets up Python venv with dependencies (using uv)
#   - Installs Node.js dependencies
#
# Usage:
#   ./setup.sh
#

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD}       Standard RAG - Development Setup               ${NC}"
echo -e "${BOLD}======================================================${NC}"

# Check requirements
check_requirements() {
  echo -e "\n${BOLD}Checking requirements...${NC}"
  local missing=0

  for cmd in npm docker; do
    if ! command -v "$cmd" &>/dev/null; then
      echo -e "${RED}✗ $cmd is not installed${NC}"
      missing=1
    else
      echo -e "${GREEN}✓ $cmd${NC}"
    fi
  done

  # Check for uv (preferred) or python3
  if command -v uv &>/dev/null; then
    echo -e "${GREEN}✓ uv${NC}"
    USE_UV=true
  elif command -v python3 &>/dev/null; then
    echo -e "${YELLOW}✓ python3 (uv recommended for faster setup)${NC}"
    USE_UV=false
  else
    echo -e "${RED}✗ Neither uv nor python3 found${NC}"
    missing=1
  fi

  if [ $missing -eq 1 ]; then
    echo -e "\n${RED}Please install missing tools:${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
      echo -e "  brew install node uv"
      echo -e "  Install Docker Desktop from https://docker.com"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
      echo -e "  sudo apt install nodejs npm docker.io"
      echo -e "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
    exit 1
  fi

  echo -e "${GREEN}All requirements satisfied.${NC}"
}

# Setup environment file
setup_env() {
  echo -e "\n${BOLD}Setting up environment...${NC}"
  if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
    echo -e "${GREEN}Created .env from .env.example${NC}"
  else
    echo -e "${YELLOW}.env already exists, skipping...${NC}"
  fi
}

# Setup backend with uv or fallback to python3
setup_backend() {
  echo -e "\n${BOLD}Setting up backend...${NC}"
  cd "$BACKEND_DIR"

  if [ "$USE_UV" = true ]; then
    # Use uv (faster, more reliable)
    if [ ! -d "venv" ]; then
      echo "Creating Python virtual environment with uv..."
      uv venv venv
    fi
    echo "Installing Python dependencies..."
    uv pip install --python venv/bin/python -r requirements.txt
  else
    # Fallback to standard python3 venv
    if [ ! -d "venv" ]; then
      echo "Creating Python virtual environment..."
      python3 -m venv venv --without-pip
      # Install pip manually to avoid ensurepip issues
      curl -sS https://bootstrap.pypa.io/get-pip.py | venv/bin/python
    fi
    echo "Installing Python dependencies..."
    venv/bin/pip install --upgrade pip -q
    venv/bin/pip install -r requirements.txt -q
  fi

  cd "$PROJECT_ROOT"
  echo -e "${GREEN}✓ Backend setup complete${NC}"
}

# Setup frontend
setup_frontend() {
  echo -e "\n${BOLD}Setting up frontend...${NC}"
  cd "$FRONTEND_DIR"

  if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
  else
    echo -e "${YELLOW}node_modules exists, running npm install anyway...${NC}"
    npm install
  fi

  cd "$PROJECT_ROOT"
  echo -e "${GREEN}✓ Frontend setup complete${NC}"
}

# Main
main() {
  check_requirements
  setup_env
  setup_backend
  setup_frontend

  echo -e "\n${GREEN}======================================================${NC}"
  echo -e "${GREEN}Setup complete!${NC}"
  echo -e "${GREEN}======================================================${NC}"
  echo -e "\n${YELLOW}Next steps:${NC}"
  echo -e "1. Update ${BOLD}.env${NC} with your ${BOLD}OPENAI_API_KEY${NC} and ${BOLD}PINECONE_API_KEY${NC}"
  echo -e "2. Run ${BOLD}docker compose up${NC} to start the development environment"
  echo -e "\n${BOLD}URLs:${NC}"
  echo -e "  Backend:  http://localhost:8000"
  echo -e "  Frontend: http://localhost:3000"
}

main "$@"
