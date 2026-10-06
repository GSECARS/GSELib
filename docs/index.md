# GSELib

A collection of tools for GSECARS.

## Installation

```bash
pip install gselib            # base (no extras)
pip install 'gselib[cloud]'   # with Nextcloud support
pip install 'gselib[logbook]' # with Google Docs logbook support
pip install 'gselib[all]'     # everything
```

## Modules

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Cloud
:link: cloud
:link-type: doc

Storage and share management for cloud services. Currently supports Nextcloud via REST API and `occ`.
:::

:::{grid-item-card} Logbook
:link: logbook
:link-type: doc

Beamline logbook backed by Google Docs. Append timestamped entries, export to PDF, and share with your team in real time.
:::

:::{grid-item-card} API Reference
:link: autoapi/index
:link-type: doc

Auto-generated reference for all public classes and functions.
:::

::::

```{toctree}
:maxdepth: 2
:hidden:

cloud
logbook
API Reference <autoapi/index>
```
