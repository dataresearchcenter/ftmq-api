[![Python test and package](https://github.com/dataresearchcenter/ftmq-api/actions/workflows/python.yml/badge.svg)](https://github.com/dataresearchcenter/ftmq-api/actions/workflows/python.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Coverage Status](https://coveralls.io/repos/github/dataresearchcenter/ftmq-api/badge.svg?branch=main)](https://coveralls.io/github/dataresearchcenter/ftmq-api?branch=main)
[![AGPLv3+ License](https://img.shields.io/pypi/l/ftmq-api)](./LICENSE)

# ftmq-api

Expose [followthemoney](https://followthemoney.tech) data via readonly [FastAPI](https://fastapi.tiangolo.com/). Data is stored in a *statement-based* store adapted by [ftmq](https://github.com/investigativedata/ftmq) from [nomenklatura](https://github.com/opensanctions/nomenklatura).

An example instance is deployed here: https://api.investigraph.dev

The api features filtering for `dataset`s, entity `Schema` and `Property` values, sorting and a search endpoint to query against a [full text search via `ftmq-search`](https://github.com/investigativedata/ftmq-search).

## Documentation

https://docs.investigraph.dev/lib/ftmq-api

## Development

This package is using [poetry](https://python-poetry.org/) for packaging and dependencies management, so first [install it](https://python-poetry.org/docs/#installation).

Clone the repository to a local destination.

Within the root directory, run

    poetry install --with dev

This installs a few development dependencies, including [pre-commit](https://pre-commit.com/) which needs to be registered:

    poetry run pre-commit install

Before creating a commit, this checks for correct code formatting (isort, black) and some other useful stuff (see: `.pre-commit-config.yaml`)

Spin up dev server and populate with fixtures data:

    make api

Run test & typing:

    make test
    make typecheck

## supported by

In 2023, developing of this project was supported by [Media Tech Lab Bayern batch #3](https://github.com/media-tech-lab)

<a href="https://www.media-lab.de/en/programs/media-tech-lab">
    <img src="https://raw.githubusercontent.com/media-tech-lab/.github/main/assets/mtl-powered-by.png" width="240" title="Media Tech Lab powered by logo">
</a>

## License and Copyright

`ftmq-api`, (C) 2023 Simon Wörpel
`ftmq-api`, (C) 2024-2025 investigativedata.io
`ftmq-api`, (C) 2025 [Data and Research Center – DARC](https://dataresearchcenter.org)

`ftmq-api` is licensed under the AGPLv3 or later license.

Prior to version 3.0.0, `ftmq-api` was released under the MIT license and was called `ftmstore-fastapi`.

see [NOTICE](./NOTICE) and [LICENSE](./LICENSE)
