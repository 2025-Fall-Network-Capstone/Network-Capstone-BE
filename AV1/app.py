from flask import Flask
from routes.av1_routes import av1_bp

def create_app():
  app = Flask(__name__)
  app.register_blueprint(av1_bp)
  return app

if __name__ == "__main__":
  from config import HOST, PORT
  app = create_app()
  app.run(host=HOST, prot = PORT)