# Creating your own stylised maps with Python

Link: [https://www.meetup.com/en-AU/PyBerlin/events/270339471/](https://www.meetup.com/en-AU/PyBerlin/events/270339471/)  

Slides: [https://docs.google.com/presentation/d/1xlHcy__2pKnFw9hg6betR5WrlMQQ7VU_GCuIDN6gopQ/edit#slide=id.p](https://docs.google.com/presentation/d/1xlHcy__2pKnFw9hg6betR5WrlMQQ7VU_GCuIDN6gopQ/edit#slide=id.p)  

## Talk summary
Let's take an overview of some common daily data processing on geospatial data and
use it as a gift idea. An alcoholic drink place recommender inside a city.

![png](PyBerlin_20_05_2020/Berlin.png)  

Some briefly touched techniques:

- What is geospatial data
- Geopandas
- Geometry operations - buffer and intersection
- Open Street Maps and street networks with OSMNx

---
## Execution Requirements
- make sure you have `make` build system  
  - Linux and Mac should have it by default  
  - Windows - Check [installer](http://gnuwin32.sourceforge.net/packages/make.htm). Windows users usually have some more difficulties (sorry!). In any case, check dockerfile for installed python packages and extra utilitaries.  
- make sure you have `docker` with **minimum 4Gb allocated to containers**. Check [here](https://stackoverflow.com/questions/44533319/how-to-assign-more-memory-to-docker-container) for an example.  
---  

## Workshop Setup

1. in your terminal, from the `art_heat_maps`, run: `make setup`
2. at the end of the process, type `make get-url`. You'll see a link similar (not equal) to the one below

`http://127.0.0.1:8888/?token=8a9ce1b6213dc455003b2ccdc79028a00b660b7666f9841b`  

3. copy and paste the link into your browser and you'll have access to the notebook.
4. to uninstall everything (after the workshop), run `make clean`
