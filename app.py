from flask import Flask
from routes import register_face, login_face  # Import routes

app = Flask(__name__)  # Initialize Flask app

# Register routes here
app.register_blueprint(register_face)
app.register_blueprint(login_face)

if __name__ == '__main__':
    app.run(debug=True)
