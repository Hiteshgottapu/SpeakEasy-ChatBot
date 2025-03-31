import pytest
from my_application import create_app  # Adjust the import according to your app structure

@pytest.fixture
def client():
    # Create an app instance using the factory function
    app = create_app()
    
    # Set the app to testing mode
    app.config['TESTING'] = True

    # Use Flask's test client for simulating HTTP requests
    with app.test_client() as client:
        # Push the application context
        with app.app_context():
            yield client  # Return the test client for use in tests

# Test for the home route
def test_home_route(client):
    # Simulate a GET request to the root route
    response = client.get('/')
    
    # Ensure the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Check if the response contains the text 'show_initialize = false'
    assert b'show_initialize = false' in response.data
