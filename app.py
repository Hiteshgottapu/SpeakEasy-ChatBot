from flask import Flask, request, jsonify, render_template, session  # Import session for session management
import sqlite3
import os
import re
from googletrans import Translator, LANGUAGES  
import uuid  # Import uuid to generate unique session IDs
import json  # Import JSON module for file handling

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Ensure database file exists
if not os.path.exists("user_progress.db"):
    print("Database file not found. Creating a new one...")
    open("user_progress.db", "w").close()

class LanguageChatbot:
    def __init__(self, target_language, current_language, proficiency_level):
        self.target_language = target_language
        self.current_language = current_language
        self.proficiency_level = proficiency_level
        self.mistakes = []
        
        # Add error handling for Translator initialization
        try:
            self.translator = Translator()  # Initialize Google Translator
        except Exception as e:
            print(f"Error initializing translator: {e}")

        self.reference_pairs = self.get_reference_pairs()
        self.db_connection = sqlite3.connect("user_progress.db", check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input TEXT,
                correction TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                bot_response TEXT,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db_connection.commit()

    def save_chat_to_db(self, user_input, bot_response, session_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_input, bot_response, session_id) VALUES (?, ?, ?)
            """, (user_input, bot_response, session_id))
            self.db_connection.commit()
        except sqlite3.Error as e:
            print(f"Error saving chat to database: {e}")

    def preprocess_input(self, user_input):
        # Normalize text: remove extra spaces, handle case sensitivity, and strip punctuation
        user_input = user_input.strip().lower()
        user_input = re.sub(r'[^\w\s]', '', user_input)  # Remove punctuation
        return user_input

    def get_reference_pairs(self):
        # Add language-specific reference pairs based on proficiency level
        if self.proficiency_level.lower() == "beginner":
            return [
                {"source_sentence": "Hello", "target_sentence": "Hola"},
                {"source_sentence": "How are you?", "target_sentence": "¿Cómo estás?"}
            ]
        # Add more pairs for other levels
        return []

    def generate_response(self, user_input):
        try:
            # Use Google Translator to translate the input
            translated = self.translator.translate(
                text=user_input, src=self.current_language, dest=self.target_language
            )
            # Return only the translated text
            return translated.text
        except Exception as e:
            print(f"Error generating response: {e}")  # Log the error for debugging
            return "I'm sorry, I couldn't process your request. Please try again later."

    def detect_and_record_mistakes(self, user_input):
        # Placeholder for mistake detection logic (not supported by Google Translator)
        return None

    def save_mistake_to_db(self, mistake):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            INSERT INTO mistakes (input, correction) VALUES (?, ?)
        """, (mistake["input"], mistake["correction"]))
        self.db_connection.commit()

    def provide_feedback(self):
        feedback = {"mistakes": [], "tips": []}
        if not self.mistakes:
            feedback["tips"].append("Great job! No mistakes recorded.")
        else:
            feedback["mistakes"] = [
                {"input": mistake["input"], "correction": mistake["correction"]}
                for mistake in self.mistakes
            ]
            feedback["tips"].extend([
                "Practice regularly to reduce common errors.",
                "Focus on vocabulary and grammar rules."
            ])
        return feedback

    def __del__(self):
        if hasattr(self, "db_connection") and self.db_connection:
            self.db_connection.close()


# Flask routes
@app.route("/index", methods=["GET", "POST"])
def initialize_chatbot():
    global chatbot
    if request.method == "GET":
        # Render the form for user input
        return render_template("index.html", show_initialize=True)
    elif request.method == "POST":
        try:
            data = request.json
            target_language = data.get("target_language")
            current_language = data.get("current_language")
            proficiency_level = data.get("proficiency_level")

            if not target_language or not current_language or not proficiency_level:
                return jsonify({"error": "All fields are required."}), 400

            # Initialize the chatbot
            chatbot = LanguageChatbot(target_language, current_language, proficiency_level)
            session['session_id'] = str(uuid.uuid4())  # Create a session ID
            print(f"Chatbot initialized with session ID: {session['session_id']}")  # Debugging log
            return jsonify({"message": "Chatbot initialized successfully.", "session_id": session['session_id']})
        except Exception as e:
            print(f"Error initializing chatbot: {e}")  # Debugging log
            return jsonify({"error": f"Failed to initialize chatbot: {e}"}), 500


@app.route("/new-chat", methods=["POST"])
def new_chat():
    try:
        # Generate a new unique session ID
        session['session_id'] = str(uuid.uuid4())
        print(f"Generated new session ID: {session['session_id']}")  # Debugging log

        # Save the session ID to the database
        db_connection = sqlite3.connect("user_progress.db")
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (session_id) VALUES (?)
        """, (session['session_id'],))
        db_connection.commit()
        print("New session ID saved to the database.")  # Debugging log

        # Return a response indicating the need to show the initialization container
        return jsonify({"message": "New chat session started.", "redirect_url": "/?show_initialize=true"})
    except sqlite3.Error as e:
        print(f"Error creating new chat session: {e}")  # Debugging log
        return jsonify({"error": "Failed to start a new chat session."}), 500
    finally:
        if 'db_connection' in locals():
            db_connection.close()


@app.route("/chat", methods=["POST"])
def chat():
    if 'chatbot' not in globals() or chatbot is None:
        return jsonify({"error": "Chatbot is not initialized."}), 400

    try:
        # Generate session ID if it doesn't exist
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            
        session_id = session['session_id']
        data = request.json
        user_input = data.get("user_input")
        
        if not user_input:
            return jsonify({"error": "User input is required."}), 400

        normalized_input = chatbot.preprocess_input(user_input)
        response = chatbot.generate_response(normalized_input)  # Ensure response is generated
        mistake = chatbot.detect_and_record_mistakes(normalized_input)

        chatbot.save_chat_to_db(user_input, response, session_id)
        
        # Include the bot's response and target language code in the JSON for playback
        return jsonify({
            "response": response,
            "mistake": mistake,
            "playback_response": response,
            "language_code": chatbot.target_language  # Pass the target language code
        })
    except Exception as e:
        print(f"Error in chat route: {e}")  # Log the error for debugging
        return jsonify({"error": f"Failed to process chat: {e}"}), 500


@app.route("/chat-history", methods=["GET"])
def chat_history():
    """Retrieve chat history grouped by session from the SQLite database."""
    try:
        # Connect to the database directly to fetch chat history
        db_connection = sqlite3.connect("user_progress.db")
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT session_id, user_input, bot_response, timestamp 
            FROM chat_history 
            ORDER BY session_id, timestamp ASC
        """)
        rows = cursor.fetchall()

        # Debugging log to verify rows fetched
        print(f"Fetched {len(rows)} rows from chat_history table.")

        # Group chat history by session_id
        grouped_history = {}
        for row in rows:
            session_id = row[0]
            if session_id not in grouped_history:
                grouped_history[session_id] = []
            grouped_history[session_id].append({
                "user_input": row[1],
                "bot_response": row[2],
                "timestamp": row[3]
            })

        if not grouped_history:
            print("No chat history found.")  # Debugging log
            return jsonify({"message": "No chat history found."}), 200

        return jsonify(grouped_history)
    except sqlite3.Error as e:
        print(f"Error fetching chat history: {e}")  # Debugging log
        return jsonify({"error": f"Failed to fetch chat history from database: {e}"}), 500
    finally:
        if db_connection:
            db_connection.close()


@app.route("/feedback", methods=["GET"])
def feedback():
    feedback_data = chatbot.provide_feedback()
    return jsonify(feedback_data)

@app.route("/")
def home():
    print("Home route accessed.")  # Debugging log
    show_initialize = request.args.get('show_initialize', 'false').lower() == 'true'

    if show_initialize:
        print("Forcing initialize container to show due to query parameter.")  # Debugging log
        return render_template("index.html", show_initialize=True)

    if 'chatbot' not in globals() or chatbot is None:
        print("Chatbot not initialized. Showing initialize container.")  # Debugging log
        return render_template("index.html", show_initialize=True)

    session_id = session.get('session_id')
    if session_id:
        print(f"Active session found: {session_id}")  # Debugging log
        return render_template("index.html", show_initialize=False, session_id=session_id)
    else:
        print("No active session. Showing initialize container.")  # Debugging log
        return render_template("index.html", show_initialize=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
