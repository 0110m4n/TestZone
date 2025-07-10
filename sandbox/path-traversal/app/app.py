from flask import Flask, request
import os

app = Flask(__name__)

FILES_DIR = 'files'
os.makedirs(FILES_DIR, exist_ok=True)

DEMO_FILES = [f"exemple{i}.txt" for i in range(1, 11)]
SECRET_FILES = ["secret1.txt", "flag.txt"]
ALL_FILES = DEMO_FILES + SECRET_FILES

for fname in ALL_FILES:
    fpath = os.path.join(FILES_DIR, fname)
    if not os.path.exists(fpath):
        with open(fpath, 'w') as f:
            if fname in DEMO_FILES:
                f.write(f"Ceci est le fichier {fname}\n")
            else:
                f.write(f"Fichier *secret* {fname} - Bravo pour l'avoir trouvé !\nFLAG{{testzone-path-traversal}}\n")

@app.route('/')
def index():
    files_list = "".join(
        f"<li><a href='/read?file={fname}'>{fname}</a></li>" for fname in DEMO_FILES
    )
    return f"""
    <html>
    <head><title>Sandbox Path Traversal</title></head>
    <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
        <h1>Sandbox Path Traversal</h1>
        <p>Liste de fichiers :</p>
        <ul style='list-style:none;padding:0;font-size:1.2em'>{files_list}</ul>
        <div style="margin-top:32px;color:#aaa">
            <b>Essayez de lire des fichiers non listés !</b>
        </div>
        <form method="post" action="/stop" style="margin-top:32px;">
            <button type="submit" style="background:#ff0044;color:#fff;padding:10px 28px;border:none;border-radius:12px;cursor:pointer;font-size:1.2em;">⬅ Retour à TestZone</button>
        </form>
    </body>
    </html>
    """

@app.route('/read')
def read_file():
    filename = request.args.get('file', '')
    file_path = os.path.join(FILES_DIR, filename)
    msg = ""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        msg = f"<pre style='background:#222;color:#0f0;padding:18px 20px;border-radius:8px;max-width:700px;margin:0 auto'>{content}</pre>"
    except Exception as e:
        msg = f"<div style='color:red;margin-top:20px;'>Erreur : {e}</div>"
    return f"""
    <html>
    <head><title>Lecture de fichier</title></head>
    <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
        <h1>Lecture du fichier : {filename}</h1>
        <a href="/" style='color:#00ff88;'>⬅ Retour</a>
        {msg}
        <form method="post" action="/stop" style="margin-top:32px;">
            <button type="submit" style="background:#ff0044;color:#fff;padding:10px 28px;border:none;border-radius:12px;cursor:pointer;font-size:1.2em;">⬅ Retour à TestZone</button>
        </form>
    </body>
    </html>
    """

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
