# Shopping Cart API

This is a simple shopping cart API that allows managing carts.
The product is retrieved from the (fakestore api)[https://fakestoreapi.com/].

## Setup

### Docker

The easiest way to run the application is using Docker. Make sure you have Docker installed on your system.

1. Build the Docker image:
2. Run Docker image

There is a makefile on the root to enable easy run with docker. 
If you have make available and docker you should get it running with the command `make run` (it will build and run the docker image exposing the project on port 8000 to the host)

## API Documentation

The API provides OpenAPI/Swagger documentation at the `/openapi` endpoint when running.

### Cart Endpoints
- GET:/cart
- GET:/cart/summary
- POST:/product/:prod_id
- DELETE /product/:cart_prod_entry_id
