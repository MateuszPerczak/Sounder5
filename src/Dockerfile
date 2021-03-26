FROM python:latest
ADD . /home/sounder
WORKDIR /home/sounder
RUN pip install -r requirements.txt
RUN pip install mypy
RUN mypy --strict Sounder5.py
CMD ["python", "Sounder5.py"]