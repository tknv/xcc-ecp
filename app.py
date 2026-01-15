from flask import Flask, request, render_template_string
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary

app = Flask(__name__)

# ==========================================
# 【設定項目】ハードコード部分
# ==========================================
# 1. RADIUSサーバー設定
RADIUS_HOST = "192.168.100.56" 
RADIUS_PORT = 1812
RADIUS_SECRET = b"testing123"
DICTIONARY_PATH = "./dictionary"

# 2. 認証成功時のリダイレクト先 (XIQ-Cのログイン受付URL)
# コントローラーのIPアドレスが 192.168.100.8 の場合の例です。環境に合わせて変更してください。
REDIRECT_TARGET_URL = "http://192.168.100.8/web/login"
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    
    # XIQ-Cからリダイレクト時に渡されるパラメータを保持
    token = request.args.get('token') or request.form.get('token', '')
    wlan = request.args.get('wlan') or request.form.get('wlan', '')
    original_url = request.args.get('redirect') or request.form.get('redirect', '')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # RADIUS認証実行
        if authenticate(username, password):
            # 認証成功：ハードコードされたURLへ自動POSTする画面を返す
            return render_xiq_redirect(username, password, token, wlan, original_url)
        else:
            message = "Authentication Failed. Please try again."

    # ログイン画面 (CSSなし)
    html = f"""
    <html>
    <head><title>Wi-Fi Login</title></head>
    <body>
        <h2>Login to Network</h2>
        <p style="color:red;">{message}</p>
        <form method="post">
            <input type="hidden" name="token" value="{token}">
            <input type="hidden" name="wlan" value="{wlan}">
            <input type="hidden" name="redirect" value="{original_url}">
            
            Username: <input type="text" name="username" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """
    return html

def render_xiq_redirect(username, password, token, wlan, original_url):
    """
    ハードコードされたREDIRECT_TARGET_URLに対して
    JavaScriptで自動的にフォームを送信（POST）する。
    """
    html = f"""
    <html>
    <body onload="document.getElementById('redirectForm').submit();">
        <p>Authenticating with Controller... Please wait.</p>
        <form id="redirectForm" action="{REDIRECT_TARGET_URL}" method="post">
            <input type="hidden" name="username" value="{username}">
            <input type="hidden" name="password" value="{password}">
            <input type="hidden" name="token" value="{token}">
            <input type="hidden" name="wlan" value="{wlan}">
            <input type="hidden" name="redirect" value="{original_url}">
            <input type="hidden" name="cmd" value="login">
        </form>
    </body>
    </html>
    """
    return html

def authenticate(username, password):
    try:
        srv = Client(server=RADIUS_HOST, authport=RADIUS_PORT, secret=RADIUS_SECRET, dict=Dictionary(DICTIONARY_PATH))
        req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username)
        req["User-Password"] = req.PwCrypt(password)
        req["NAS-IP-Address"] = "127.0.0.1"
        req["NAS-Port"] = 0
        reply = srv.SendPacket(req)
        return reply.code == pyrad.packet.AccessAccept
    except Exception as e:
        print(f"RADIUS Error: {e}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)