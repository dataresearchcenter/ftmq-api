from anystore.model import StoreModel
from nomenklatura.settings import DB_URL
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ftmq_api import __version__

DEFAULT_DESCRIPTION = """
This api exposes a
[FollowTheMoney Store](https://github.com/alephdata/followthemoney-store) as a
read-only endpoint that allows granular data fetching and searching.

* [Available datasets in this api instance](/catalog)
* [More about the FollowTheMoney model](https://followthemoney.tech/explorer/)

This api works for all store implementations found in
[`nomenklatura.store`](https://github.com/opensanctions/nomenklatura/tree/main/nomenklatura/store)

There are four main api endpoints:

* Retrieve a single entity based on its id and dataset, optionally with inlined
  adjacent entities: `/{dataset}/entities/{entity_id}`
* Retrieve a list of entities based on filter criteria and sorting, with
  pagination: `/{dataset}/entities?{params}`
* Search for entities (by their name property types) via
  [Sqlite FTS](https://www.sqlite.org/fts5.html): `/{dataset}/search?q=<search term>`
* Aggregate (on store backend level) `sum`, `avg`, `max`, `min` for ftm properties

Two more endpoints for catalog / dataset metadata:

* Catalog overview: [`/catalog`](/catalog)
* Dataset metadata: `/catalog/{dataset}`
"""


class ApiContact(BaseModel):
    name: str = "Data and Research Center – DARC"
    url: str = "https://dataresearchcenter.org"
    email: str = "hi@dataresearchcenter.org"


class ApiInfo(BaseModel):
    title: str = "FTMQ Api"
    contact: ApiContact = ApiContact()
    description_uri: str | None = None


class Settings(BaseSettings):
    """
    `anystore` settings management using
    [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

    Note:
        All settings can be set via environment variables in uppercase,
        prepending `ANYSTORE_` (except for those with a given prefix)
    """

    model_config = SettingsConfigDict(
        env_prefix="ftmq_api_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )

    debug: bool = Field(False, alias="debug")

    catalog: str | None = None
    """Catalog uri"""

    store_uri: str = DB_URL
    """ftmq store uri"""

    build_api_key: str = "secret-key-for-build"
    """Backend api key to use for build process (higher limit)"""

    min_search_length: int = 3
    """Minimum search query length"""

    use_cache: bool = False
    """Activate caching"""

    cache: StoreModel = StoreModel(
        uri=".cache", backend_config={"redis_prefix": f"ftmq-api/{__version__}"}
    )
    """Api cache (via anystore)"""

    allowed_origin: list[str] = ["http://localhost:3000"]
    """Allowed origins"""

    default_limit: int = 100
    """Default public pagination limit"""

    info: ApiInfo = ApiInfo()
    """Rendered information on redoc page"""
