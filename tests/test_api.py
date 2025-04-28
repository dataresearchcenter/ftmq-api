from fastapi.testclient import TestClient

from ftmq_api.api import app

client = TestClient(app)


def test_api_1():
    res = client.get("/")
    assert res.status_code == 200


def test_api_catalog():
    res = client.get("/catalog")
    assert res.status_code == 200
    data = res.json()
    assert len(data["datasets"]) == 3


def test_api_dataset_detail():
    res = client.get("/catalog/ec_meetings")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "ec_meetings"
    assert data["entities_url"] == "http://testserver/entities?dataset=ec_meetings"
    assert (
        data["title"] == "European Commission - Meetings with interest representatives"
    )
    assert data["things"]["countries"] == [{"code": "eu", "count": 103, "label": "eu"}]
    assert data["coverage"]["countries"] == ["eu"]

    res = client.get("/not_existent")
    assert res.status_code == 404

    res = client.get("/catalog/not_existent")
    assert res.status_code == 422  # validation error


def test_api_entities():
    res = client.get("/entities")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 49822
    assert data["items"] == 100

    res = client.get("/entities?dataset=gdho")
    assert res.status_code == 200
    data = res.json()
    combined = data["total"]
    res = client.get("/entities?dataset=eu_authorities")
    assert res.status_code == 200
    data = res.json()
    combined += data["total"]

    res = client.get("/entities?dataset=gdho&dataset=eu_authorities")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == combined
    assert data["items"] == 100


def test_api_dataset_entities():
    res = client.get("/entities?dataset=ec_meetings")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 45038
    assert data["items"] == 100

    res = client.get("/entities?dataset=ec_meetings&limit=1")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 45038
    assert data["items"] == 1
    assert len(data["entities"]) == 1

    res = client.get(
        "/entities?dataset=eu_authorities&jurisdiction=eu&order_by=-name&dehydrate=true"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 151
    assert data["entities"][0]["id"] == "eu-authorities-cdt"
    assert "jurisdiction" not in data["entities"][0]["properties"]

    res = client.get(
        "/entities?dataset=eu_authorities&jurisdiction=eu&order_by=-name&featured=true"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 151
    assert data["entities"][0]["id"] == "eu-authorities-cdt"
    assert "jurisdiction" not in data["entities"][0]["properties"]

    res = client.get(
        "/entities?dataset=eu_authorities&jurisdiction__not=eu&order_by=-name"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0

    res = client.get("/entities?dataset=ec_meetings&schema=Event&limit=1&nested=true")
    assert res.status_code == 200
    data = res.json()
    assert data["entities"][0]["properties"]["organizer"][0]["schema"] == "PublicBody"


def test_api_dataset_entity_detail():
    res = client.get("/entities/addr-00177d9455d8e1b6a3f5530ea1e7e81ce1c8333f")
    data = res.json()
    assert data == {
        "id": "addr-00177d9455d8e1b6a3f5530ea1e7e81ce1c8333f",
        "caption": "SIllicon Valley",
        "schema": "Address",
        "properties": {"full": ["SIllicon Valley"]},
        "datasets": ["ec_meetings"],
        "referents": [],
    }


def test_api_reversed():
    res = client.get(
        "/entities?dataset=ec_meetings&reverse=addr-041ab56007250cb6752559152411948269a968bd"
    )
    data = res.json()
    assert data["total"] == 4
    tested = False
    for entity in data["entities"]:
        assert (
            "addr-041ab56007250cb6752559152411948269a968bd"
            in entity["properties"]["addressEntity"]
        )
        tested = True
    assert tested


def test_api_aggregation():
    res = client.get(
        "/aggregate?dataset=ec_meetings&schema=Event&aggMin=date&aggMax=date"
    )
    data = res.json()
    assert data == {
        "stats": {
            "coverage": {
                "start": "2014-11-12",
                "end": "2023-01-20",
                "frequency": "unknown",
                "countries": [],
                "schedule": None,
            },
            "things": {
                "total": 34975,
                "countries": [],
                "schemata": [
                    {
                        "name": "Event",
                        "count": 34975,
                        "label": "Event",
                        "plural": "Events",
                    }
                ],
            },
            "intervals": {
                "total": 34975,
                "countries": [],
                "schemata": [
                    {
                        "name": "Event",
                        "count": 34975,
                        "label": "Event",
                        "plural": "Events",
                    }
                ],
            },
            "entity_count": 34975,
        },
        "total": 34975,
        "query": {
            "q": None,
            "limit": 100,
            "page": 1,
            "dataset": ["ec_meetings"],
            "schema": "Event",
            "order_by": None,
            "reverse": None,
            "aggMax": ["date"],
            "aggMin": ["date"],
        },
        "url": "http://testserver/aggregate?dataset=ec_meetings&schema=Event&aggMin=date&aggMax=date&limit=100&page=1",
        "aggregations": {"date": {"min": "2014-11-12", "max": "2023-01-20"}},
    }
    res = client.get(
        "/aggregate?dataset=ec_meetings&schema=Event&aggGroups=year&aggCount=id&aggCount=location"
    )
    data = res.json()
    assert data["aggregations"] == {
        "id": {"count": 34975},
        "location": {"count": 1281},
        "year": {
            "groups": {
                "count": {
                    "id": {
                        "2014": 550,
                        "2015": 6691,
                        "2016": 5199,
                        "2017": 4047,
                        "2018": 3873,
                        "2019": 2321,
                        "2020": 4640,
                        "2021": 4079,
                        "2022": 3499,
                        "2023": 76,
                    },
                    "location": {
                        "2014": 69,
                        "2015": 366,
                        "2016": 224,
                        "2017": 171,
                        "2018": 157,
                        "2019": 141,
                        "2020": 299,
                        "2021": 280,
                        "2022": 255,
                        "2023": 21,
                    },
                }
            }
        },
    }


def test_api_entities_id_filter():
    res = client.get("/entities?entity_id=eu-authorities-chafea")
    data = res.json()
    assert data["total"] == data["items"] == 1
    res = client.get("/entities?canonical_id=eu-authorities-chafea")
    data = res.json()
    assert data["total"] == data["items"] == 1
    res = client.get("/entities?canonical_id=eu-authorities-chafea&dataset=gdho")
    data = res.json()
    assert data["total"] == data["items"] == 0
    res = client.get("/entities?canonical_id__startswith=eu-authorities-")
    data = res.json()
    assert data["total"] == 151
    res = client.get("/entities?canonical_id__startswith=eu-authorities-&dataset=gdho")
    data = res.json()
    assert data["total"] == data["items"] == 0


def test_api_search_fts():
    res = client.get("/search?dataset=eu_authorities&q=agency")
    data = res.json()
    # assert data["total"] == 151
    assert data["items"] == 51

    res = client.get("/search?q=berlin")
    data = res.json()
    # assert data["total"] == 49822
    assert data["items"] == 100

    res = client.get("/search?q=germany&dehydrate=1&dataset=eu_authorities")
    res = res.json()
    assert res["items"] == 1
    assert res["entities"] == [
        {
            "id": "eu-authorities-permanent-representation-of-germany-to-the-eu",
            "caption": "Permanent Representation of Germany to the EU",
            "schema": "PublicBody",
            "properties": {
                "name": ["Permanent Representation of Germany to the EU"],
                "country": ["eu"],
            },
            "datasets": ["eu_authorities"],
            "referents": [],
        }
    ]

    res = client.get("/autocomplete?q=european defence")
    data = res.json()
    assert len(data["candidates"]) == 1
