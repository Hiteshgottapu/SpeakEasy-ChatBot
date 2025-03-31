import pytest
from your_application import create_app  # Adjust the import statement as per your application structure

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
    assert b'show_initialize = true' in response.data  # Ensure correct spacing
