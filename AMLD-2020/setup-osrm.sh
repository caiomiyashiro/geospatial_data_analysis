#!/env/sh

if [ ! -f "router/new_york_city.osm.pbf" ]; then
  mkdir router
  echo "Downloading file router/new-york-latest.osm.pbf..."
  wget https://amldspatial.s3.eu-central-1.amazonaws.com/new_york_city.osm.pbf -O router/new_york_city.osm.pbf
  cp router/new_york_city.osm.pbf data/new_york_city.osm.pbf
else
  echo "File router/new-york-latest.osm.pbf exists!"
fi

if [ ! -f "data/temp_routes_train.pickle" ]; then
  echo "Downloading file data/temp_routes_train.pickle..."
  wget https://amldspatial.s3.eu-central-1.amazonaws.com/temp_routes_train.pickle -O data/temp_routes_train.pickle
else
  echo "File data/temp_routes_train.pickle exists!"
fi

if [ ! -f "data/temp_routes_test.pickle" ]; then
  echo "Downloading file data/temp_routes_test.pickle..."
  wget https://amldspatial.s3.eu-central-1.amazonaws.com/temp_routes_test.pickle -O data/temp_routes_test.pickle
else
  echo "File data/temp_routes_test.pickle exists!"
fi

if [ ! -f "data/AMLD_lookups.pickle" ]; then
  echo "Downloading file data/AMLD_lookups.pickle..."
  wget https://amldspatial.s3.eu-central-1.amazonaws.com/AMLD_lookups.pickle -O data/AMLD_lookups.pickle
else
  echo "File data/AMLD_lookups.pickle exists!"
fi

docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/router/new_york_city.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/router/new_york_city.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/router/new_york_city.osm.pbf
