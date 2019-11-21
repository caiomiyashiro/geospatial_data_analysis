FROM python:3.6.5

RUN apt-get update
RUN apt-get install cmake make -y
RUN apt-get install python3-rtree -y #libspatialindex_c for geopandas
#RUN apt-get install -y build-essential libatlas-base-dev
#RUN apt-get install gcc
#RUN apt-get install -y libav-tools

WORKDIR /amld_geo

COPY requirements.txt /amld_geo/.

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY AMLD_2020.ipynb /amld_geo/AMLD_2020.ipynb

#COPY data/sample_100000.csv /amld_geo/data/sample_100000.csv
#COPY data/temp_routes_test.pickle /amld_geo/data/temp_routes_test.pickle
#COPY data/temp_routes_train.pickle /amld_geo/data/temp_routes_train.pickle

COPY images/ /amld_geo/images

COPY utils/conversor.py /amld_geo/utils/conversor.py
COPY utils/lines.py /amld_geo/utils/lines.py
COPY utils/OSRMFramework.py /amld_geo/utils/OSRMFramework.py
COPY utils/RouteAnnotator.py /amld_geo/utils/RouteAnnotator.py

EXPOSE 8888

CMD jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
