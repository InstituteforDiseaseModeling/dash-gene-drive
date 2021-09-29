FROM python:3.9

RUN apt update

RUN mkdir -p /root/.pip
ADD pip.conf /root/.pip/pip.conf
ENV PYTHONPATH=/app:${PYTHONPATH}
ENV PATH=/app:${PATH}

RUN mkdir -p /app/service/csvs
WORKDIR /app

ADD README_Old.md /app
ADD Gene_Drive /app/service
RUN cd service && pip install -r requirements.txt
ADD entrypoint.sh .
RUN chmod +x ./entrypoint.sh


EXPOSE 8050
CMD /app/entrypoint.sh