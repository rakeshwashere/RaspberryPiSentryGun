FROM sgtwilko/rpi-raspbian-opencv

WORKDIR /SentryGun 

COPY . .

RUN sudo apt-get update && sudo pip3 install -r requirements.txt

CMD ./activate.sh