import streamlit as st
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
import requests
from bs4 import BeautifulSoup
import jieba
import re
from collections import Counter

# 用于获取网页文本内容的函数
def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # 提取所有文本内容，可根据实际情况调整提取更精准的文本部分
        text = soup.get_text()
        return text
    except:
        return None

# 对文本进行分词和词频统计的函数
def word_frequency(text, top_n=20):
    words = jieba.cut(text)
    words = [word for word in words if len(word) > 1 and re.match(r'[\u4e00-\u9fa5a-zA-Z0-9]+', word)]
    word_counts = Counter(words)
    return word_counts.most_common(top_n)

# 绘制词云图
def draw_wordcloud(word_frequency_data):
    wordcloud = WordCloud()
    data = [(word, count) for word, count in word_frequency_data]
    wordcloud.add("", data)
    return wordcloud

# 绘制柱状图
def draw_bar(word_frequency_data):
    bar = Bar()
    words, counts = zip(*word_frequency_data)
    bar.add_xaxis(list(words))
    bar.add_yaxis("词频", list(counts))
    return bar

# 绘制饼图
def draw_pie(word_frequency_data):
    pie = Pie()
    words, counts = zip(*word_frequency_data)
    pie.add("", [list(z) for z in zip(words, counts)])
    return pie

# 绘制折线图（示例，这里以词频顺序为x轴，词频数值为y轴，可能实际意义不大，可按需调整）
def draw_line(word_frequency_data):
    line = Line()
    x_data = list(range(1, len(word_frequency_data) + 1))
    _, counts = zip(*word_frequency_data)
    line.add_xaxis(x_data)
    line.add_yaxis("词频", list(counts))
    return line

# 绘制散点图（示例，以词频顺序为x轴，词频数值为y轴，可能实际意义不大，可按需调整）
def draw_scatter(word_frequency_data):
    scatter = Scatter()
    x_data = list(range(1, len(word_frequency_data) + 1))
    _, counts = zip(*word_frequency_data)
    scatter.add_xaxis(x_data)
    scatter.add_yaxis("词频", list(counts))
    return scatter

# 绘制漏斗图（示例，根据词频构建，可能需要根据实际情况合理展示）
def draw_funnel(word_frequency_data):
    funnel = Funnel()
    words, counts = zip(*word_frequency_data)
    funnel.add("词频漏斗", [list(z) for z in zip(words, counts)], gap=2)
    return funnel

# 绘制雷达图（示例，简单构造维度，可能需根据实际情况更好设计）
# 绘制雷达图（适配新版本的pyecharts）
# 绘制雷达图（适配新版本的pyecharts）
def draw_radar(word_frequency_data):
    radar = Radar()
    max_count = max([count for _, count in word_frequency_data])
    c_schema = [{"name": "词频", "max": max_count}]
    radar.add_schema(schema=c_schema)

    # 将数据整理成符合要求的格式
    data = []
    words, counts = zip(*word_frequency_data)
    for index in range(len(words)):
        data.append({"name": words[index], "value": [counts[index]]})

    radar.add("词频雷达", data)
    return radar


st.title("网页文本词频分析与可视化")

# 侧边栏输入URL
url = st.sidebar.text_input("请输入文章URL")
if url:
    text = get_text_from_url(url)
    if text:
        # 分词与词频统计
        word_frequency_data = word_frequency(text)
        # 过滤低频词（可通过交互设置阈值等方式来完善，这里简单示例）
        min_frequency = st.sidebar.slider("设置最低词频阈值", 1, min([count for _, count in word_frequency_data]), 1)
        filtered_word_frequency_data = [(word, count) for word, count in word_frequency_data if count >= min_frequency]
        # 选择图形类型
        chart_type = st.sidebar.selectbox("选择可视化图表类型", ["词云图", "柱状图", "饼图", "折线图", "散点图", "漏斗图", "雷达图"])
        if chart_type == "词云图":
            chart = draw_wordcloud(filtered_word_frequency_data)
        elif chart_type == "柱状图":
            chart = draw_bar(filtered_word_frequency_data)
        elif chart_type == "饼图":
            chart = draw_pie(filtered_word_frequency_data)
        elif chart_type == "折线图":
            chart = draw_line(filtered_word_frequency_data)
        elif chart_type == "散点图":
            chart = draw_scatter(filtered_word_frequency_data)
        elif chart_type == "漏斗图":
            chart = draw_funnel(filtered_word_frequency_data)
        elif chart_type == "雷达图":
            chart = draw_radar(filtered_word_frequency_data)
        st.components.v1.html(chart.render_embed(), height=600)
    else:
        st.sidebar.error("无法获取网页内容，请检查URL是否正确")
else:
    st.sidebar.warning("请输入有效的文章URL")
