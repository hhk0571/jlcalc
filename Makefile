define HELP_MENU
Commands:
   install
       Install software to system.
   sync
       Sync local files to product server.
   test
       Run UT cases for Python code.
   clean
       Remove python artifacts.
   help
       Show help message and exit.
endef

export HELP_MENU

help:
	@echo "$$HELP_MENU"

install:
	@systemctl --version
	python ./utils/preprocessing.py
	python ./setup.py

sync: clean
	@rsync -rv --delete --exclude=.* --exclude=venv . root@10.181.132.156:/mnt/disk/projects/jlcalc/

test:
	@echo "Not implemented yet."

clean:
	find . \( -name '__pycache__' -o -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -exec rm -rf {} +

.PHONY : help install sync test clean
