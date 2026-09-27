# Back-end APIs — Cart, Auth & Payment

Back-end microservices of the online shopping MVP developed for the Software
Architecture post-graduation course (PUC). The services are built with Flask
and [flask-openapi3](https://luolingchun.github.io/flask-openapi3/) and persist
data through SQLAlchemy 2 — PostgreSQL when running the full stack via
Docker Compose, SQLite as a local fallback. The cart service integrates with
the external [Fake Store API](https://fakestoreapi.com/) and the payment
service with the public [ViaCEP API](https://viacep.com.br/).

| Service | Folder | Port | Domain |
| ------- | ------ | ---- | ------ |
| Cart API | [`./cart`](./cart) | `8000` | Shopping carts: create, add/remove products, summaries with prices |
| Auth API | [`./auth`](./auth) | `8001` | Authentication: user registration, JWT login, token validation |
| Payment API | [`./payment`](./payment) | `8002` | Payments: pays a cart with card data and a CEP-validated delivery address |

## Stack

- **Python 3.13** + **Flask 3** + **flask-openapi3** (OpenAPI/Swagger docs)
- **SQLAlchemy 2** for persistence — **PostgreSQL** (`psycopg` driver) in the
  compose stack, **SQLite** as the local fallback
- **Pydantic** for request/response schemas
- **requests** as the HTTP client for the external APIs (cart → Fake Store,
  payment → ViaCEP and the cart API)
- **PyJWT** (auth only) to sign and validate JWT session tokens
- **Werkzeug** (auth only) for password hashing

## Architecture Overview

The services follow a microservice architecture: they are consumed by the
[front-end SPA](https://github.com/ommeirelles/puc-arq-software-front). The
cart service communicates with the Fake Store API to resolve product details
and prices, the auth service is fully self-contained (it owns its user
database and issues self-signed JWT session tokens), and the payment service
validates the delivery CEP against the public ViaCEP API and fetches the cart
total from the cart API before registering the payment.

```mermaid
flowchart LR
    User([User]) --> FE["Front-end SPA<br/>React + Vite · :4173"]
    FE -->|"GET /products"| FSA["Fake Store API<br/>fakestoreapi.com"]
    FE -->|"Cart operations<br/>(create, add, remove, summary)"| LB["nginx load balancer<br/>:8000 (cart) · :8001 (auth) · :8002 (payment)"]
    FE -->|"POST /user · POST /login<br/>GET /user"| LB
    FE -->|"POST /pay/&lt;cart_guid&gt;"| LB
    LB -->|"round-robin"| CART["Cart API ×3 replicas<br/>Flask · :8000"]
    LB -->|"round-robin"| AUTH["Auth API ×3 replicas<br/>Flask · :8001"]
    LB -->|"round-robin"| PAY["Payment API ×3 replicas<br/>Flask · :8002"]
    CART -->|"Product details & prices"| FSA
    CART -->|"JWT validation"| AUTH
    PAY -->|"JWT validation"| AUTH
    PAY -->|"GET /cart/summary"| CART
    PAY -->|"CEP lookup"| VIA["ViaCEP API<br/>viacep.com.br"]
    CART --> CARTDB[("PostgreSQL<br/>soft-arq-cart-db · :5432")]
    AUTH --> AUTHDB[("PostgreSQL<br/>soft-arq-auth-db · :5432")]
    PAY --> PAYDB[("PostgreSQL<br/>soft-arq-payment-db · :5432")]
```

> **Design choice — horizontal scaling:** in the compose stack each service
> runs **3 replicas** (`deploy.replicas`) behind an **nginx load balancer**
> (`soft-arq-lb`) that round-robins requests across them while publishing the
> same host ports (`8000` / `8001` / `8002`), so clients need no changes. This
> is only possible because the services are stateless — sessions are
> self-signed JWTs validated cryptographically, and carts are identified by
> GUID — so any replica can serve any request.

> **Design choice — one database per service:** each service owns a dedicated
> PostgreSQL container (`soft-arq-cart-db` for the cart API, `soft-arq-auth-db`
> for the auth API, `soft-arq-payment-db` for the payment API), provisioned by
> the compose file at the
> [front-end repository](https://github.com/ommeirelles/puc-arq-software-front).
> Keeping the databases isolated lets each service scale horizontally and
> independently — no shared database, no cross-service coupling at the data
> layer. The services connect through the `DB_URL` environment variable; when
> it is not set they fall back to a local SQLite file (named from `DB_NAME`,
> under `./db/`), which keeps the standalone `make run` / `make dev` and local
> `python src/main.py` flows working without extra infrastructure.

The auth service manages sessions with stateless JWTs: on login it validates
the credentials against the local `users` table (passwords stored as Werkzeug
hashes) and returns a token signed with the service `SECRET`, carrying the
user id in the `sub` claim and expiring after `TOKEN_TTL_SECONDS`. Token
validation is purely cryptographic — logout is handled client-side by
discarding the token.

Key implementation points (shared by the services):

- Entry point: `src/main.py` — builds the `OpenAPI` app, registers blueprints,
  applies permissive CORS headers, and initializes the database.
- Routes are organized as blueprints in `src/blueprints/`
  (`cart.py` + `product.py` in the cart API, `auth.py` in the auth API,
  `payment.py` in the payment API).
- Business logic lives in `src/services/`; SQLAlchemy models in `src/models/`;
  Pydantic request/response schemas in `src/schemas/`.
- The database connection string comes from the `DB_URL` env var; when unset,
  a SQLite file is created under `./db/` and named from the `DB_NAME` env var
  (`cart` / `auth` / `payment`).
- The cart and payment APIs guard their endpoints with a `before_request`
  middleware (`src/middlewares/auth.py`) that validates the bearer JWT against
  the auth service (`GET {AUTH_API_URL}user`), rejecting requests with `401`
  when the token is missing or invalid.

## API Documentation

The APIs provide interactive OpenAPI/Swagger documentation at the `/openapi`
endpoint when running.

### Cart API Endpoints

All cart endpoints require an `Authorization: Bearer <JWT>` header issued by the
auth service (validated by a `before_request` middleware in
`cart/src/middlewares/auth.py`); requests without a valid token are rejected with
`401`.

| Method   | Path                   | Description                                                        |
| -------- | ---------------------- | ------------------------------------------------------------------ |
| `GET`    | `/cart`                | Creates a new cart; returns `{id, guid, deleted}`.                 |
| `GET`    | `/cart/summary?guid=`  | Cart summary: items grouped by product (`product_id` + `quantity`) plus total price. |
| `POST`   | `/product/<product_id>`| Adds a product to a cart (`cart_guid`, `quantity` query params).   |
| `DELETE` | `/product/<product_id>`| Removes units of a product from the cart (`cart_guid` query param; optional `quantity` — removes all units when omitted). |
| `POST`   | `/internal/cart/<guid>/close` | **Internal route** — closes a cart, marking it stale and unusable (`deleted = true`); called by the payment API after an approved payment. Routes under the `/internal/` prefix are blocked at the nginx load balancer (`404`) on every service, so they are only reachable container-to-container inside the docker network. |

### Auth API Endpoints

| Method | Path     | Description                                                            |
| ------ | -------- | ---------------------------------------------------------------------- |
| `POST` | `/user`  | Registers a new user `{name, email, password}` (all required, valid email format); returns `{id, name, email}`. Responds `409` when the email is already registered, `422` on invalid payloads. |
| `POST` | `/login` | Authenticates `{email, password}`; returns a signed JWT `{token}`.     |
| `GET`  | `/user`  | Validates the `Authorization: Bearer` JWT; returns the user info.      |

### Payment API Endpoints

All payment endpoints require an `Authorization: Bearer <JWT>` header issued by
the auth service (validated by a `before_request` middleware in
`payment/src/middlewares/auth.py`); requests without a valid token are rejected
with `401`.

| Method | Path                | Description                                                  |
| ------ | ------------------- | ------------------------------------------------------------ |
| `POST` | `/pay/<cart_guid>`  | Pays a cart. Validates the token and that the cart exists (via the cart API summary), validates the delivery CEP against the ViaCEP API (cross-checking city/state), then registers the payment attempt. After an **approved** payment the cart is closed through the cart API's internal close route, making it stale and unusable; a declined payment leaves the cart open for a retry. |

Request body:

```json
{
  "card_number": "4111 1111 1111 1111",
  "card_expiry": "12/30",
  "card_cvv": "123",
  "address": {
    "cep": "01001-000",
    "street": "Praça da Sé",
    "number": "100",
    "neighborhood": "Sé",
    "city": "São Paulo",
    "state": "SP"
  }
}
```

- `card_number` — 13 to 19 digits (spaces allowed); validated with the Luhn
  algorithm. A valid-format number that fails Luhn registers a `declined`
  payment (`402`); a passing one registers an `approved` payment (`201`).
- `card_expiry` — `MM/YY` or `MM/YYYY`, must not be in the past.
- `card_cvv` — 3 or 4 digits.
- `address.cep` — brazilian CEP (8 digits, dash optional), looked up in the
  ViaCEP API; `address.city` and `address.state` must match the CEP data.

Responses: `201` approved / `402` declined (both return the registered payment
with `card_brand` and `card_last4`), `400` cart not found, empty cart, CEP not
found or address mismatch, `401` missing/invalid token, `409` cart already
paid, `422` invalid payload, `502` ViaCEP unavailable.

> **Security — no sensitive card data at rest:** following common payment
> security rules, the full card number, the expiry date and the security code
> are never persisted — the `payments` table stores only the card brand and
> the last 4 digits, alongside the delivery address and the amount.

## Environment Variables

### Cart API

| Variable          | Default                      | Purpose                                   |
| ----------------- | ---------------------------- | ----------------------------------------- |
| `PORT`            | `8000`                       | HTTP port exposed to the host             |
| `SECRET`          | `MY_SECRET_KEY`              | Flask secret key                          |
| `DB_URL`          | *(none — SQLite fallback)*   | SQLAlchemy connection string; set by the compose file to `postgresql+psycopg://cart:cart@soft-arq-cart-db:5432/cart`. When unset, falls back to SQLite |
| `DB_NAME`         | `cart`                       | SQLite database file name (under `./db`), used only when `DB_URL` is unset |
| `ENV`             | `production`                 | `development` enables debug/SQL echo      |
| `PRODUCT_API_URL` | *(none — required)*          | External product API base URL; set by the makefile / compose file to `https://fakestoreapi.com/` |
| `AUTH_API_URL`    | *(none — required)*          | Auth API base URL used by the JWT middleware; set by the compose file to `http://soft-arq-auth:8001/` and by the makefile to `http://host.docker.internal:8001/` |
| `OTEL_SERVICE_NAME` | `puc-arq-soft-cart`        | Service name reported in telemetry        |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc`       | OTLP exporter protocol (`grpc` or `http/protobuf`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` (`grpc`) or `http://localhost:4318` (`http/protobuf`) | OTLP collector endpoint |

### Auth API

| Variable            | Default                      | Purpose                                   |
| ------------------- | ---------------------------- | ----------------------------------------- |
| `PORT`              | `8001`                       | HTTP port exposed to the host             |
| `SECRET`            | `MY_SECRET_KEY`              | Flask secret key / JWT signing key        |
| `DB_URL`            | *(none — SQLite fallback)*   | SQLAlchemy connection string; set by the compose file to `postgresql+psycopg://auth:auth@soft-arq-auth-db:5432/auth`. When unset, falls back to SQLite |
| `DB_NAME`           | `auth`                       | SQLite database file name (under `./db`), used only when `DB_URL` is unset |
| `ENV`               | `production`                 | `development` enables debug/SQL echo      |
| `TOKEN_TTL_SECONDS` | `3600`                       | How long a JWT session token stays valid  |
| `OTEL_SERVICE_NAME` | `puc-arq-soft-auth`          | Service name reported in telemetry        |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc`         | OTLP exporter protocol (`grpc` or `http/protobuf`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` (`grpc`) or `http://localhost:4318` (`http/protobuf`) | OTLP collector endpoint |

### Payment API

| Variable          | Default                      | Purpose                                   |
| ----------------- | ---------------------------- | ----------------------------------------- |
| `PORT`            | `8002`                       | HTTP port exposed to the host             |
| `SECRET`          | `MY_SECRET_KEY`              | Flask secret key                          |
| `DB_URL`          | *(none — SQLite fallback)*   | SQLAlchemy connection string; set by the compose file to `postgresql+psycopg://payment:payment@soft-arq-payment-db:5432/payment`. When unset, falls back to SQLite |
| `DB_NAME`         | `payment`                    | SQLite database file name (under `./db`), used only when `DB_URL` is unset |
| `ENV`             | `production`                 | `development` enables debug/SQL echo      |
| `CART_API_URL`    | *(none — required)*          | Cart API base URL used to fetch the cart summary; set by the compose file to `http://soft-arq-cart:8000/` and by the makefile to `http://host.docker.internal:8000/` |
| `AUTH_API_URL`    | *(none — required)*          | Auth API base URL used by the JWT middleware; set by the compose file to `http://soft-arq-auth:8001/` and by the makefile to `http://host.docker.internal:8001/` |
| `VIA_CEP_API_URL` | `https://viacep.com.br`      | ViaCEP API base URL used to validate delivery CEPs |
| `OTEL_SERVICE_NAME` | `puc-arq-soft-payment`     | Service name reported in telemetry        |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc`       | OTLP exporter protocol (`grpc` or `http/protobuf`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` (`grpc`) or `http://localhost:4318` (`http/protobuf`) | OTLP collector endpoint |

## Running

Each service has its own `Dockerfile` and `Makefile` inside its folder — run
the commands below from `./cart`, `./auth` or `./payment`.

### Docker

The easiest way to run each application is using Docker. Make sure you have
Docker installed on your system.

There is a Makefile on each service's root to enable easy runs with Docker. If
you have `make` and Docker available, you should get it running with:

- `make run` — builds and runs the Docker image, exposing the API on its port
  (**8000** for cart, **8001** for auth, **8002** for payment) to the host
  (with the `./db` folder mounted for persistence).
- `make dev` — runs the same image with `./src` and `./db` mounted and
  `ENV=development`, so Flask reloads on each code change.
- `make stop` — stops and removes the container.

*It's also possible to run without make:*

- Cart: `docker build -t arq-soft-cart .` then
  `docker run --rm -p 8000:8000 -v ./db:/app/db -e PRODUCT_API_URL=https://fakestoreapi.com/ arq-soft-cart`
- Auth: `docker build -t arq-soft-auth .` then
  `docker run --rm -p 8001:8001 -v ./db:/app/db arq-soft-auth`
- Payment: `docker build -t arq-soft-payment .` then
  `docker run --rm -p 8002:8002 -v ./db:/app/db -e CART_API_URL=http://host.docker.internal:8000/ -e AUTH_API_URL=http://host.docker.internal:8001/ arq-soft-payment`

> Docker is used through the Podman compatibility layer.

> To run the **full stack** (3 replicas per API behind the nginx load
> balancer, one PostgreSQL container per service, the front-end, OTEL
> collector and Jaeger), use the `docker-compose.yml` at the root of the
> [front-end repository](https://github.com/ommeirelles/puc-arq-software-front):
> `docker-compose up --build --watch`.

### Locally

Prerequisites:

- Python 3.13

Steps (per service, from its folder):

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python src/main.py`
4. Open `http://localhost:8000/openapi` (cart),
   `http://localhost:8001/openapi` (auth) or
   `http://localhost:8002/openapi` (payment) for the interactive API docs
