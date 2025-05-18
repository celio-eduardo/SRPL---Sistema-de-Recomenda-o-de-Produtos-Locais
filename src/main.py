import os
import sys
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template
from src.routes.main import main_bp, carregar_dados_iniciais

def create_app():
    app = Flask(__name__)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    
    # Carregar dados iniciais
    carregar_dados_iniciais()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
