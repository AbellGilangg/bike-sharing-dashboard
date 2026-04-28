import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

@st.cache_data
def load_data():
    try:
        day_df = pd.read_csv("main_data.csv")
        hour_df = pd.read_csv("hour.csv")
    except FileNotFoundError:
        day_df = pd.read_csv("main_data.csv")
        hour_df = pd.read_csv("hour.csv")

    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_mapping = {
        1: "Clear",
        2: "Misty",
        3: "Light Snow/Rain",
        4: "Heavy Rain/Snow",
    }

    day_df["season_label"] = day_df["season"].map(season_mapping)
    day_df["weather_label"] = day_df["weathersit"].map(weather_mapping)
    hour_df["season_label"] = hour_df["season"].map(season_mapping)

    return day_df, hour_df

day_df, hour_df = load_data()

st.sidebar.title("Bike Sharing Dashboard")
st.sidebar.markdown("Analisis Data Penyewaan Sepeda")

# --- FITUR BARU: FILTER MUSIM & CUACA (DI ATAS KALENDER) ---
season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=day_df["season_label"].unique(),
    default=day_df["season_label"].unique()
)

weather_filter = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    options=day_df["weather_label"].unique(),
    default=day_df["weather_label"].unique()
)
# -----------------------------------------------------------

date_min = day_df["dteday"].min().date()
date_max = day_df["dteday"].max().date()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_min, date_max

try:
    # Penyesuaian agar hour_df juga memiliki weather_label untuk difilter
    weather_mapping_hour = {1: "Clear", 2: "Misty", 3: "Light Snow/Rain", 4: "Heavy Rain/Snow"}
    if "weather_label" not in hour_df.columns:
        hour_df["weather_label"] = hour_df["weathersit"].map(weather_mapping_hour)

    # Memasukkan season_filter dan weather_filter ke dalam logika filtering
    filtered_day_df = day_df[
        (day_df["dteday"].dt.date >= start_date) &
        (day_df["dteday"].dt.date <= end_date) &
        (day_df["season_label"].isin(season_filter)) &
        (day_df["weather_label"].isin(weather_filter))
    ]
    filtered_hour_df = hour_df[
        (hour_df["dteday"].dt.date >= start_date) &
        (hour_df["dteday"].dt.date <= end_date) &
        (hour_df["season_label"].isin(season_filter)) &
        (hour_df["weather_label"].isin(weather_filter))
    ]

    if filtered_day_df.empty or filtered_hour_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan sesuaikan filter di sidebar.")
        st.stop()

    st.title("Bike Sharing Analysis Dashboard")
    st.markdown("Dashboard interaktif untuk analisis penyewaan sepeda berdasarkan rentang waktu yang dipilih.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan", f"{filtered_day_df['cnt'].sum():,}")
    with col2:
        st.metric("Rata-rata Penyewaan Harian", f"{filtered_day_df['cnt'].mean():.0f}")
    with col3:
        st.metric("Jumlah Hari", len(filtered_day_df))

    st.divider()

    st.header("1. Rata-rata Penyewaan Sepeda per Musim")
    season_analysis = filtered_day_df.groupby("season_label")["cnt"].mean().reset_index().sort_values('cnt', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors_season = ["#90CAF9" if i == 0 else "#D3D3D3" for i in range(len(season_analysis))]
    bars = ax.bar(season_analysis["season_label"], season_analysis["cnt"], color=colors_season)
    
    ax.set_title("Rata-rata Penyewaan per Musim", fontsize=20)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='x', labelsize=15)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 50, f"{yval:.0f}", ha="center", va="bottom", fontsize=12)
    
    st.pyplot(fig)

    st.header("2. Tren Penyewaan per Jam (Hari Kerja)")
    working_data = filtered_hour_df[filtered_hour_df['workingday'] == 1]
    
    if not working_data.empty:
        hourly_avg = working_data.groupby('hr')['cnt'].mean().reset_index()

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(hourly_avg["hr"], hourly_avg["cnt"], marker="o", linestyle="-", color="#90CAF9", linewidth=3)
        ax2.set_title("Rata-rata Penyewaan per Jam (Hari Kerja)", fontsize=20)
        ax2.set_xlabel("Jam (0-23)", fontsize=15)
        ax2.set_ylabel(None)
        ax2.set_xticks(range(0, 24))
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

        peak_hour = hourly_avg.loc[hourly_avg["cnt"].idxmax()]
        st.write(f"**Insight:** Jam puncak pada hari kerja terjadi pada pukul **{peak_hour['hr']:.0f}:00** dengan rata-rata **{peak_hour['cnt']:.0f} penyewaan**.")
    else:
        st.warning("Tidak ada data hari kerja pada rentang tanggal ini.")

    st.header("3. Pengaruh Kondisi Cuaca terhadap Penyewaan")
    weather_avg = filtered_day_df.groupby("weather_label")["cnt"].mean().reset_index().sort_values('cnt', ascending=False)
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    colors_weather = ["#90CAF9" if i == 0 else "#D3D3D3" for i in range(len(weather_avg))]
    bars_w = ax3.bar(weather_avg["weather_label"], weather_avg["cnt"], color=colors_weather)
    
    ax3.set_title("Rata-rata Penyewaan per Kondisi Cuaca", fontsize=20)
    ax3.set_xlabel(None)
    ax3.set_ylabel(None)
    ax3.tick_params(axis='y', labelsize=15)
    ax3.tick_params(axis='x', labelsize=15)

    for bar in bars_w:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2, yval + 50, f"{yval:.0f}", ha="center", va="bottom", fontsize=12)
        
    st.pyplot(fig3)

    st.markdown("---")
    st.markdown("Dashboard dibuat dengan Streamlit.")
    st.caption('Copyright © Abel Gilang Saputra 2026')

except Exception as e:
    st.error(f"Terjadi kesalahan dalam memproses data: {str(e)}. Silakan periksa rentang tanggal.")
