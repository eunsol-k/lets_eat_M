from controllers.controllers import rt_bp

def routes_list(app):
    app.register_blueprint(rt_bp)
    return app