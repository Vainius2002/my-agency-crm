FROM python:3.12-slim

WORKDIR /app

COPY agency_crm/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "agency_crm/run.py"]