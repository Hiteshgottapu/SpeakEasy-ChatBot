import pytest
from my_application import create_app  

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'show_initialize = false' in response.data  # Ensure correct spacing
