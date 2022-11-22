# FAERS_ROR_calculator
A web application for calculating reported odds ratio (ROR) from FDA Adverse Event Reporting System (FAERS) data.<br>
It commprises of Nginx + uWSGI + Flask components working on docker containers.

## System Requirements
RAM: >8GB free space<br>
Storage: >20GB free space<br>
(Tested on Windows 10/11 + WSL2 with docker-desktop for Windows)

## Prerequisite
Install docker and docker-compose<br>
https://docs.docker.com/engine/install/

## Getting Started
Download this repository
```bash
git clone https://github.com/philanthropython/FAERS_ROR_calculator.git
```
Build docker images
```bash
cd FAERS_ROR_calculator
```
```bash
docker-compose build
```

## Initial Setup
Start the setup container<br>
This step may take several hours
```bash
docker run --rm -v $PWD/app:s/app -it faers-app
```
If you need to update FAERS data, edit app/config.py and repeat this step again 

## Starting web-app server
```bash
docker-compose up -d
```
Access *http://localhost* with a web browser<br>

## Secure Access
Install remote.it to your host machine and start HTTP service with a persistent public URL<br>
https://ja.remote.it/download-list

## Configuration
Edit *app/config.py* and repeat the setup process shown above.

