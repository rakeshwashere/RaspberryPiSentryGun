FROM sgtwilko/rpi-raspbian-opencv

WORKDIR /SentryGun 

RUN pip3 install RPi.GPIO

COPY . .

CMD ./activate.sh