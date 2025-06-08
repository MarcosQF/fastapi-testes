from fastapi.testclient import TestClient

from fastapi_testes.main import app


def test_root_must_return_helloworld():
    client = TestClient(app)

    response = client.get('/')

    assert response.json() == {'message': 'Hello World'}
