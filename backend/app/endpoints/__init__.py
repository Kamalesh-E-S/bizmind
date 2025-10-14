from .auth_endpoints import auth_bp
from .competitor_endpoints import competitor_bp
from .heatmap_endpoints import heatmap_bp
from .strategy_endpoints import strategy_bp
from .report_endpoints import report_bp
from .landmark_endpoints import landmark_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(competitor_bp)
    app.register_blueprint(heatmap_bp)
    app.register_blueprint(strategy_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(landmark_bp)
