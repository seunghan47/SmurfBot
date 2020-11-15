FROM python:3.7-slim-buster
RUN pip install GroupyAPI==0.10.3
RUN pip install atomicwrites==1.3.0
RUN pip install google-api-python-client==1.7.11
RUN useradd --create-home groupme
WORKDIR /home/groupme
USER groupme
RUN mkdir app/
RUN mkdir app/src/
RUN mkdir app/logs/
RUN mkdir app/tags/
COPY src/* app/src/
WORKDIR /home/groupme/app
CMD ["python","src/start.py", "-c", "config.ini", "-g", "groups.json"]
