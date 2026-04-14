def test_auth_is_required_for_api(client):
    """проверяет что api защищён авторизацией"""

    response = client.get("/api/v1/collections")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authorization_required"


def test_invalid_token_returns_401(client):
    """проверяет что неверный токен отклоняется"""

    response = client.get(
        "/api/v1/collections",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_create_collection_and_list_with_pagination(client, auth_headers):
    """проверяет создание коллекций и пагинацию"""

    for index in range(1, 4):
        response = client.post(
            "/api/v1/collections",
            json={"name": f"Collection {index}"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/collections?page=1&size=2", headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["total"] == 3
    assert data["pages"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Collection 1"


def test_add_bookmark_and_sort_inside_collection(client, auth_headers):
    """проверяет добавление статьи и сортировку"""

    create_response = client.post(
        "/api/v1/collections",
        json={"name": "Backend"},
        headers=auth_headers,
    )
    collection_id = create_response.json()["id"]

    payloads = [
        {"title": "Zeta article", "url": "https://example.com/zeta"},
        {"title": "Alpha article", "url": "https://example.com/alpha"},
        {"title": "Gamma article", "url": "https://example.com/gamma"},
    ]
    for payload in payloads:
        response = client.post(
            f"/api/v1/collections/{collection_id}/bookmarks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        f"/api/v1/collections/{collection_id}/bookmarks?sort=title",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert [item["title"] for item in data["items"]] == [
        "Alpha article",
        "Gamma article",
        "Zeta article",
    ]


def test_duplicate_bookmark_in_same_collection_returns_409(
    client, auth_headers
):
    """проверяет защиту от дублей"""

    create_response = client.post(
        "/api/v1/collections",
        json={"name": "Python"},
        headers=auth_headers,
    )
    collection_id = create_response.json()["id"]
    payload = {"title": "FastAPI docs", "url": "https://fastapi.tiangolo.com/"}

    first = client.post(
        f"/api/v1/collections/{collection_id}/bookmarks",
        json=payload,
        headers=auth_headers,
    )
    second = client.post(
        f"/api/v1/collections/{collection_id}/bookmarks",
        json=payload,
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert (
        second.json()["error"]["code"]
        == "bookmark_already_exists_in_collection"
    )


def test_nonexistent_collection_returns_404(client, auth_headers):
    """проверяет 404 для несуществующей коллекции"""

    response = client.get(
        "/api/v1/collections/999/bookmarks", headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "collection_not_found"


def test_delete_bookmark_from_collection(client, auth_headers):
    """проверяет удаление статьи из коллекции"""

    collection = client.post(
        "/api/v1/collections",
        json={"name": "Data"},
        headers=auth_headers,
    ).json()
    bookmark = client.post(
        f"/api/v1/collections/{collection['id']}/bookmarks",
        json={"title": "SQLAlchemy", "url": "https://docs.sqlalchemy.org/"},
        headers=auth_headers,
    ).json()

    delete_response = client.delete(
        f"/api/v1/collections/{collection['id']}/bookmarks/{bookmark['id']}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    list_response = client.get(
        f"/api/v1/collections/{collection['id']}/bookmarks",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["items"] == []


def test_update_collection_name(client, auth_headers):
    """проверяет обновление имени коллекции"""

    collection = client.post(
        "/api/v1/collections",
        json={"name": "Old name"},
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/api/v1/collections/{collection['id']}",
        json={"name": "New name"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New name"


def test_validation_error_has_unified_format(client, auth_headers):
    """проверяет единый формат ошибки валидации"""

    response = client.post(
        "/api/v1/collections",
        json={"name": "   "},
        headers=auth_headers,
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"
    assert data["error"]["details"][0]["field"] == "name"
