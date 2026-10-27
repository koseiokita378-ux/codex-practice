"""Codex ハンズオンの準備ができているかを確かめる。

    Windows:  py check_setup.py
    Mac:      python3 check_setup.py

何も変更しない。NG の行に書いてあることをやってから、もう一度実行する。
"""

import glob
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

WINDOWS = sys.platform == "win32"
MAC = sys.platform == "darwin"
HOME = os.path.expanduser("~")

results = []


def report(status, title, hint=""):
    results.append(status)
    print(f"[{status}] {title}")
    for line in hint.splitlines():
        print(f"       {line}")


def run(args):
    """コマンドを実行して (成功したか, 出力の1行目) を返す。"""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    out = (p.stdout or p.stderr).strip().splitlines()
    return p.returncode == 0, out[0] if out else ""


def check_python():
    v = sys.version_info
    if v < (3, 9):
        report("NG", f"Python {v.major}.{v.minor}（古い）", "3.9 以上を入れてください")
        return
    report("OK", f"Python {v.major}.{v.minor}.{v.micro}")
    # Windows の「python」は、入っていないと Microsoft Store を開くだけの偽物のことがある
    if WINDOWS:
        p = shutil.which("python")
        if p is None or "WindowsApps" in p:
            report("注意", "このPCでは「python」ではなく「py」で起動します",
                   "Codex が python で失敗したら「py を使って」と頼めば大丈夫です")


def check_git():
    ok, line = run(["git", "--version"])
    if not ok:
        if WINDOWS:
            hint = "PowerShell で: winget install -e --id Git.Git\n入れたら VS Code を閉じて開き直す"
        else:
            hint = "ターミナルで: xcode-select --install\n出てきた画面で「インストール」を押す"
        report("NG", "Git が見つからない", hint)
        return
    report("OK", line)
    for key, example in (("user.name", "GitHubのユーザー名"), ("user.email", "登録したメールアドレス")):
        ok, value = run(["git", "config", "--global", key])
        if ok and value:
            report("OK", f"git の {key}: {value}")
        else:
            report("NG", f"git の {key} が未設定", f'git config --global {key} "{example}"')


def find_vscode():
    if shutil.which("code"):
        return True
    if WINDOWS:
        cands = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft VS Code", "Code.exe"),
        ]
    elif MAC:
        cands = [
            "/Applications/Visual Studio Code.app",
            os.path.join(HOME, "Applications", "Visual Studio Code.app"),
        ]
    else:
        cands = []
    return any(os.path.exists(c) for c in cands)


def check_vscode():
    if find_vscode():
        report("OK", "VS Code")
    else:
        report("注意", "VS Code の場所を確認できなかった",
               "VS Code が開けているなら、そのまま進んで構いません")
    if glob.glob(os.path.join(HOME, ".vscode", "extensions", "openai.chatgpt-*")):
        report("OK", "Codex 拡張機能")
    else:
        report("NG", "Codex 拡張機能が入っていない",
               "VS Code の拡張機能で「Codex」を検索し、提供元が OpenAI のものを入れる")


def check_login():
    codex_home = os.environ.get("CODEX_HOME") or os.path.join(HOME, ".codex")
    if os.path.exists(os.path.join(codex_home, "auth.json")):
        report("OK", "Codex にログイン済み")
    else:
        # 認証情報を OS のキーチェーンに置く設定だと auth.json はできない。だから NG にはしない
        report("注意", "Codex のログインを確認できなかった",
               "VS Code の Codex の画面でログインを求められていなければ大丈夫です")


def check_network():
    try:
        urllib.request.urlopen("https://chatgpt.com/", timeout=10)
    except urllib.error.HTTPError:
        pass  # 応答が返ってきたのでつながっている（403 なども問題ない）
    except Exception as e:
        # 証明書のエラーは、ウイルス対策ソフトの通信検査が原因のことが多い
        report("NG", "chatgpt.com につながらない", f"{type(e).__name__}: {e}\n手を挙げてください")
        return
    report("OK", "chatgpt.com につながる")


def main():
    print(f"{platform.system()} {platform.release()} / Python {platform.python_version()}")
    print()
    check_python()
    check_git()
    check_vscode()
    check_login()
    check_network()
    print()
    ng = results.count("NG")
    if ng:
        print(f"NG が {ng} 個あります。上の指示どおりにして、もう一度実行してください。")
    else:
        print("準備できています。")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
