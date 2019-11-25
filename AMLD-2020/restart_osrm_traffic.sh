#!/env/sh

docker-compose stop osrm-router     # go to hibernate
docker-compose rm osrm-router       # shutdown the PC
docker-compose create osrm-router   # create the container from image and put it in hibernate

if [ $1 = 'normal' ]; then
  sudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/router/new_york_city.osm.pbf
else
  sudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/router/new_york_city.osm.pbf --segment-speed-file /data/data/test_traffic.csv
fi

docker-compose start osrm-router    #bring container to life from hibernation
