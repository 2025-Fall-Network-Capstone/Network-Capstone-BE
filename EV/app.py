from flask import Flask
from routes.ev_routes import ev_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(ev_bp)
    return app

if __name__ == "__main__":
    from config import HOST, PORT
    app = create_app()
    app.run(host=HOST, port=PORT)
