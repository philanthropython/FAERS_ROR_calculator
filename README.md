# FAERS_ROR_calculator

## Gtting started
1. Install Docker<br>
https://docs.docker.com/engine/install/

2. Download this repository
```
git clone https://github.com/philanthropython/FAERS_ROR_calculator.git
```
```
cd FAERS_ROR_calculator
```

3. Build a docker image for setup
```bash
docker build -t setup app/setup/container
```

4. Start the setup container
```bash
docker run --rm -v $PWD/data:/data -v $PWD/app:/app -it setup
```

5. Start the web app server
```bash
docker-compose up -d
```

6. Access the server with any web browser of your choice<br>
http://localhost

## Secure access
Install remote.it to your host machine<br>
https://ja.remote.it/download-list

## Configuration
Edit app/common/config.py and repeat the above steps 3 and 4

