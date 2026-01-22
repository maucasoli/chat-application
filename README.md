# Open Chat

A modern, secure, and real-time chat application built with Python (Flask) and WebSockets (Socket.IO).

![Chat page](https://github.com/maucasoli/chat-application/blob/main/docs/chat.png "Chat page")

## 🚀 Features

- **Real-time Messaging**: Instant communication using WebSockets.
- **Security**: bcrypt password hashing and secure session management.
- **File Sharing**: Upload and share images and files directly in the chat.
- **User Management**: Registration, Login, and Password Change functionality.

## 🛠️ Technologies

- **Backend**: Python, Flask, Flask-SocketIO, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Flask-Bcrypt

## 📦 Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/maucasoli/open-chat.git
    cd open-chat
    ```

2.  **Create a virtual environment (Recommended)**

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory (copy from `.env.example`):
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and set your `SECRET_KEY`. You can also configure the `PORT` (default is 5000).

## ▶️ Usage

1.  **Run the Application**

    ```bash
    python app.py
    ```

2.  **Access the App**
    Open your browser and navigate to `http://localhost:5000` (or your configured port).

3.  **Create a User**
    - Click on "Create Account" on the login screen.
    - Or run the CLI helper: `python add_user.py`

## 📁 Project Structure

```
open-chat/
├── app.py              # Main application entry point
├── database.py         # Database models and connection logic
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── static/
│   ├── styles.css      # Modern CSS styles
│   └── images/         # Static assets
├── templates/
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── open_chat.html  # Main chat interface
│   └── modify.html     # User settings page
└── uploads/            # Directory for uploaded files
```
