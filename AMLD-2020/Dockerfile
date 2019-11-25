FROM python:3.6.5

RUN apt-get update && apt-get install -y --no-install-recommends cmake make python3-rtree \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /amld_geo

COPY requirements.txt /amld_geo/.

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY AMLD_2020.ipynb /amld_geo/AMLD_2020.ipynb

COPY data/taxi_fare_sample_100000.csv /amld_geo/data/taxi_fare_sample_100000.csv
COPY data/temp_routes_test.pickle /amld_geo/data/temp_routes_test.pickle
COPY data/temp_routes_train.pickle /amld_geo/data/temp_routes_train.pickle

COPY images/ /amld_geo/images

COPY utils/conversor.py /amld_geo/utils/conversor.py
COPY utils/plot_geometry.py /amld_geo/utils/plot_geometry.py
COPY utils/OSRMFramework.py /amld_geo/utils/OSRMFramework.py
COPY utils/RouteAnnotator.py /amld_geo/utils/RouteAnnotator.py

COPY router/new_york_city.osm.pbf /amld_geo/router/new_york_city.osm.pbf

EXPOSE 8888

CMD jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
