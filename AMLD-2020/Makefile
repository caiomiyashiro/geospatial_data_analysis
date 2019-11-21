setup:
	# init osmr data
	sh setup-osrm.sh
up: 
	docker-compose up --build

down:
	docker-compose down

.PHONY: get-url
get-url:
	@docker logs jupyter-image >& logs
	@cat logs | grep "127." | sed -n 2p
	@rm -rf logs

clean:
	docker-compose down
	docker rm jupyter-image
	docker rm osrm/osrm-backend
	rm new-york-latest.osm.pbf
