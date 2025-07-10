from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    value = ""
    if request.method == "POST":
        value = request.form.get("input", "")
    return f"""
    <html>
    <head><title>Sandbox XSS</title></head>
    <body style="background:#142850;color:#00ff88;font-family:sans-serif;text-align:center;">
        <h1>Sandbox XSS</h1>
        <form method="post">
            <input name="input" placeholder="Tapez ici…" style="padding:10px;font-size:1.2em;">
            <button type="submit" style="padding:10px 30px;">Envoyer</button>
        </form>
        <div style="margin-top:40px;font-size:2em;color:#fff;">
            {value}
        </div>
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
