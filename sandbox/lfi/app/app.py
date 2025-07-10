from flask import Flask, request
import os
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def lfi():
    msg = ''
    if request.method == 'POST':
        f = request.files['file']
        save_path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(save_path)
        msg = f"Fichier '{f.filename}' uploadé !"
    files = os.listdir(UPLOAD_FOLDER)
    files_list = "".join(
        f"<li>{fname} - <a href='?include={fname}'>Inclure</a></li>" for fname in files
    )
    include_result = ''
    to_include = request.args.get('include')
    if to_include:
        try:
            with open(os.path.join(UPLOAD_FOLDER, to_include), 'r') as f:
                code = f.read()
                exec(code)
            include_result = f"<b>Code exécuté depuis {to_include} !</b>"
        except Exception as e:
            include_result = f"<span style='color:red;'>Erreur d'exécution : {e}</span>"
        try:
            with open(os.path.join(UPLOAD_FOLDER, to_include), 'r') as f:
                code = f.read()
            include_result += f"<br><b>Contenu de {to_include} :</b><pre>{code}</pre>"
        except Exception:
            pass
    return f"""
    <html>
    <head><title>Sandbox LFI</title></head>
    <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
        <h1>Sandbox LFI</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Uploader</button>
        </form>
        <div style='margin:14px;'>{msg}</div>
        <ul style='list-style:none;padding:0;'>{files_list}</ul>
        <div style='margin-top:20px;'>{include_result}</div>
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
