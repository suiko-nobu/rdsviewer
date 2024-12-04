import streamlit as st
import pymysql
import pandas as pd

# データベース接続設定
DB_HOST = st.secrets.APIs.DB_HOST
DB_PORT = st.secrets.APIs.DB_PORT
DB_USER = st.secrets.APIs.DB_USER
DB_PASSWORD = st.secrets.APIs.DB_PASSWORD
DB_NAME = st.secrets.APIs.DB_NAME

# 性別の英語から日本語への変換辞書
gender_translation = {
    'Male': '男性',
    'Female': '女性',
    'Prefer not to say': '答えたくない'
}

# 感情の英語から日本語への変換辞書
emotion_translation = {
    'HAPPY': '幸せ',
    'SAD': '悲しい',
    'ANGRY': '怒り',
    'CONFUSED': '困惑',
    'DISGUSTED': '嫌悪',
    'SURPRISED': '驚き',
    'CALM': '冷静',
    'FEAR': '恐怖'
}

def fetch_data(query):
    """
    データベースからデータを取得する関数
    """
    try:
        # データベース接続
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        
        # 性別情報の日本語変換
        if data:
            for row in data:
                row['gender'] = gender_translation.get(row['gender'], row['gender'])  # 英語を日本語に変換
                # 感情情報の日本語変換
                row['emotion'] = emotion_translation.get(row['emotion'], row['emotion'])  # 英語を日本語に変換
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return pd.DataFrame()
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# Streamlitアプリ
def main():
    st.title("RDSデータベースビューア")
    
    # クエリ入力
    st.sidebar.header("クエリを入力")
    query = st.sidebar.text_area("SQLクエリを入力してください", "SELECT * FROM information LIMIT 10;")
    
    if st.sidebar.button("データを取得"):
        st.write("以下のデータが取得されました:")
        data = fetch_data(query)
        if not data.empty:
            st.dataframe(data)
            # CSVダウンロードリンク
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSVをダウンロード",
                data=csv,
                file_name="data.csv",
                mime="text/csv",
            )
        else:
            st.warning("データが見つかりませんでした。")

if __name__ == "__main__":
    main()
