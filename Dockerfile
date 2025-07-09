FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Attente de MariaDB avant de démarrer Flask
CMD sh -c "echo 'Attente de MariaDB sur mariadb:3306...' && \
  while ! nc -z mariadb 3306; do sleep 1; done && \
  echo 'MariaDB est prêt, démarrage de Flask...' && \
  python app.py"
