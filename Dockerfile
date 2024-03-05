
#Using python
FROM python:3.9-slim
# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements_docker.txt
RUN pip install -r requirements_docker.txt
#Copy files to your container
COPY . ./
#Running your APP and doing some PORT Forwarding
CMD gunicorn -b 0.0.0.0:80 app:server


docker tag local-image:tagname new-repo:tagname
docker push new-repo:tagname