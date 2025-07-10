from flask import Flask, request

app = Flask(__name__)

users = {
    1: {'nom': 'Alice', 'email': 'alice@pentest.com', 'role': 'user'},
    2: {'nom': 'Bob', 'email': 'bob@pentest.com', 'role': 'user'},
    3: {'nom': 'Admin', 'email': 'admin@pentest.com', 'role': 'admin'}
}

CURRENT_USER_ID = 1

@app.route('/')
def home():
    return f'''
    <html>
    <head><title>Sandbox IDOR</title></head>
    <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
        <h1>Sandbox IDOR</h1>
        <p>Bienvenue Alice !</p>
        <a href="/profile/{CURRENT_USER_ID}" style="color:#00ff88;font-size:1.3em;">Voir mon profil</a><br><br>
        <span style="color:#aaa;">Essayez de modifier l'URL du navigateur pour voir d'autres profils…</span>
        <form method="post" action="/stop" style="margin-top:32px;">
            <button type="submit" style="background:#ff0044;color:#fff;padding:10px 28px;border:none;border-radius:12px;cursor:pointer;font-size:1.2em;">⬅ Retour à TestZone</button>
        </form>
    </body>
    </html>
    '''

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = users.get(user_id)
    if user:
        return f'''
        <html>
        <head><title>Profil Utilisateur</title></head>
        <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
            <h1>Profil Utilisateur #{user_id}</h1>
            <p><b>Nom :</b> {user["nom"]}<br>
            <b>Email :</b> {user["email"]}<br>
            <b>Rôle :</b> {user["role"]}</p>
            <a href="/" style="color:#00ff88;">Retour</a>
            <form method="post" action="/stop" style="margin-top:32px;">
                <button type="submit" style="background:#ff0044;color:#fff;padding:10px 28px;border:none;border-radius:12px;cursor:pointer;font-size:1.2em;">⬅ Retour à TestZone</button>
            </form>
        </body>
        </html>
        '''
    else:
        return "<span style='color:red;'>Utilisateur non trouvé.</span>", 404

@app.route('/stop', methods=['POST'])
def stop():
    import threading, os, time
    def stop_later():
        time.sleep(2)
        os._exit(0)
    threading.Thread(target=stop_later, daemon=True).start()
    return """
    <html>
    <head><meta http-equiv="refresh" content="1; url=http://localhost:5000/sandbox"></head>
    <body style='background:#142850;color:#00ff88;text-align:center;font-family:sans-serif;'>
    <h1>Sandbox arrêtée.</h1>
    <p>Redirection vers TestZone...</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
