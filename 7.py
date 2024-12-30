import string
from cmath import pi
import streamlit as st
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import re
import pandas as pd
import plotly.express as px
import altair as alt

# 函数用于从指定URL获取文本内容，并进行初步清理
def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # 移除文本中的标点符号
        text = text.translate(str.maketrans("", "", string.punctuation))
        # 将所有多余的空白字符替换为单个空格，并去除首尾空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return ""

# 对给定的文本进行分词，并统计出现频率最高的前top_n个词语
def word_frequency(text, top_n=20):
    words = [word for word in jieba.cut(text) if len(word) >= 2 and word.strip()]
    word_counts = Counter(words)
    return word_counts.most_common(top_n)

# 绘制图表的函数
def draw_chart(chart_type, data, library='Pyecharts'):
    # 根据选定的库绘制相应的图表
    if library == 'Pyecharts':
        if chart_type == "词云图":
            wc = WordCloud()
            wc.add("", data)
            return wc
        elif chart_type == "柱状图":
            bar = Bar()
            words, counts = zip(*data)
            bar.add_xaxis(list(words))
            bar.add_yaxis("词频", list(counts))
            return bar
        elif chart_type == "饼图":
            pie = Pie()
            pie.add("", data)
            return pie
        elif chart_type == "折线图":
            line = Line()
            x_data = list(range(1, len(data) + 1))
            _, counts = zip(*data)
            line.add_xaxis(x_data)
            line.add_yaxis("词频", list(counts))
            return line
        elif chart_type == "散点图":
            scatter = Scatter()
            x_data = list(range(1, len(data) + 1))
            _, counts = zip(*data)
            scatter.add_xaxis(x_data)
            scatter.add_yaxis("词频", list(counts))
            return scatter
        elif chart_type == "漏斗图":
            funnel = Funnel()
            funnel.add("词频漏斗", data, gap=2)  # 直接使用 data
            return funnel
        elif chart_type == "雷达图":
            radar = Radar()
            max_count = max([count for _, count in data])
            c_schema = [{"name": word, "max": max_count} for word, _ in data]
            radar.add_schema(schema=c_schema)
            data = [{"name": word, "value": [count]} for word, count in data]
            radar.add("词频雷达", data)
            return radar

    elif library == 'Plotly':
        df = pd.DataFrame(data, columns=['words', 'counts'])
        if chart_type == "词云图":
            fig = px.scatter(df, x='words', y='counts', size='counts', hover_data=['words'])
        elif chart_type == "柱状图":
            fig = px.bar(df, x='words', y='counts')
        elif chart_type == "饼图":
            fig = px.pie(df, names='words', values='counts')
        elif chart_type == "折线图":
            fig = px.line(df, x='words', y='counts')
        elif chart_type == "散点图":
            fig = px.scatter(df, x='words', y='counts')
        elif chart_type == "漏斗图":
            fig = px.funnel(df, x='counts', y='words')
        elif chart_type == "雷达图":
            # Create a DataFrame with the necessary structure for a radar chart
            labels = {'words': '指标', 'counts': '值'}
            fig = px.line_polar(df, r='counts', theta='words', line_close=True, labels=labels)
            fig.update_traces(fill='toself')
        return fig

    elif library == 'Altair':
        df = pd.DataFrame(data, columns=['words', 'counts'])
        if chart_type == "词云图":
            chart = alt.Chart(df).mark_circle().encode(
                alt.X('words:N'),
                alt.Y('counts:Q'),
                size='counts',
                tooltip=['words']
            )
        elif chart_type == "柱状图":
            chart = alt.Chart(df).mark_bar().encode(
                x='words:N',
                y='counts:Q'
            )
        elif chart_type == "饼图":
            chart = alt.Chart(df).mark_arc().encode(
                theta='counts:Q',
                color='words:N'
            )
        elif chart_type == "折线图":
            chart = alt.Chart(df).mark_line().encode(
                x='words:N',
                y='counts:Q'
            )
        elif chart_type == "散点图":
            chart = alt.Chart(df).mark_point().encode(
                x='words:N',
                y='counts:Q'
            )
        elif chart_type == "漏斗图":
            chart = alt.Chart(df).transform_window(
                cumulative_count='sum(counts)',
                sort=[alt.SortField('counts', order='descending')]
            ).mark_bar().encode(
                x=alt.X('cumulative_count:Q', axis=alt.Axis(title='累计数量')),
                y=alt.Y('words:N', axis=alt.Axis(title='词语'), sort=alt.SortField(field='counts', order='descending'))
            )
        elif chart_type == "雷达图":
            # Prepare data for radar chart
            df_radar = df.assign(angle=lambda d: (d.index / len(df)) * 2 * pi)
            chart = alt.Chart(df_radar).mark_line().encode(
                x=alt.X('counts:Q', scale=alt.Scale(type='sqrt')),
                y=alt.Y('angle:Q', scale=alt.Scale(domain=[0, 2 * pi], type='linear'), axis=None),
                order='angle:Q',
                tooltip='words:N'
            ).properties(width=400, height=400)
        return chart

st.title("网页文本词频分析与可视化")

# 用户界面配置
url = st.sidebar.text_input("请输入文章URL")
selected_library = st.sidebar.selectbox("请选择可视化库", ["Pyecharts", "Plotly", "Altair"])
chart_type = st.sidebar.button("请选择图表类型", ["词云图", "柱状图", "饼图", "折线图", "散点图", "漏斗图", "雷达图"], index=0)

if url:
    text = get_text_from_url(url)
    if text:
        word_counts = word_frequency(text)
        min_frequency = st.sidebar.slider("设置最低词频阈值", 1, min([count for _, count in word_counts]), 1)
        filtered_word_counts = [(word, count) for word, count in word_counts if count >= min_frequency]

        chart = draw_chart(chart_type, filtered_word_counts, selected_library)

        if selected_library in ['Plotly', 'Altair']:
            st.write(chart)
        else:
            st.components.v1.html(chart.render_embed(), height=600)
    else:
        st.sidebar.error("无法获取网页内容，请检查URL是否正确")
else:
    st.sidebar.warning("请输入有效的文章URL")