FROM python:3.10.4-slim-buster
RUN useradd --create-home groupme
RUN rm -f /etc/localtime
RUN ln -s /usr/share/zoneinfo/America/New_York /etc/localtime
USER groupme
WORKDIR /home/groupme
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt
RUN rm requirements.txt
RUN mkdir app/
RUN mkdir app/src/
RUN mkdir app/logs/
RUN mkdir app/tags/
RUN mkdir app/reminders/
COPY src/* app/src/
WORKDIR /home/groupme/app
CMD ["python","src/start.py", "-c", "config.ini"]
