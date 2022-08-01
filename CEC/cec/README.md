# NextWind
Repository for the California Energy Commission (CEC) Floating Wind Project

## Overview
(To be added)

## Team Members

* , Account Manager
* Katherine Cao, Project Manager
* Marissa Pang, Tech Lead
* Mina Shaker Mousa, Data Scientist
* Darius Alix-Williams, Data Scientist
* Elise Buck,

## Directory Structure
More detailed information can be found in `README.md` within each subdirectory.

### `cdf_examples/`
Scripts written to show examples of how cdf works that were sent to our partners.

### `cognite_apps/`
Scripts that show any specific configuration used for any of our applications.

### `Ingestion/`
Scripts that were used to ingest data that wasn't done by the Summer 2020 Interns. This includes
any currently running functions - including any that were written by the Summer 2020 Interns and
may have been updated. PreKickoff is preserved to keep track of the work initially done by the
Summer 2020 Interns so we can better reference their findings and work, etc. But anything after
their work and currently going on is tracked in this directory.

### `PreKickoff/`
Scripts for using publicly available data to build prototype services. Having been started
by summer interns, the directory was named `PreKickoff` for a historical reason; but it can
be renamed appropriately.

## Google Colab for Analytic Scripts
Given the highly interactive and narrative nature of analytic activities, the project team
decided to share and store analytic scripts (mostly `.ipynb` files) on the project's
[Google Drive](https://drive.google.com/drive/u/0/folders/12WLgSsAdq0zejD60F-_cPW1QSc6PKcxu)
rather than here on GitHub. Analytic scripts on Google Drive can be viewed, run, and commented
using Google Colab. The intention is to use GitHub repo for sharing and storing scripts
related to data engineering and production.

## Dependency Management
The current project repo uses [`poetry`](https://python-poetry.org/docs/) to manage
dependencies among different Python packages, which is essential to reproducibility.
Hence, all users of and contributors to the current project repo are expected to use
`poetry` to install and/or update packages. Following are some basic commands that can
get you started:

Once you clone the current repo into your local machine, you can run:
```
$ poetry install
```
to install the right versions of packages for running scripts in the project repo.

To use the new Python configuration that has been installed, you need to run:
```
$ poetry shell
```
which will activate the virtual environment for the project repo.

You can simply type:
```
$ exit
```
to exit from the virtual environment and return to the global (or system) Python installation.

If a new script that you are planning to add and commit to the repo requires a new package,
you can run:
```
$ poetry add [package-name]
```
This will add the new package to the repo's virtual environment and update the corresponding
information in the `pyproject.toml` and `poetry.lock`, which you need to add and commit as well.

Conversely, if changes to the project repo make a certain package not needed anymore,
you can remove it by running:
```
$ poetry remove [package-name]
```

You can check out the following resources to learn more about how to set up and use `poetry`:

- [Official Documentation](https://python-poetry.org/docs/)
- [This tutorial](https://blog.jayway.com/2019/12/28/pyenv-poetry-saviours-in-the-python-chaos/)
walks you through how to install and use `poetry` along with `pyenv` (`pyenv` helps to better manage
multiple versions of Python installation in the local machine). Furthermore, it teaches you how to
use `jupyter` with `poetry`.
