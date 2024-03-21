
#Using python
FROM python:3.9-slim
# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#Copy files to your container
COPY . ./
# CMD gunicorn -b 0.0.0.0:8080 app:server