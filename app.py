import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import warnings

warnings.filterwarnings('ignore')

# 1. 画面のタイトルと入力欄
st.title("📈 銘柄分析ダッシュボード")
ticker_code = st.text_input("銘柄コードを入力してください", "6547")

# 入力がある場合のみ処理を実行
if ticker_code:
    ticker = ticker_code + ".T"
    
    try:
        # 2. データの取得
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get('longName', ticker_code)
        df = stock.history(period="1y")

        if len(df) < 25:
            st.error(f"【エラー】{ticker_code} のデータが足りません.")
        else:
            df = df.dropna()

            # 3. テクニカル指標の計算
            window = 25
            df['SMA25'] = df['Close'].rolling(window=window).mean()
            df['STD25'] = df['Close'].rolling(window=window).std()
            df['Upper_2sigma'] = df['SMA25'] + (df['STD25'] * 2)
            df['Lower_2sigma'] = df['SMA25'] - (df['STD25'] * 2)
            df['Deviation_Rate'] = ((df['Close'] - df['SMA25']) / df['SMA25']) * 100

            latest = df.iloc[-1]

            # テキスト情報の表示 (Colabのprintの代わりにst.writeを使用)
            st.write(f"**分析銘柄:** {company_name} | **現在値:** {latest['Close']:.1f} 円 | **25日乖離率:** {latest['Deviation_Rate']:.2f} %")

            # 4. グラフの作成 (ここで fig が定義されます)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})

            ax1.plot(df.index, df['Close'], label='Price', color='#1f77b4', linewidth=2)
            ax1.plot(df.index, df['SMA25'], label='25MA', color='#ff7f0e', linestyle='--')
            ax1.plot(df.index, df['Upper_2sigma'], label='+2σ', color='#d62728', linestyle=':', alpha=0.6)
            ax1.plot(df.index, df['Lower_2sigma'], label='-2σ', color='#2ca02c', linestyle=':', alpha=0.6)
            ax1.fill_between(df.index, df['Upper_2sigma'], df['Lower_2sigma'], color='gray', alpha=0.1)

            ax1.set_title(f"{company_name} ({ticker_code}) - Analysis", fontsize=16, fontweight='bold')
            ax1.set_ylabel("Price (JPY)")
            ax1.legend(loc='upper left')
            ax1.grid(True, linestyle='--', alpha=0.5)

            ax2.plot(df.index, df['Deviation_Rate'], label='Deviation (%)', color='#9467bd')
            ax2.axhline(0, color='black', linewidth=1)
            ax2.axhline(-10, color='red', linestyle='--', alpha=0.5)
            ax2.axhline(10, color='red', linestyle='--', alpha=0.5)
            ax2.set_title("25-Day Moving Average Deviation Rate", fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()

            # 5. Streamlitの画面にグラフを表示
            st.pyplot(fig)

            # 6. おまけ: 最新データの表も表示
            st.write("▼ 最新のデータ")
            st.dataframe(df.tail())

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")