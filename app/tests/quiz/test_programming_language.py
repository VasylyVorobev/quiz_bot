

class TestCreateProgrammingLanguage:

    async def test_create_programming_language_success(self, cli):
        data = {"title": "sql"}
        resp = await cli.post("/api/v1/programming_language/", json=data)
        assert resp.status == 201
        result = await resp.json()
        assert result["status"] == "ok"
        assert result["data"]["id"] is not None
        assert result["data"]["title"] == data["title"]

        resp = await cli.post("/api/v1/programming_language/", json=data)
        assert resp.status == 400

    async def test_invalid(self, cli):
        data = {"invalid": "python"}
        resp = await cli.post("/api/v1/programming_language/", json=data)
        assert resp.status == 422


class TestListProgrammingLanguage:

    async def test_success(self, cli, get_programming_languages: list[tuple]):
        resp = await cli.get("/api/v1/programming_language/")
        assert resp.status == 200
        result = await resp.json()
        assert result["status"] == "ok"
        assert result["data"]["count"] == len(get_programming_languages)

    async def test_pagination(self, cli, get_programming_languages: list[tuple]):
        resp = await cli.get("/api/v1/programming_language/", params={"page": 1, "page_size": 1})
        assert resp.status == 200
        result = await resp.json()
        assert result["status"] == "ok"
        assert len(result["data"]["result"]) == 1
        assert result["data"]["result"][0]["id"] == get_programming_languages[0][0]


class TestGetProgrammingLanguage:
    async def test_success(self, cli, get_programming_language):
        language_id, title = get_programming_language
        resp = await cli.get(f"/api/v1/programming_language/{language_id}/")
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["title"] == title

    async def test_invalid(self, cli):
        resp = await cli.get("/api/v1/programming_language/99999/")
        assert resp.status == 404

        resp = await cli.get("/api/v1/programming_language/invalid_number/")
        assert resp.status == 422


class TestUpdateProgrammingLanguage:
    async def test_success(self, cli, get_programming_language):
        language_id, title = get_programming_language
        resp = await cli.put(
            f"/api/v1/programming_language/{language_id}/",
            json={"title": "typescript"}
        )
        assert resp.status == 200
        result = await resp.json()
        assert result["data"]["title"] == "typescript"

    async def test_invalid(self, cli, get_programming_language, get_programming_languages):
        language_id, title = get_programming_language
        resp = await cli.put(
            f"/api/v1/programming_language/{language_id}/",
            json={"title": "python"}
        )
        assert resp.status == 400  # already exists

        resp = await cli.put("/api/v1/programming_language/9999/", json={"title": "language"})
        assert resp.status == 404
