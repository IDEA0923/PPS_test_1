FROM  ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 && apt install -y python3-pip &&apt install postgresql postgresql-contrib -y -q &&rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
COPY init_database.py /app/
COPY videos.json /app/
COPY config.py /app/
COPY main.py /app/

CMD [ "python3" , "main.py" ]