# FAERS_ROR_calculator

## Getting Started
Install Docker<br>
https://docs.docker.com/engine/install/

Download this repository
```
git clone https://github.com/philanthropython/FAERS_ROR_calculator.git
```
```
cd FAERS_ROR_calculator
```

Build docker images
```bash
docker compose build
```

## Initial Setup
Start the setup container
This step may take several hours
```bash
docker run --rm -v $PWD/app:/app -it faers-app
```
If you need to update FAERS data, edit app/config.py and repeat this step again 

## Starting web-app server
```bash
docker-compose up -d
```
Access `http://localhost` with a web browser<br>

## Secure access
Install remote.it to your host machine and start HTTP service with a persistent public URL<br>
https://ja.remote.it/download-list

## Configuration
Edit app/common/config.py and repeat the above steps 3 and 4

