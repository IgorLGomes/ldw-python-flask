from flask import Flask
from controllers import routes
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='views')
# Prefer the secret key from .env for stable sessions across restarts
app.secret_key = os.getenv("FLASK_SECRET_KEY")
routes.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
