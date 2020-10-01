FROM balenalib/raspberrypi3:stretch

ADD ./test_image1.jpg .
ADD ./test_image2.jpg .

RUN apt-get update && apt-get install -y --no-install-recommends\
        python3 \
        python3-pip \
        build-essential \
        libboost-python1.62.0 \
        python3-picamera \
        python3-dev && \
        rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip 
RUN pip install --upgrade setuptools 
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

WORKDIR /home/pi
RUN usermod -a -G video root
RUN mkdir /capturedImage
RUN chmod 777 /capturedImage
ADD /app/ .
RUN chmod +x main.py
RUN chmod +x test_camera.py

ENTRYPOINT [ "python3", "-u", "main.py" ]