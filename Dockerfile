FROM python:3.8

# set the working directory in the container
WORKDIR /ruskiBot

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies / make sure time zone is correct
RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/timezone && \
    ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    pip install -r requirements.txt

# copy the content of the local directory to the working directory
COPY . /ruskiBot

# command to run on container start
CMD [ "python", "-m", "main" ]
