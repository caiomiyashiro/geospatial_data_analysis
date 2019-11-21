setup:
	# init osmr data
	sh setup-osrm.sh
up:
	docker-compose up --build

down:
	docker-compose down

clean:
	docker-compose down
	docker rm jupyter-image
	docker rm osrm/osrm-backend
	rm new-york-latest.osm.pbf
