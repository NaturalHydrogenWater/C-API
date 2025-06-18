from flask import Flask, request, jsonify, send_from_directory
import subprocess
import uuid
import os

app = Flask(__name__)

# C言語コードを受け取り、コンパイル・実行して結果を返すAPIエンドポイント
@app.route('/run', methods=['POST'])
def run_c():
    data = request.get_json()  # リクエストボディからJSONを取得
    code = data.get('code')    # 'code'キーからC言語コードを取得
    # コードが提供されていない場合のエラーハンドリング
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # 一時ファイル名を生成
    filename = f"/tmp/{uuid.uuid4().hex}.c"
    execname = filename[:-2]
    # C言語コードを一時ファイルに保存
    with open(filename, 'w') as f:
        f.write(code)

    try:
        # gccでC言語コードをコンパイル
        compile_proc = subprocess.run(
            ['gcc', filename, '-o', execname],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
        )
        # コンパイルエラーがあればエラー内容を返す
        if compile_proc.returncode != 0:
            return jsonify({'error': compile_proc.stderr.decode()}), 200

        # コンパイル成功時、バイナリを実行
        run_proc = subprocess.run(
            [execname],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
        )
        # 実行結果（標準出力・標準エラー・終了コード）をJSONで返す
        result = {
            'stdout': run_proc.stdout.decode(),
            'stderr': run_proc.stderr.decode(),
            'exit_code': run_proc.returncode
        }
        return jsonify(result)
    except subprocess.TimeoutExpired:
        # タイムアウト時のエラー
        return jsonify({'error': 'Timeout'}), 200
    finally:
        # 一時ファイルを削除
        try:
            os.remove(filename)
            os.remove(execname)
        except Exception:
            pass

# 動作確認用のルートエンドポイント
@app.get("/hello")
def read_root():
    return {"Hello": "World"}

if __name__ == '__main__':
    # Flaskアプリを0.0.0.0:5100で起動
    app.run(host='0.0.0.0', port=5100)