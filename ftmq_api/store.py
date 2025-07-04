from functools import cache
from typing import TYPE_CHECKING, Literal, TypeAlias

from fastapi import HTTPException
from ftmq.model import Catalog, Dataset
from ftmq.query import Q
from ftmq.store import Store
from ftmq.store import get_store as _get_store
from ftmq.types import CE, CEGenerator
from ftmq.util import get_dehydrated_proxy, get_featured_proxy

from ftmq_api.logging import get_logger
from ftmq_api.settings import Settings

if TYPE_CHECKING:
    from ftmq_api.views import RetrieveParams

log = get_logger(__name__)
settings = Settings()


@cache
def get_catalog() -> Catalog:
    if settings.catalog is not None:
        return Catalog._from_uri(settings.catalog)
    return Catalog()


@cache
def get_dataset(name: str) -> Dataset:
    catalog = get_catalog()
    dataset = catalog.get(name)
    if dataset is None:
        raise HTTPException(404, detail=[f"Dataset `{name}` not found."])
    return dataset


@cache
def get_store(dataset: str | None = None) -> Store:
    catalog = get_catalog()
    if dataset is not None:
        dataset = get_dataset(dataset)
        store = _get_store(catalog=catalog, dataset=dataset, uri=settings.store_uri)
    else:
        store = _get_store(catalog=catalog, uri=settings.store_uri)
    return store


def retrieve_entities(entities: CEGenerator, params: "RetrieveParams") -> CEGenerator:
    for proxy in entities:
        if params.dehydrate:
            proxy = get_dehydrated_proxy(proxy)
        elif params.featured:
            proxy = get_featured_proxy(proxy)
        yield proxy


class View:
    def __init__(
        self,
        dataset: str | None = None,
    ) -> None:
        self.store = get_store(dataset)
        self.dataset = dataset
        self.query = self.store.query()
        self.view = self.store.default_view()

        self.stats = self.query.stats
        self.count = self.query.count
        self.aggregations = self.query.aggregations
        self.get_adjacents = self.query.get_adjacents

    def get_entity(self, entity_id: str, params: "RetrieveParams") -> CE:
        canonical = self.store.linker.get_canonical(entity_id)
        proxy = self.view.get_entity(canonical)
        if proxy is None:
            # try to get original one FIXME
            proxy = self.view.get_entity(entity_id)
            if proxy is None:
                raise HTTPException(404, detail=[f"Entity `{entity_id}` not found."])
        if params.dehydrate:
            return get_dehydrated_proxy(proxy)
        if params.featured:
            return get_featured_proxy(proxy)
        return proxy

    def get_entities(self, query: Q, params: "RetrieveParams") -> CEGenerator:
        yield from retrieve_entities(self.query.entities(query), params)

    def similar(self, entity_id: str, params: "RetrieveParams") -> CEGenerator:
        yield from retrieve_entities(self.query.similar(entity_id), params)


@cache
def get_view(dataset: str | None = None) -> View:
    return View(dataset)


# cache at boot time
catalog = get_catalog()
Datasets: TypeAlias = Literal[tuple(catalog.names or ["default"])]
