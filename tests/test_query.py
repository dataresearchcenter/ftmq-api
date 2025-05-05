import pytest
from pydantic import ValidationError

from ftmq_api.query import Query, ViewQueryParams


def test_query():
    params = ViewQueryParams()
    q = Query.from_params(params)
    assert q.to_dict() == {"limit": 100, "offset": 0}

    params = ViewQueryParams(dataset=["gdho"])
    q = Query.from_params(params)
    assert q.to_dict() == {"limit": 100, "offset": 0, "dataset__in": {"gdho"}}

    params = ViewQueryParams(dataset=["gdho", "ec_meetings"])
    q = Query.from_params(params)
    assert q.to_dict() == {
        "limit": 100,
        "offset": 0,
        "dataset__in": {"ec_meetings", "gdho"},
    }

    params = ViewQueryParams(schema="Event")
    q = Query.from_params(params)
    assert q.to_dict() == {"limit": 100, "offset": 0, "schema": "Event"}

    params = ViewQueryParams(schema="Event", prop="date", value=2023)
    q = Query.from_params(params)
    assert q.to_dict() == {
        "limit": 100,
        "offset": 0,
        "schema": "Event",
        "date": "2023",
    }

    params = ViewQueryParams(
        schema="Event", prop="date", value=2023, order_by="location", page=2, limit=10
    )
    q = Query.from_params(params)
    assert q.to_dict() == {
        "limit": 10,
        "offset": 10,
        "schema": "Event",
        "date": "2023",
        "order_by": ["location"],
    }

    params = ViewQueryParams(
        schema="Event", date__gte=2023, order_by="-location", page=2, limit=10
    )
    q = Query.from_params(params)
    assert q.to_dict() == {
        "limit": 10,
        "offset": 10,
        "schema": "Event",
        "date__gte": "2023",
        "order_by": ["-location"],
    }

    # invalid schema lookups
    with pytest.raises(ValidationError):
        ViewQueryParams(schema="foo")
