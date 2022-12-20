FROM python:3 
ENV PYTHONUNBUFFERED True
ENV PORT=8080

ENV APP_HOME /app
WORKDIR $APP_HOME


COPY . ./
#RUN pip install Flask gunicorn Jinja2 numpy
RUN apt-get update && apt-get -y install sudo

RUN sudo pip3 install pickle5
RUN pip install -r requirements.txt
RUN pip install -U scikit-learn

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
