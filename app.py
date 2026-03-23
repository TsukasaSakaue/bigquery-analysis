"""Austin Bikeshare ダッシュボード"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Austin Bikeshare 分析",
    page_icon="🚲",
    layout="wide",
)

# --- データ読み込み（CSV から。BigQuery 不要） ---
@st.cache_data
def load_data():
    station_pairs = pd.read_csv("data/station_pairs.csv")
    monthly = pd.read_csv("data/monthly.csv")
    heatmap = pd.read_csv("data/heatmap.csv")
    return station_pairs, monthly, heatmap

station_pairs, monthly, heatmap = load_data()

st.title("🚲 Austin Bikeshare 分析ダッシュボード")
st.caption("データ元: bigquery-public-data.austin_bikeshare.bikeshare_trips（約227万トリップ）")

# ========================================
# タブで分析を切り替え
# ========================================
tab1, tab2, tab3 = st.tabs(["📊 ステーション別分析", "📈 時系列推移", "🗓️ 曜日×時間帯"])

# ========================================
# タブ1: ステーション別分析
# ========================================
with tab1:
    st.header("到着ステーション別 平均利用時間")
    st.write("出発ステーションを選ぶと、到着先ごとの平均利用時間が表示されます。")

    station_trip_counts = (
        station_pairs.groupby("start_station_name")["trip_count"]
        .sum()
        .sort_values(ascending=False)
    )
    station_list = station_trip_counts.index.tolist()

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_station = st.selectbox(
            "出発ステーションを選択",
            station_list,
            index=0,
        )
    with col2:
        top_n = st.slider("表示件数", min_value=5, max_value=30, value=15, step=5)

    filtered = (
        station_pairs[station_pairs["start_station_name"] == selected_station]
        .sort_values("avg_duration", ascending=True)
        .tail(top_n)
    )

    total_trips = filtered["trip_count"].sum()

    fig = px.bar(
        filtered,
        x="avg_duration",
        y="end_station_name",
        orientation="h",
        color="avg_duration",
        color_continuous_scale="Viridis",
        labels={
            "avg_duration": "平均利用時間（分）",
            "end_station_name": "到着ステーション",
        },
        title=f"「{selected_station}」発 → 到着ステーション別 平均利用時間（対象: {total_trips:,} トリップ）",
        hover_data={"trip_count": ":,"},
    )
    fig.update_layout(height=max(400, top_n * 35), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("データテーブルを表示"):
        st.dataframe(
            filtered[["end_station_name", "avg_duration", "trip_count"]]
            .sort_values("avg_duration", ascending=False)
            .rename(columns={
                "end_station_name": "到着ステーション",
                "avg_duration": "平均利用時間（分）",
                "trip_count": "トリップ数",
            }),
            hide_index=True,
            use_container_width=True,
        )

# ========================================
# タブ2: 月別トリップ数の推移
# ========================================
with tab2:
    st.header("月別トリップ数の推移")

    subscriber_types = monthly["subscriber_type"].unique().tolist()
    top_types = (
        monthly.groupby("subscriber_type")["trip_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    selected_types = st.multiselect(
        "利用者タイプで絞り込み（複数選択可）",
        subscriber_types,
        default=top_types[:3],
    )

    if selected_types:
        filtered_monthly = monthly[monthly["subscriber_type"].isin(selected_types)]
        monthly_agg = (
            filtered_monthly.groupby("month")
            .agg({"trip_count": "sum", "avg_duration": "mean"})
            .reset_index()
        )

        fig2 = px.line(
            filtered_monthly,
            x="month",
            y="trip_count",
            color="subscriber_type",
            labels={
                "month": "月",
                "trip_count": "トリップ数",
                "subscriber_type": "利用者タイプ",
            },
            title="月別トリップ数の推移（利用者タイプ別）",
        )
        fig2.update_layout(height=500, xaxis_tickangle=-45)
        fig2.update_xaxes(dtick=6)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("利用者タイプを1つ以上選択してください。")

# ========================================
# タブ3: 曜日×時間帯ヒートマップ
# ========================================
with tab3:
    st.header("曜日×時間帯の利用パターン")
    st.write("どの曜日・時間帯に自転車がよく使われているかを色の濃さで表現しています。")

    day_labels = {1: "日", 2: "月", 3: "火", 4: "水", 5: "木", 6: "金", 7: "土"}
    heatmap["day_label"] = heatmap["day_of_week"].map(day_labels)

    pivot = heatmap.pivot(index="day_of_week", columns="hour", values="trip_count").fillna(0)
    y_labels = [day_labels[i] for i in pivot.index]

    fig3 = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h}時" for h in pivot.columns],
        y=y_labels,
        colorscale="YlOrRd",
        hovertemplate="曜日: %{y}<br>時間: %{x}<br>トリップ数: %{z:,}<extra></extra>",
    ))
    fig3.update_layout(
        title="曜日×時間帯の利用パターン（ヒートマップ）",
        height=400,
        xaxis_title="時間帯",
        yaxis_title="曜日",
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- フッター ---
st.divider()
st.caption("データソース: Google BigQuery Public Datasets - Austin Bikeshare Trips")
