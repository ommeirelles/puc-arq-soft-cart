from os import environ, getcwd
from sqlalchemy import create_engine
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_openapi3.models import SecurityScheme
from blueprints import auth_blueprint
from models import bind_engine, Base
from telemetry import initTelemetry
info = Info(title="Auth Store API", version="1.0.0")
security_schemes = {"bearerAuth": SecurityScheme(type="http", scheme="bearer", bearerFormat="JWT")}
app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

app.register_api(auth_blueprint)

@app.after_request
def applyCORS(response):
    response.headers.add('Accept', '*/*')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    return response

if __name__ == "__main__":
    isDev: bool = environ.get('ENV', "production") == 'development'
    db_url = environ.get("DB_URL") or "sqlite:///" + getcwd() + "/db/" + environ.get("DB_NAME", "auth") + ".db"
    engine = create_engine(db_url, echo=isDev, pool_pre_ping=True)
    bind_engine(engine=engine)
    Base.metadata.create_all(engine)
    initTelemetry(app=app, engine=engine)
    secretKey: str = environ.get('SECRET', "MY_SECRET_KEY")
    app.secret_key = secretKey.encode("utf-8")
    app.run(debug=isDev, port=int(environ.get("PORT", "8001")), host="0.0.0.0")
