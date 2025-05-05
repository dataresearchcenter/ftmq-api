from collections.abc import Iterable
from functools import cache

from anystore.decorators import anycache
from anystore.store import BaseStore, get_store
from anystore.util import make_data_checksum
from fastapi import HTTPException
from fastapi import Query as QueryField
from fastapi import Request
from fastapi.responses import RedirectResponse
from ftmq.model import Catalog, Dataset
from ftmq.types import CE
from ftmq.util import get_dehydrated_proxy
from ftmq_search.store import get_store as get_search_store
from furl import furl

from ftmq_api.query import (
    AggregationParams,
    Query,
    RetrieveParams,
    SearchQuery,
    SearchQueryParams,
    ViewQueryParams,
)
from ftmq_api.serialize import (
    AggregationResponse,
    AutocompleteResponse,
    EntitiesResponse,
    EntityResponse,
)
from ftmq_api.settings import Settings
from ftmq_api.store import get_catalog, get_dataset, get_view

settings = Settings()


def get_cache_key(request: Request, *args, **kwargs) -> str | None:
    if not settings.use_cache:
        return None
    f = furl(str(request.url))
    return f"{f.host}{f.path}/{make_data_checksum(f.querystr)}"


@cache
def get_cache() -> BaseStore:
    return get_store(**settings.cache.model_dump())


def get_retrieve_params(
    nested: bool = QueryField(
        False, description="Inline adjacent entities instead of their ids"
    ),
    featured: bool = QueryField(
        False, description="Only include featured properties and caption"
    ),
    dehydrate: bool = QueryField(
        False, description="Only include id, schema and caption"
    ),
    dehydrate_nested: bool = QueryField(True, description="Dehydrate nested entities"),
) -> RetrieveParams:
    return RetrieveParams(
        nested=nested,
        featured=featured,
        dehydrate=dehydrate,
        dehydrate_nested=dehydrate_nested,
    )


def get_aggregation_params(
    aggSum: list[str] = QueryField([], description="Fields to aggregate for SUM"),
    aggMax: list[str] = QueryField([], description="Fields to aggregate for MAX"),
    aggMin: list[str] = QueryField([], description="Fields to aggregate for MIN"),
    aggAvg: list[str] = QueryField([], description="Fields to aggregate for AVG"),
) -> AggregationParams:
    return AggregationParams(aggSum=aggSum, aggMin=aggMin, aggMax=aggMax, aggAvg=aggAvg)


@anycache(store=get_cache(), key_func=get_cache_key, model=Catalog)
def dataset_list(request: Request) -> Catalog:
    catalog = get_catalog()
    datasets: list[Dataset] = []
    for dataset in catalog.datasets:
        view = get_view(dataset.name)
        dataset.apply_stats(view.stats())
        datasets.append(dataset)
    catalog.datasets = datasets
    return catalog


@anycache(store=get_cache(), key_func=get_cache_key, model=Dataset)
def dataset_detail(request: Request, name: str) -> Dataset:
    view = get_view(name)
    dataset = get_dataset(name)
    dataset.apply_stats(view.stats())
    return dataset


@anycache(store=get_cache(), key_func=get_cache_key, model=EntitiesResponse)
def entity_list(
    request: Request,
    retrieve_params: RetrieveParams,
    authenticated: bool | None = False,
) -> EntitiesResponse:
    view = get_view()
    params = ViewQueryParams.from_request(request, authenticated)
    query = Query.from_params(params)
    adjacents = []
    entities = [e for e in view.get_entities(query, retrieve_params)]
    if retrieve_params.nested:
        adjacents = view.get_adjacents(entities)
    return EntitiesResponse.from_view(
        request=request,
        entities=entities,
        adjacents=adjacents,
        stats=view.stats(query),
        authenticated=authenticated,
    )


@anycache(store=get_cache(), key_func=get_cache_key, serialization_mode="pickle")
def entity_detail(
    request: Request,
    entity_id: str,
    retrieve_params: RetrieveParams,
) -> EntityResponse | RedirectResponse:
    view = get_view()
    entity = view.get_entity(entity_id, retrieve_params)
    adjacents: Iterable[CE] = []
    if retrieve_params.nested:
        adjacents = [e[1] for e in view.view.get_adjacent(entity)]
        if retrieve_params.dehydrate_nested:
            adjacents = [get_dehydrated_proxy(e) for e in adjacents]
    if entity.id != entity_id:  # we have a redirect to a merged entity
        url = furl(request.url)
        url.path.segments[-1] = entity.id
        response = RedirectResponse(url)
        response.headers["X-Entity-ID"] = entity.id
        response.headers["X-Entity-Schema"] = entity.schema.name
        return response
    return EntityResponse.from_entity(entity, adjacents)


@anycache(store=get_cache(), key_func=get_cache_key, model=AggregationResponse)
def aggregation(request: Request) -> AggregationResponse:
    view = get_view()
    params = ViewQueryParams.from_request(request)
    query = Query.from_params(params)
    return AggregationResponse.from_view(
        request=request,
        aggregations=view.aggregations(query),
        stats=view.stats(query),
    )


@anycache(store=get_cache(), key_func=get_cache_key, model=EntitiesResponse)
def search(request: Request, authenticated: bool | None = False) -> EntitiesResponse:
    params = SearchQueryParams.from_request(request, authenticated)
    q = params.q
    if q is None or len(q) < settings.min_search_length:
        raise HTTPException(400, [f"Invalid search query: `{q}`"])
    params.q = None
    query = SearchQuery.from_params(params)
    store = get_search_store()
    entities = (e.to_proxy() for e in store.search(q, query))
    return EntitiesResponse.from_view(
        request=request,
        entities=entities,
        authenticated=authenticated,
    )


@anycache(store=get_cache(), key_func=get_cache_key, model=AutocompleteResponse)
def autocomplete(request, q: str) -> AutocompleteResponse:
    if q is None or len(q) < 4:
        raise HTTPException(400, [f"Invalid search query: `{q}`"])
    store = get_search_store()
    return AutocompleteResponse(candidates=store.autocomplete(q))


@anycache(store=get_cache(), key_func=get_cache_key, model=EntitiesResponse)
def similar(
    request: Request,
    entity_id: str,
    retrieve_params: RetrieveParams,
    authenticated: bool | None = False,
) -> EntitiesResponse:
    view = get_view()
    entities = [e[0] for e in view.similar(entity_id, retrieve_params)]
    return EntitiesResponse.from_view(
        request=request,
        entities=entities,
        authenticated=authenticated,
    )
