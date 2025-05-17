#!/bin/bash
set -e

# Development helper script for TIL project using uv

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}TIL Development Script (using uv)${NC}"
echo "=================================="

# Ensure we're in the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

case "${1:-help}" in
    init)
        echo -e "${YELLOW}Initializing project environment...${NC}"
        uv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
        echo -e "${YELLOW}Installing project dependencies...${NC}"
        uv sync
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        ;;
    
    install)
        echo -e "${YELLOW}Installing project dependencies...${NC}"
        uv sync --no-dev
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        ;;
    
    install-dev)
        echo -e "${YELLOW}Installing project with dev dependencies...${NC}"
        uv sync
        echo -e "${GREEN}✓ Dev dependencies installed${NC}"
        ;;
    
    format)
        echo -e "${YELLOW}Formatting code...${NC}"
        uv run ruff format til/ tests/
        echo -e "${GREEN}✓ Code formatted${NC}"
        ;;
    
    lint)
        echo -e "${YELLOW}Running linters...${NC}"
        uv run ruff check til/ tests/
        echo -e "${GREEN}✓ Linting complete${NC}"
        ;;
    
    fix)
        echo -e "${YELLOW}Fixing linting issues...${NC}"
        uv run ruff check --fix til/ tests/
        echo -e "${GREEN}✓ Linting issues fixed${NC}"
        ;;
    
    typecheck)
        echo -e "${YELLOW}Running type checker...${NC}"
        uv run mypy til/
        echo -e "${GREEN}✓ Type checking complete${NC}"
        ;;
    
    test)
        echo -e "${YELLOW}Running tests...${NC}"
        uv run pytest tests/ -v
        echo -e "${GREEN}✓ Tests complete${NC}"
        ;;
    
    test-cov)
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        uv run pytest tests/ -v --cov=til --cov-report=term-missing
        echo -e "${GREEN}✓ Test coverage complete${NC}"
        ;;
    
    build)
        echo -e "${YELLOW}Building TIL database...${NC}"
        uv run til build
        echo -e "${GREEN}✓ Database built${NC}"
        ;;
    
    serve)
        echo -e "${YELLOW}Starting Datasette server...${NC}"
        uv run datasette . -h 0.0.0.0 -p 8765 --cors
        ;;
    
    shell)
        echo -e "${YELLOW}Activating project shell...${NC}"
        source .venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
        echo -e "${GREEN}Run 'deactivate' to exit${NC}"
        exec $SHELL
        ;;
    
    clean)
        echo -e "${YELLOW}Cleaning build artifacts...${NC}"
        rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
        find . -type d -name __pycache__ -exec rm -rf {} +
        find . -type f -name "*.pyc" -delete
        echo -e "${GREEN}✓ Clean complete${NC}"
        ;;
    
    update)
        echo -e "${YELLOW}Updating dependencies...${NC}"
        uv sync --upgrade
        echo -e "${GREEN}✓ Dependencies updated${NC}"
        ;;
    
    all)
        echo -e "${YELLOW}Running all checks...${NC}"
        $0 format
        $0 lint
        $0 typecheck
        $0 test-cov
        echo -e "${GREEN}✓ All checks complete${NC}"
        ;;
    
    help|*)
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  init         - Initialize project environment and install dependencies"
        echo "  install      - Install project dependencies (no dev)"
        echo "  install-dev  - Install project with dev dependencies" 
        echo "  format       - Format code with ruff"
        echo "  lint         - Run ruff linter"
        echo "  fix          - Auto-fix linting issues"
        echo "  typecheck    - Run mypy type checker"
        echo "  test         - Run tests"
        echo "  test-cov     - Run tests with coverage"
        echo "  build        - Build TIL database"
        echo "  serve        - Start Datasette server"
        echo "  shell        - Activate project shell"
        echo "  clean        - Remove build artifacts"
        echo "  update       - Update all dependencies"
        echo "  all          - Run all checks (format, lint, typecheck, test-cov)"
        echo "  help         - Show this help message"
        ;;
esac