# ÚKOL 3

## Popis
Využití přechozího kódu - snazání plotu grafů a zanechání ukladaní do CSV

## Struktura projektu
- mariadb/ - Dockerfile pro MariaDB kontejner
- python_app/ - Dockerfile a app.py pro Python kontejner
- docker-compose.yaml - spuštění celého projektu

## Postup řešení

### 1. Vytvoření Docker sítě
docker network create prum_indstr

### 2. Sestavení a spuštění MariaDB
docker build -t my-mariadb ./mariadb
docker run -d --name mariadb-container --network prum_indstr -p 3307:3306 my-mariadb

### 3. Sestavení a spuštění Python kontejneru
docker build -t my-python-app ./python_app
docker run --name python-container --network prum_indstr my-python-app

### 4. Spuštění přes docker-compose
docker-compose up

## Výsledek
Python kontejner načte 27394 řádků z CSV a uloží je do tabulky
"weather" v MariaDB databázi.
