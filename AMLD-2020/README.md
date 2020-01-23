# Feature Engineering for Spatial Data Analysis in the Context of Fare Prediction

Link: [https://appliedmldays.org/workshops/feature-engineering-for-spatial-data-analysis](https://appliedmldays.org/workshops/feature-engineering-for-spatial-data-analysis)

Duration of the workshop - 1 Day

## Workshop summary
In this workshop, participants will be able to understand what are the types of data processing they can do in order to extract better knowledge out of their spatial data. We will introduce tools for visualizing, extracting features and feature engineering and explain the logic and steps needed in order to create them. The techniques will be presented in the context of a simple machine learning model for predicting taxi tariffs and illustrate how we can improve it with these new features.

Participants will be able to learn:

- Visualise spatial data for exploratory data analysis
- Understand and calculate distances
- Extract routes, route distances and estimated durations
- Extract city features based on open source tools, e.g. Open Street Maps
- Data processing performance - Spatial indices in Python
- Ideas for traffic estimation
- Approaches and potentials for GPS analysis and how they can help you in terms of feature engineering.

---
## Execution Requirements
- make sure you have `make` build system and `wget` file download command
  - Linux and Mac should have it by default
  - Windows - Check [installer](http://gnuwin32.sourceforge.net/packages/make.htm). If you can't install these tools in your machine, please go through the `Manual Setup`.
- make sure you have `docker` with **minimum 2Gb allocated to containers**. Check [here](https://stackoverflow.com/questions/44533319/how-to-assign-more-memory-to-docker-container) for an example. Some linux users might also have to separately install docker-compose as well. See [here](https://stackoverflow.com/questions/36685980/docker-is-installed-but-docker-compose-is-not-why)
---
### Data Usage Licence and Download:

Because we're using a dataset from [Kaggle](https://www.kaggle.com/), you have to agree to it's terms of conditions in the [New York Taxi Fare Prediction Challenge](https://www.kaggle.com/c/new-york-city-taxi-fare-prediction).
1. Make an account at Kaggle platform and log in
2. Access the New York Taxi Fare Prediction Challenge and click "Late Submission"
3. Accept the terms of condition
4. Access [this link](https://www.kaggle.com/caiomiyashiro/ny-taxi-fare-sample-100000/download) while logged in to download the dataset and put it in the `data/` inside this project repository

### Workshop Setup

#### OPTION 1 - Automatic Setup  

1. in your terminal, from the AMLD project folder (`AMLD-2020`), run: `make setup`
2. after it's done, run `make up`
3. at the end of the process, you'll see a link similar (not equal) to the one below

`http://127.0.0.1:8888/?token=8a9ce1b6213dc455003b2ccdc79028a00b660b7666f9841b`  

4. copy and paste the link into your browser
5. to uninstall everything (after the workshop), run `make down`

#### OPTION 2 - Manual Setup
1. Download following links into `data` folder. Try to use a different browser than Google Chrome, as it tends to block pickle file downloads:
  - https://amldspatial.s3.eu-central-1.amazonaws.com/new_york_city.osm.pbf
  - https://amldspatial.s3.eu-central-1.amazonaws.com/temp_routes_train.pickle
  - https://amldspatial.s3.eu-central-1.amazonaws.com/temp_routes_test.pickle
  - https://amldspatial.s3.eu-central-1.amazonaws.com/AMLD_lookups.pickle
2. Create a `router` folder in the folder `AMLD-2020` and copy `data/new_york_city.osm.pbf` to it.
3. In your terminal at the root folder (`AMLD-2020`), execute the following commands:
  - docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/router/new_york_city.osm.pbf
  - docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/router/new_york_city.osm.pbf
  - docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/router/new_york_city.osm.pbf
4. In your terminal, at the root folder (`AMLD-2020`), execute `docker-compose up --build`
5. At the end of step 4., you'll see a link similar (not equal) to the one below:
`http://127.0.0.1:8888/?token=8a9ce1b6213dc455003b2ccdc79028a00b660b7666f9841b`. Copy and paste the link into your browser
6. After executing the project, close it by executing `docker-compose down`
