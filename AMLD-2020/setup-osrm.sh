#!/env/sh

if [ ! -f "router/new-york-latest.osm.pbf" ]; then
  mkdir router
  wget http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf -O router/new-york-latest.osm.pbf
else
  echo "File exists!"
fi
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/router/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/router/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/router/new-york-latest.osm.pbf
