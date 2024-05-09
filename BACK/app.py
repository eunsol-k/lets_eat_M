import os
import logging
import logging.handlers
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from configs.config import config
from redis import StrictRedis
from flask_restx import Api

jwt = JWTManager()
logger = logging.getLogger("myLogger")
rc = StrictRedis(host='redis', port=6379, db=0)

bp_api = Blueprint(
    name="api",
    import_name=__name__,
    url_prefix="/api/v1"
)

authorizations = {
    'bearer_auth': {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

api = Api(
    version='0.1',
    title='알약 알고 먹어요 API Server',
    description='‘알약 알고 먹어요’ API 서버의 문서입니다.',
    terms_url="/",
    contact='solsol1203@gmail.com',
    license='MIT',
    authorizations=authorizations
)

def register_router(app: Flask):
    from apis.v1.auth import Auth
    from apis.v1.mypage import MyPage

    api.add_namespace(Auth, '/auth')
    api.add_namespace(MyPage, '/mypage')

def create_app():
    app = Flask(__name__)
    app.config.from_object(obj=config['development'])
    app.register_blueprint(blueprint=bp_api)
    
    # JWT
    jwt.init_app(app=app)

    # REST-X
    api.init_app(app=app)

    register_router(app=app)

    # logging.getLogger("werkzeug").disabled = True
    # logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(remote_addr)s] \"%(method)s %(url)s %(version)s\" : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if not os.path.isdir(s=app.config.get("LOG_DIR")):
        os.mkdir(path=app.config.get("LOG_DIR"))

    log_path = os.path.join(app.config.get("LOG_DIR"), app.config.get("LOG_FILE"))
    # handler = logging.FileHandler(filename=log_path, mode="a", encoding="utf-8")
    handler = logging.handlers.RotatingFileHandler(filename=log_path, mode="a", encoding="utf-8", maxBytes=200, backupCount=3)
    handler.setFormatter(fmt=logging.Formatter('[%(asctime)s] [%(levelname)s] [%(remote_addr)s] \"%(method)s %(url)s %(version)s\" : %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return app


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    """
    사용된 액세스 토큰(access_token)의 재사용을 방지합니다.
    """

    if not jwt_payload and "jti" not in jwt_payload:
        return None

    jti = jwt_payload.get("jti")
    token = rc.get(name=jti)

    return token is not None