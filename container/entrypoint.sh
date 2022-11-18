USER_ID=$(id -u)
GROUP_ID=$(id -g)

usermod -u $USER_ID user
sudo groupmod -g $GROUP_ID user

/bin/bash
# DockerfileのCMDで渡されたコマンド（→Railsのサーバー起動）を実行
#exec "$@"
