from os import environ, getcwd
from sqlalchemy import create_engine
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_openapi3.models import SecurityScheme
from blueprints import payment_blueprint
from middlewares import checkJwt
from models import bind_engine, Base
from telemetry import initTelemetry
info = Info(title="Payment Store API", version="1.0.0")
security_schemes = {"bearerAuth": SecurityScheme(type="http", scheme="bearer", bearerFormat="JWT")}
app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

app.register_api(payment_blueprint)

@app.after_request
def applyCORS(response):
    response.headers.add('Accept', '*/*')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    return response

if __name__ == "__main__":
    isDev: bool = environ.get('ENV', "production") == 'development'
    db_url = environ.get("DB_URL") or "sqlite:///" + getcwd() + "/db/" + environ.get("DB_NAME", "payment") + ".db"
    engine = create_engine(db_url, echo=isDev, pool_pre_ping=True)
    bind_engine(engine=engine)
    Base.metadata.create_all(engine)
    initTelemetry(app=app, engine=engine)
    # Registered after initTelemetry on purpose: Flask runs before_request
    # handlers in registration order, and the telemetry one starts the server
    # span — the JWT middleware must run after it so its call to the auth
    # service joins the request trace instead of starting a new one.
    app.before_request(checkJwt)
    secretKey: str = environ.get('SECRET', "MY_SECRET_KEY")
    app.secret_key = secretKey.encode("utf-8")
    app.run(debug=isDev, port=int(environ.get("PORT", "8002")), host="0.0.0.0")
