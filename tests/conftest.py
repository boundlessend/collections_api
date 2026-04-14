import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_AUTH_TOKEN = "dev-secret-token"


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """возвращает заголовки авторизации для тестов"""

    return {"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    """создаёт тестовый клиент с отдельной базой"""

    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        """подменяет зависимость сессии для тестов"""

        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
