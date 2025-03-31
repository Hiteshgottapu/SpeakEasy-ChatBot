def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'show_initialize = true' in response.data  # Ensure correct spacing
