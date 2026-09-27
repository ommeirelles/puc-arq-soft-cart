port := 8000
imageName := arq-soft-cart
containerName := arq-soft-cart
dbName := cart
prodApi := https://fakestoreapi.com/
authApi := http://host.docker.internal:8001/
secret := SSS

.PHONY: build run dev stop

build:
	- docker stop $(containerName)
	- docker rm $(containerName)
	docker build -t $(imageName) .

run: build
	docker run --name $(containerName) --rm -p $(port):$(port) \
		-v ./db:/app/db \
		-e DB_NAME=$(dbName) -e PORT=$(port) \
		-e PRODUCT_API_URL=$(prodApi) -e AUTH_API_URL=$(authApi) \
		-e SECRET=$(secret) $(imageName)

dev: build
	docker run --name $(containerName) --rm -p $(port):$(port) \
		-v ./src:/app/src -v ./db:/app/db \
		-e ENV=development -e DB_NAME=$(dbName) -e PORT=$(port) \
		-e PRODUCT_API_URL=$(prodApi) -e AUTH_API_URL=$(authApi) \
		-e SECRET=$(secret) $(imageName)

stop:
	- docker stop $(containerName)
	- docker rm $(containerName)
