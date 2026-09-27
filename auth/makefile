port := 8001
imageName := arq-soft-auth
containerName := arq-soft-auth
dbName := auth
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
		-e SECRET=$(secret) $(imageName)

dev: build
	docker run --name $(containerName) --rm -p $(port):$(port) \
		-v ./src:/app/src -v ./db:/app/db \
		-e ENV=development -e DB_NAME=$(dbName) -e PORT=$(port) \
		-e SECRET=$(secret) $(imageName)

stop:
	- docker stop $(containerName)
	- docker rm $(containerName)
