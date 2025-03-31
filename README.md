# SpeakEasy-ChatBot

This project is a **SpeakEasy-ChatBot** designed to help users practice and improve their language skills. The chatbot leverages Google Translator for translations and provides feedback on user inputs.

## Features

- **Language Translation**: Supports multiple languages using Google Translator.
- **Chat History**: Stores and displays chat history grouped by sessions.
- **Feedback Mechanism**: Provides feedback on mistakes and tips for improvement.
- **Session Management**: Allows users to start new chat sessions.
- **Interactive UI**: User-friendly interface with dynamic chat features.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Translation API**: Google Translator

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd project_assigment
   ```

2. **Install Dependencies**:
   Ensure you have Python installed. Then, install the required Python packages:
   ```bash
   pip install flask googletrans==4.0.0-rc1
   ```

3. **Run the Application**:
   Start the Flask server:
   ```bash
   python main.py
   ```
add all 
4. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage

1. **Initialize the Chatbot**:
   - Enter the target language, current language, and proficiency level.
   - Click "Start Chatbot" to begin.

2. **Chat with the Bot**:
   - Type your message in the input box and click the send button.
   - The bot will respond with translations and feedback.

3. **View Chat History**:
   - The sidebar displays a list of previous chat sessions.
   - Click on a session to view its chat history.

4. **Start a New Chat**:
   - Click the "New Chat" button to begin a new session.

## File Structure

- **`main.py`**: Backend logic and Flask routes.
- **`templates/index.html`**: Frontend HTML structure.
- **`static/styles.css`**: Styling for the application.
- **`user_progress.db`**: SQLite database for storing chat history and feedback.

## Notes

- Ensure you have an active internet connection for Google Translator to work.
- The application uses session management to track user interactions.

## Future Enhancements

- Add support for voice input and output.
- Implement advanced mistake detection and correction.
- Integrate more language learning resources.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
