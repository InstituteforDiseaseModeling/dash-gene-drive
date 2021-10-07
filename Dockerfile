FROM python:3.9

RUN apt update

RUN mkdir -p /root/.pip
ADD pip.conf /root/.pip/pip.conf
ENV PYTHONPATH=/app:${PYTHONPATH}
ENV PATH=/app:${PATH}

RUN mkdir -p /app/service/csvs
WORKDIR /app

ADD README.md .
ADD main.py ./service
ADD .dev_scripts .
ADD docs .
ADD Gene_Drive .
ADD entrypoint.sh .
RUN chmod +x ./entrypoint.sh
RUN python ./.dev_scripts/bootstrap.py


EXPOSE 8050
CMD /app/entrypoint.sh