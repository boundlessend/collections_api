def test_create_collection_and_list_with_pagination(client):
    """проверяет создание коллекций и пагинацию"""

    for index in range(1, 4):
        response = client.post(
            "/api/v1/collections", json={"name": f"Collection {index}"}
        )
        assert response.status_code == 201

    response = client.get("/api/v1/collections?page=1&size=2")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["total"] == 3
    assert data["pages"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Collection 1"


def test_add_bookmark_and_sort_inside_collection(client):
    """проверяет добавление статьи и сортировку"""

    create_response = client.post(
        "/api/v1/collections", json={"name": "Backend"}
    )
    collection_id = create_response.json()["id"]

    payloads = [
        {"title": "Zeta article", "url": "https://example.com/zeta"},
        {"title": "Alpha article", "url": "https://example.com/alpha"},
        {"title": "Gamma article", "url": "https://example.com/gamma"},
    ]
    for payload in payloads:
        response = client.post(
            f"/api/v1/collections/{collection_id}/bookmarks", json=payload
        )
        assert response.status_code == 201

    response = client.get(
        f"/api/v1/collections/{collection_id}/bookmarks?sort=title"
    )
    assert response.status_code == 200

    data = response.json()
    assert [item["title"] for item in data["items"]] == [
        "Alpha article",
        "Gamma article",
        "Zeta article",
    ]


def test_duplicate_bookmark_in_same_collection_returns_409(client):
    """проверяет защиту от дублей"""

    create_response = client.post(
        "/api/v1/collections", json={"name": "Python"}
    )
    collection_id = create_response.json()["id"]
    payload = {"title": "FastAPI docs", "url": "https://fastapi.tiangolo.com/"}

    first = client.post(
        f"/api/v1/collections/{collection_id}/bookmarks", json=payload
    )
    second = client.post(
        f"/api/v1/collections/{collection_id}/bookmarks", json=payload
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert (
        second.json()["error"]["code"]
        == "bookmark_already_exists_in_collection"
    )


def test_nonexistent_collection_returns_404(client):
    """проверяет 404 для несуществующей коллекции"""

    response = client.get("/api/v1/collections/999/bookmarks")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "collection_not_found"


def test_delete_bookmark_from_collection(client):
    """проверяет удаление статьи из коллекции"""

    collection = client.post(
        "/api/v1/collections", json={"name": "Data"}
    ).json()
    bookmark = client.post(
        f"/api/v1/collections/{collection['id']}/bookmarks",
        json={"title": "SQLAlchemy", "url": "https://docs.sqlalchemy.org/"},
    ).json()

    delete_response = client.delete(
        f"/api/v1/collections/{collection['id']}/bookmarks/{bookmark['id']}"
    )
    assert delete_response.status_code == 204

    list_response = client.get(
        f"/api/v1/collections/{collection['id']}/bookmarks"
    )
    assert list_response.status_code == 200
    assert list_response.json()["items"] == []


def test_update_collection_name(client):
    """проверяет обновление имени коллекции"""

    collection = client.post(
        "/api/v1/collections", json={"name": "Old name"}
    ).json()

    response = client.patch(
        f"/api/v1/collections/{collection['id']}", json={"name": "New name"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New name"


def test_validation_error_has_unified_format(client):
    """проверяет единый формат ошибки валидации"""

    response = client.post("/api/v1/collections", json={"name": "   "})

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"
    assert data["error"]["details"][0]["field"] == "name"
