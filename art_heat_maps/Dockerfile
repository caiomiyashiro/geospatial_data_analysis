FROM python:3.7.4

RUN apt-get update && apt-get install -y --no-install-recommends python3-rtree \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workshop

COPY requirements.txt /workshop/.

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8888

CMD jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
