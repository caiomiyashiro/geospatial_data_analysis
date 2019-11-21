#!/env/sh

if [ ! -f "new-york-latest.osm.pbf" ]; then
  wget http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf
else
  echo "File exists!"
fi
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/new-york-latest.osm.pbf
