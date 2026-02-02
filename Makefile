# ===========================
# Terra Scout Makefile
# ===========================

.PHONY: help install install-dev setup verify clean test lint format train evaluate

# Default target
help:
	@echo "Terra Scout - Available Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make setup        Full setup (venv + install)"
	@echo "  make verify       Verify installation"
	@echo ""
	@echo "Development:"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make clean        Clean generated files"
	@echo ""
	@echo "Training:"
	@echo "  make train        Start training"
	@echo "  make evaluate     Evaluate trained model"
	@echo "  make tensorboard  Start TensorBoard"
	@echo ""

# ===========================
# Setup
# ===========================

install:
	pip install -e ./agent
	pip install -r training/requirements.txt

install-dev: install
	pip install pytest pytest-cov black isort flake8 mypy

setup:
	python -m venv venv
	@echo "Activate venv with: .\venv\Scripts\Activate.ps1"
	@echo "Then run: make install-dev"

verify:
	python scripts/verify_installation.py

# ===========================
# Development
# ===========================

test:
	pytest agent/tests/ -v --cov=agent/src

lint:
	flake8 agent/src/ training/scripts/ shared/
	mypy agent/src/ --ignore-missing-imports

format:
	black agent/ training/ shared/ scripts/
	isort agent/ training/ shared/ scripts/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ===========================
# Training
# ===========================

train:
	python training/scripts/train.py

train-config:
	python training/scripts/train.py --config training/configs/training_config.yaml

evaluate:
	python training/scripts/evaluate.py --model training/checkpoints/model_best.zip

tensorboard:
	tensorboard --logdir training/logs

# ===========================
# Git
# ===========================

commit-docs:
	git add docs/ *.md
	git commit -m "docs: update documentation"

commit-all:
	git add .
	git commit -m "chore: update project files"

push:
	git push origin main