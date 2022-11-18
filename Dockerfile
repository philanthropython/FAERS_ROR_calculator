FROM python:latest

#RUN useradd -m user
# ユーザーを作成
#ARG UID=1000
#ARG USER=docker
#ARG PASSWORD=docker
#　RUN useradd -m -u ${UID} -g sudo ${USER} \
#  && echo ${USER}:${PASSWORD} | chpasswd
#RUN useradd -m -u ${UID} ${USER}
#USER ${USER}

RUN apt update && apt upgrade && apt install -y sudo

ARG USERNAME=user
ARG GROUPNAME=user
ARG UID=1000
ARG GID=1000
ARG PASSWORD=user

RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USERNAME 

#USER ${USER}

EXPOSE 5000
EXPOSE 8888

RUN mkdir ${HOME}/work
RUN mkdir ${HOME}/src
WORKDIR ${HOME}
COPY . ${HOME}/src 

RUN pip install -U pip
RUN pip install -r src/requirements.txt

#CMD /bin/bash
#ENTRYPOINT ["/bin/bash", "src/entrypoint.sh"]
ENTRYPOINT ["/bin/bash"]
