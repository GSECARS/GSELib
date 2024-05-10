# GSELib

![Licence](https://img.shields.io/badge/License-MIT-teal.svg) ![Python](https://img.shields.io/badge/Python-3.12-22558a.svg?logo=python&color=22558a)

A library for GSECARS that provides a set of tools for GUI development, data analysis, and data visualization.

------------
## Table of Contents
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

------------
## Development
To set up the project for development, just clone the repository, install all the development requirements, the project and the pre-commit hooks.

```bash
git clone -b main https://github.com/GSECARS/gselib/git && cd gselib
pip install -e .[development]
pre-commit install
```

> Pre-commit is a tool that checks your code for any errors before you commit it. It helps maintain the quality of the codebase and reduces the chance of pushing faulty code. When you try to commit your changes, pre-commit will run checks defined in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file. If any of these checks fail, the commit will be aborted.

## Contributing

All contributions to the GSELib are welcome! Here are some ways you can help:
- Report a bug by opening an [issue](https://github.com/GSECARS/gselib/issues).
- Add new features, fix bugs or improve documentation by submitting a [pull request](https://github.com/GSECARS/gselib/pulls).

Please adhere to the [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow) model when making your contributions! This means creating a new branch for each feature or bug fix, and submitting your changes as a pull request against the main branch. If you're not sure how to contribute, please open an issue and we'll be happy to help you out.

By contributing to the GSELib project, you agree that your contributions will be licensed under the MIT License.

------------
## License
GSELib is distributed under the MIT license. You should have received a [copy](LICENSE) of the MIT License along with this program. If not, see https://mit-license.org/ for additional details.