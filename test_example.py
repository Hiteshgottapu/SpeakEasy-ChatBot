# test_example.py
import pytest
from main import app, LanguageChatbot
from flask import session
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def chatbot():
    return LanguageChatbot(
        target_language='es',
        current_language='en',
        proficiency_level='beginner'
    )

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'show_initialize=True' in response.data

def test_initialize_chatbot(client):
    data = {
        "target_language": "es",
        "current_language": "en",
        "proficiency_level": "beginner"
    }
    response = client.post('/index', 
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 200
    assert 'session_id' in response.get_json()

def test_chat_endpoint(client):
    # First initialize the chatbot
    init_data = {
        "target_language": "es",
        "current_language": "en",
        "proficiency_level": "beginner"
    }
    client.post('/index', 
                data=json.dumps(init_data),
                content_type='application/json')
    
    # Test chat endpoint
    chat_data = {"user_input": "Hello"}
    response = client.post('/chat',
                          data=json.dumps(chat_data),
                          content_type='application/json')
    assert response.status_code == 200
    assert 'response' in response.get_json()

def test_new_chat_session(client):
    response = client.post('/new-chat')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'message' in json_data
    assert 'redirect_url' in json_data

def test_chatbot_translation(chatbot):
    response = chatbot.generate_response("Hello")
    assert response is not None
    assert isinstance(response, str)

def test_chatbot_preprocessing(chatbot):
    processed = chatbot.preprocess_input("Hello!")
    assert processed == "hello"
    assert isinstance(processed, str)

def test_chat_history_endpoint(client):
    response = client.get('/chat-history')
    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)

def test_feedback_endpoint(client):
    # First initialize the chatbot
    init_data = {
        "target_language": "es",
        "current_language": "en",
        "proficiency_level": "beginner"
    }
    client.post('/index', 
                data=json.dumps(init_data),
                content_type='application/json')
    
    response = client.get('/feedback')
    assert response.status_code == 200
    feedback_data = response.get_json()
    assert 'mistakes' in feedback_data
    assert 'tips' in feedback_data
