FROM python:3.8

COPY . .

RUN pip install -r requirements.txt

# command to run on container start
CMD [ "gunicorn" ,"--chdir", "src", "app:app" ]

EXPOSE 5000