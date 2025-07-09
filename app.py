
from flask import Flask, request, render_template_string, redirect, session, url_for
import os
import time
import hvac
import mysql.connector
import pyotp
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # À remplacer par une valeur sûre en prod

# Templates HTML simples
login_template = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
  <h2>Login</h2>
  <form method="post">
    Nom d'utilisateur: <input type="text" name="username"><br>
    Mot de passe: <input type="password" name="password"><br>
    <input type="submit" value="Connexion">
  </form>
</body>
</html>
"""

totp_template = """
<!DOCTYPE html>
<html>
<head><title>2FA</title></head>
<body>
  <h2>Code de vérification</h2>
  <form method="post">
    Code TOTP: <input type="text" name="code"><br>
    <input type="submit" value="Vérifier">
  </form>
</body>
</html>
"""

def get_db_credentials():
    client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
    secrets = client.secrets.kv.v2.read_secret_version(path="database/testvault")['data']['data']
    return secrets

def get_user_from_db(username):
    secrets = get_db_credentials()
    conn = mysql.connector.connect(
        host="mariadb",
        user=secrets['username'],
        password=secrets['password'],
        database="testvault"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_db(username)
        if user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['password'] == hashed_password:
                session['pre_2fa'] = True
                session['username'] = username
                return redirect(url_for('totp'))
        return "Identifiants invalides", 403
    return render_template_string(login_template)

@app.route('/2fa', methods=['GET', 'POST'])
def totp():
    if 'pre_2fa' not in session or 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form['code']
        username = session['username']
        user = get_user_from_db(username)

        if user:
            totp = pyotp.TOTP(user['totp_secret'])
            if totp.verify(code):
                # Vérifie si le code a déjà été utilisé
                secrets = get_db_credentials()
                conn = mysql.connector.connect(
                    host="mariadb",
                    user=secrets['username'],
                    password=secrets['password'],
                    database="testvault"
                )
                cursor = conn.cursor()

                cursor.execute("SELECT 1 FROM used_totp WHERE username = %s AND code = %s", (username, code))
                if cursor.fetchone():
                    cursor.close()
                    conn.close()
                    return "Code TOTP déjà utilisé", 403

                # Si ok, enregistre le code
                cursor.execute("INSERT INTO used_totp (username, code) VALUES (%s, %s)", (username, code))
                conn.commit()
                cursor.close()
                conn.close()

                session['authenticated'] = True
                return redirect(url_for('index'))

        return "Code invalide", 403

    return render_template_string(totp_template)

@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    secrets = get_db_credentials()
    conn = mysql.connector.connect(
        host="mariadb",
        user=secrets['username'],
        password=secrets['password'],
        database="testvault"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livre")
    livres = cursor.fetchall()
    cursor.close()
    conn.close()

    return "<br>".join(f"{id}: {titre}" for id, titre in livres)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
