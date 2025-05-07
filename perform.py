from fastapi.testclient import TestClient

from ftmq_api.api import app

client = TestClient(app)

client.get("/catalog")
client.get("/catalog/ec_meetings")

client.get("/entities")
client.get("/entities?dataset=eu_authorities")

client.get("/entities?dataset=gdho&dataset=eu_authorities")
client.get("/entities?dataset=gdho&dataset=eu_authorities&stats=1")

client.get("/entities?dataset=ec_meetings&schema=Event&limit=1&nested=true")
