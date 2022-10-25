
class TestPing:

    async def test_ping(self, cli):
        resp = await cli.get("/api/v1/ping")
        assert resp.status == 200
        data = await resp.json()
        assert data["data"] == {"ping": "pong"}
        assert data["status"] == "ok"
