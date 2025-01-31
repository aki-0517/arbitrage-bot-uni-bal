# Market Maker Bot

マーケットメイクボットは、仮想通貨市場での自動取引を行うPythonベースのアプリケーションです。

## 機能
- **仮想通貨取引所とのAPI連携**: Binanceや他の主要取引所をサポート。
- **マーケットメイキング**: スプレッドを活用した効率的な注文処理。
- **データ分析と可視化**: pandasとmatplotlibを使用。
- **ログ管理**: ログを記録し、問題を簡単にトラブルシュート。

---

## 環境構築

### 1. 必要なソフトウェア
- Python 3.8以上
- pip (Pythonパッケージ管理ツール)
- Git

### 2. セットアップ手順
1. **リポジトリをクローン**:
   ```bash
   git clone https://github.com/your_username/market_maker_bot.git
   cd market_maker_bot
   ```

2. **仮想環境を作成**:
   ```bash
   python3 -m venv market_maker_env
   source market_maker_env/bin/activate  # Windowsの場合: market_maker_env\Scripts\activate
   ```

3. **依存関係をインストール**:
   ```bash
   pip install -r requirements.txt
   ```

4. **環境変数の設定**:
   `.env.example` をコピーして `.env` にリネームし、APIキーを入力します。
   ```plaintext
   cp .env.example .env
   ```

5. **動作確認**:
   以下のコマンドでサンプルスクリプトを実行します。
   ```bash
   python src/bot.py
   ```

---

## 使用ライブラリ
- [ccxt](https://github.com/ccxt/ccxt): 仮想通貨取引所API
- [numpy](https://numpy.org/): 数値計算
- [pandas](https://pandas.pydata.org/): データ分析
- [matplotlib](https://matplotlib.org/): グラフ描画
- [python-dotenv](https://github.com/theskumar/python-dotenv): 環境変数管理

---

## ディレクトリ構造
```
market_maker_bot/
├── market_maker_env/  # 仮想環境
├── data/              # データ保存用
├── logs/              # ログ保存用
├── src/               # ソースコード
│   ├── bot.py         # メインスクリプト
│   ├── config.py      # 設定
│   ├── strategies/    # 戦略用モジュール
├── requirements.txt   # 必要なパッケージ
├── .env               # 環境変数
├── .env.example       # 環境変数のサンプル
├── .gitignore         # Git無視リスト
├── README.md          # プロジェクト説明
```

---

## 注意事項
- 本ボットを使用する際は、取引リスクを十分に理解してください。
- APIキーは厳重に管理し、公開しないようにしてください。

