FROM python:latest

RUN apt update && apt -y upgrade && apt install -y sudo vim

ARG USERNAME=user
ARG GROUPNAME=user
ARG UID=1000
ARG GID=1000
ARG PASSWORD=user

RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
ENV PATH $PATH:/home/$USERNAME/.local/bin

RUN mkdir /data
WORKDIR /app/main
ENV FLASK_APP=app
COPY ./requirements.txt ./

USER $USERNAME
RUN pip install -U pip
RUN pip install -r requirements.txt

#EXPOSE 5000

CMD ["uwsgi", "--ini", "app.ini"]
