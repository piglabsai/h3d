# Contributing to H3D

Set up a development environment with Python 3.10 or later and install the
package in editable mode with its test and documentation dependencies.

```console
python -m pip install -e ".[test,docs]"
python -m pytest
python -m doctest README.md
python -m sphinx -W -b html docs docs/_build/html
python -m sphinx -W -b doctest docs docs/_build/doctest
```

Use the [documentation guidelines](documentation_guidelines.md) when changing
the public API. Before release, build the wheel from the source distribution
and run the tests and README examples against the installed wheel in a clean
environment.

## Publish a release

Keep development history in the private backup. Start the public repository
from a reviewed snapshot. Run the public repository's Tests workflow and tag
the verified commit with the version from `pyproject.toml`.

For the first PyPI release, configure a pending Trusted Publisher for
`piglabsai/h3d`, workflow `publish.yml`, and environment `pypi`. Dispatch
**Publish release** on the version tag. It runs the package and documentation
checks, publishes the verified Linux build to PyPI, and attaches those same
distributions to the GitHub release. Verify the published files and a clean
PyPI installation after the workflow succeeds.
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
