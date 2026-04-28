import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

day_df = pd.read_csv("dashboard/main_data.csv")
day_df["dteday"] = pd.to_datetime(day_df["dteday"])

season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
day_df["season_label"] = day_df["season"].map(season_map)

st.title("Bike Sharing Data Analytics Dashboard")
st.markdown("Dashboard ini menampilkan hasil analisis data penyewaan sepeda.")

st.sidebar.header("Filter Tahun")
selected_year = st.sidebar.selectbox("Pilih Tahun", [2011, 2012])
year_filter = 0 if selected_year == 2011 else 1

main_df = day_df[day_df["yr"] == year_filter]

st.subheader("Ringkasan Data")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", value=f"{main_df.cnt.sum():,}")
with col2:
    st.metric("Rata-rata Pengguna Casual", value=int(main_df.casual.mean()))
with col3:
    st.metric("Rata-rata Pengguna Terdaftar", value=int(main_df.registered.mean()))

st.divider()

st.subheader("Rata-rata Penyewaan Harian Berdasarkan Musim")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="season_label", 
    y="cnt", 
    data=main_df.groupby("season_label")["cnt"].mean().reset_index().sort_values("cnt", ascending=False),
    palette="viridis",
    ax=ax
)
ax.set_ylabel("Rata-rata Penyewaan")
ax.set_xlabel(None)
st.pyplot(fig)

st.caption("Copyright (c) Abel 2026")