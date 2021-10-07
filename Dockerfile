FROM python:3.9

RUN apt update

RUN mkdir -p /root/.pip
ADD pip.conf /root/.pip/pip.conf
ENV PYTHONPATH=/app:${PYTHONPATH}
ENV PATH=/app:${PATH}

RUN mkdir -p /app/service/csvs
WORKDIR /app

ADD README.md /app
ADD main.py /app/service
ADD .dev_scripts /app
ADD docs /app
ADD Gene_Drive /app
RUN cd app && python ./.dev_scripts/bootstrap.py
ADD entrypoint.sh .
RUN chmod +x ./entrypoint.sh

EXPOSE 8050
CMD /app/entrypoint.sh