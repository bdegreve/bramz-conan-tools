ifdef ComSpec
	MKDIRP=powershell md -Force
	RMRF=powershell function rmrf ($$path) { if (Test-Path $$path) { Remove-Item -Recurse -Force $$path } }; rmrf
	TOUCH=powershell function touch ($$path) { if (Test-Path $$path) { (Get-ChildItem $$path).LastWriteTime = Get-Date } else { New-Item -ItemType file $$path } }; touch
	PYTHON=py
	ENV_PYTHON=.venv\Scripts\python.exe
else
	MKDIRP=mkdir -p
	RMRF=rm -rf
	TOUCH=touch
	PYTHON=python3
	ENV_PYTHON=.venv/bin/python
endif

all: format check

.venv/.dev-requirements.stamp: .venv dev-requirements.txt dev-constraints.txt
	$(ENV_PYTHON) -m pip install --upgrade pip setuptools wheel --constraint dev-constraints.txt
	$(ENV_PYTHON) -m pip install --requirement dev-requirements.txt --constraint dev-constraints.txt
	$(TOUCH) .venv/.dev-requirements.stamp

.venv:
	$(PYTHON) -m venv .venv

format: .venv/.dev-requirements.stamp
	$(ENV_PYTHON) -m ruff check --select I --fix .
	$(ENV_PYTHON) -m ruff format .

check: lint mypy

lint: .venv/.dev-requirements.stamp
	$(ENV_PYTHON) -m ruff check .

mypy: .venv/.dev-requirements.stamp
	$(ENV_PYTHON) -m mypy

clean:

distclean: clean
	$(RMRF) .venv
	$(RMRF) .ruff_cache
	$(RMRF) .mypy_cache

.PHONY: all format check lint mypy clean distclean
