FROM python:3.6.5

RUN apt-get update && apt-get install -y --no-install-recommends cmake make python3-rtree \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /amld_geo

COPY requirements.txt /amld_geo/.

RUN pip install --upgrade pip && pip install  -r requirements.txt

COPY Complete_AMLD_2020.ipynb \
     Presentation_AMLD_2020.ipynb /amld_geo/

COPY data/taxi_fare_sample_100000.csv \
     data/temp_routes_test.pickle \
     data/temp_routes_train.pickle \
     data/new_york_city.osm.pbf \
     data/AMLD_lookups.pickle /amld_geo/data/

COPY images/ /amld_geo/images

COPY utils/conversor.py \
     utils/plot_geometry.py \
     utils/OSRMFramework.py \
     utils/RouteAnnotator.py /amld_geo/utils/

ENV IS_DOCKER Yes

EXPOSE 8888

CMD jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
