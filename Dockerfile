FROM python:3.9.6-slim-buster
RUN useradd --create-home groupme
USER groupme
WORKDIR /home/groupme
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt
RUN rm requirements.txt
RUN mkdir app/
RUN mkdir app/src/
RUN mkdir app/logs/
RUN mkdir app/tags/
COPY src/* app/src/
WORKDIR /home/groupme/app
CMD ["python","src/start.py", "-c", "config.ini"]
