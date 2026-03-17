
FROM node:18 AS frontend
COPY ui/package.json /var/app/ui/package.json
COPY ui/package-lock.json /var/app/ui/package-lock.json
WORKDIR /var/app/ui
RUN npm ci
COPY ui/src /var/app/ui/src
COPY ui/public /var/app/ui/public
RUN npm run build

FROM python:3.14.2
COPY --from=frontend /var/app/ui/build /var/app/ui/build
COPY api/requirements.txt /var/app/api/requirements.txt
WORKDIR /var/app/api
RUN pip install --no-cache-dir --upgrade -r /var/app/api/requirements.txt
COPY api /var/app/api
CMD ["uvicorn", "main:app", "--port", "80", "--host", "0.0.0.0"]
