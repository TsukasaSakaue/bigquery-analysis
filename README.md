# BigQuery データ分析プロジェクト

BigQuery の公開データセット（Austin Bikeshare）を使ったデータ分析プロジェクトです。

## 使用データ

- **テーブル**: `bigquery-public-data.austin_bikeshare.bikeshare_trips`
- **内容**: テキサス州オースティンの自転車シェアリング利用記録
- **規模**: 約227万件（2013年〜2024年）

## ノートブック

| ファイル | 内容 |
|----------|------|
| `bigquery_analysis.ipynb` | SQL・可視化・統計分析の基礎 |
| `station_analysis.ipynb` | 到着ステーション別の平均利用時間（インタラクティブ） |

## セットアップ

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
.\venv\Scripts\activate

# ライブラリのインストール
pip install -r requirements.txt
```

## 使い方

1. Cursor で `.ipynb` ファイルを開く
2. カーネルに `venv` の Python を選択
3. 上から順にセルを実行（Shift + Enter）

## 必要な環境

- Python 3.12
- GCP プロジェクトへのアクセス（`gcloud auth application-default login` で認証）
