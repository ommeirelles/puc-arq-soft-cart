from os import environ, getcwd
from pydantic import BaseModel
from sqlalchemy import create_engine
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from blueprints import product_blueprint, cart_blueprint
from models import bind_engine, Base
info = Info(title="Cart Store API", version="1.0.0")
app = OpenAPI(__name__, info=info)

app.register_api(product_blueprint)
app.register_api(cart_blueprint)

@app.after_request
def applyCORS(response):
    response.headers.add('Accept', '*/*')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    return response

if __name__ == "__main__":
    isDev: bool = environ.get('ENV', "production") == 'development'
    db_url = "sqlite:///" + getcwd() + "/db/" + environ.get("DB_NAME", "cart") + ".db"
    engine = create_engine(db_url, echo=isDev)
    bind_engine(engine=engine)
    Base.metadata.create_all(engine)
    secretKey: str = environ.get('SECRET', "MY_SECRET_KEY")
    app.secret_key = secretKey.encode("utf-8")
    app.run(debug=isDev, port=int(environ.get("PORT", "8000")), host="0.0.0.0")