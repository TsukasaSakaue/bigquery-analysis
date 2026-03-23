"""BigQuery からデータを取得して CSV に保存するスクリプト"""
from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='samplestudy-465703')

# 出発×到着ステーション別の平均利用時間・トリップ数
query_station_pairs = """
SELECT
    start_station_name,
    end_station_name,
    ROUND(AVG(duration_minutes), 1) AS avg_duration,
    COUNT(*) AS trip_count
FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
WHERE start_station_name IS NOT NULL
    AND end_station_name IS NOT NULL
    AND duration_minutes IS NOT NULL
    AND duration_minutes > 0
GROUP BY start_station_name, end_station_name
HAVING COUNT(*) >= 10
ORDER BY start_station_name, avg_duration DESC
"""

# 月別トリップ数（時系列推移）
query_monthly = """
SELECT
    FORMAT_TIMESTAMP('%Y-%m', start_time) AS month,
    subscriber_type,
    COUNT(*) AS trip_count,
    ROUND(AVG(duration_minutes), 1) AS avg_duration
FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
WHERE start_time IS NOT NULL
    AND subscriber_type IS NOT NULL
    AND subscriber_type != ''
GROUP BY month, subscriber_type
ORDER BY month
"""

# 曜日×時間帯のヒートマップ用
query_heatmap = """
SELECT
    EXTRACT(DAYOFWEEK FROM start_time) AS day_of_week,
    EXTRACT(HOUR FROM start_time) AS hour,
    COUNT(*) AS trip_count
FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
WHERE start_time IS NOT NULL
GROUP BY day_of_week, hour
ORDER BY day_of_week, hour
"""

datasets = {
    'station_pairs': query_station_pairs,
    'monthly': query_monthly,
    'heatmap': query_heatmap,
}

for name, query in datasets.items():
    print(f'{name} を取得中...')
    df = client.query(query).to_dataframe()
    path = f'data/{name}.csv'
    df.to_csv(path, index=False)
    print(f'  -> {path} ({len(df):,} 行)')

print('\n全データ取得完了！')
