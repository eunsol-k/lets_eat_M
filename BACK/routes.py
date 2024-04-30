from controllers.controllers import ex_bp

def routes_list(app):
    app.register_blueprint(ex_bp)
    return app