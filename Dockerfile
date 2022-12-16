FROM python:3 
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME


COPY . ./
#RUN pip install Flask gunicorn Jinja2 numpy
RUN pip install -r requirements.txt
RUN pip install -U scikit-learn

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
