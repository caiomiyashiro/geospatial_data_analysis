setup:
	docker build . -t art_maps
	docker run -p 8888:8888 -d -v "$(PWD)":/workshop --name art_maps art_maps

.PHONY: get-url
get-url:
	@docker logs art_maps >& logs
	@cat logs | grep "127." | sed -n 2p
	@rm -rf logs

clean:
	docker stop art_maps
	docker rm art_maps
	# docker rmi art_maps_image
