setup:
	docker build . -t amld_geo
	docker run -p 8888:8888 -d --name workshop amld_geo 

.PHONY: get-url
get-url:
	@docker logs workshop >& logs
	@cat logs | grep "127." | sed -n 2p
	@rm -rf logs

clean:
	docker stop workshop
	docker rm workshop
	docker rmi amld_geo
