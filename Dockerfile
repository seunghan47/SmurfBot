FROM python:3.9.6-slim-buster
RUN useradd --create-home groupme
USER groupme
RUN pip install --user GroupyAPI==0.10.3
RUN pip install --user atomicwrites==1.3.0
RUN pip install --user google-api-python-client==1.7.11
WORKDIR /home/groupme
RUN mkdir app/
RUN mkdir app/src/
RUN mkdir app/logs/
RUN mkdir app/tags/
COPY src/* app/src/
WORKDIR /home/groupme/app
CMD ["python","src/start.py", "-c", "config.ini", "-g", "groups.json"]
