port = 8000
imageName = "arq-soft-cart"
dbName = "cart"
prodAPi="https://fakestoreapi.com/"
secret="SSS"

db:
	if [ ! -f ./db/$(DB_NAME).db ]; then touch ./db/$(DB_NAME).db fi
	sqlite3 ./db/$(DB_NAME).db "select 1"


build:
	- docker stop $(imageName)
	- docker rm $(imageName)
	docker build -t $(imageName) .

run: db build
	docker run -v ./db:/app/db \
--rm -p $(port):$(port) \
-e ENV=development -e DB_NAME=$(dbName) \
-e PORT=$(port) -e PRODUCT_API_URL=$(prodAPi) -e SECRET=$(secret) $(imageName)

dev: db
	- docker compose down --rmi all -v --remove-orphans
	ENV=development docker compose up --build --watch