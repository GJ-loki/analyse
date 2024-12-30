# 导入必要的模块和库
import string  # 提供字符串操作方法
from cmath import pi  # 引入复数数学函数中的pi常量（注意：对于实际数值计算应使用math.pi）
import streamlit as st  # Streamlit用于创建Web应用界面
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar  # Pyecharts用于生成各种类型的图表
import requests  # 用于发送HTTP请求获取网页内容
from bs4 import BeautifulSoup  # Beautiful Soup用于解析HTML文档
import jieba  # Jieba用于中文分词
from collections import Counter  # Counter用于统计词频
import re  # 正则表达式用于字符串处理
import pandas as pd  # Pandas用于数据处理
import plotly.express as px  # Plotly Express用于快速绘制交互式图表
import altair as alt  # Altair用于创建声明式的统计可视化

# 定义一个函数，从给定的URL中提取文本内容并进行初步清理
def get_text_from_url(url):
    try:
        response = requests.get(url)  # 发送GET请求获取网页内容
        response.raise_for_status()  # 如果响应状态码不是200，则抛出异常
        soup = BeautifulSoup(response.text, 'html.parser')  # 解析HTML文档
        text = soup.get_text()  # 获取纯文本内容

        # 移除文本中的标点符号
        text = text.translate(str.maketrans("", "", string.punctuation))
        # 将所有多余的空白字符替换为单个空格，并去除首尾空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text  # 返回清理后的文本
    except requests.RequestException as e:  # 捕获请求异常
        print(f"请求出错: {e}")  # 打印错误信息
        return ""  # 如果发生错误，返回空字符串

# 定义一个函数，对给定的文本进行分词，并统计出现频率最高的前top_n个词语
def word_frequency(text, top_n=20):
    words = [word for word in jieba.cut(text) if len(word) >= 2 and word.strip()]  # 分词并过滤掉长度小于2或为空的词语
    word_counts = Counter(words)  # 统计每个词语出现的次数
    return word_counts.most_common(top_n)  # 返回出现频率最高的top_n个词语及其对应的次数

# 定义一个函数，根据用户的选择绘制不同类型的图表
def draw_chart(chart_type, data, library='Pyecharts'):
    # 根据选定的库绘制相应的图表
    if library == 'Pyecharts':
        # 使用Pyecharts库绘制不同类型的图表...
        pass  # 这里省略了具体的实现，因为它们已经在您的代码中定义好了
    elif library == 'Plotly':
        df = pd.DataFrame(data, columns=['words', 'counts'])  # 将数据转换成Pandas DataFrame
        # 使用Plotly库绘制不同类型的图表...
        pass  # 同上
    elif library == 'Altair':
        df = pd.DataFrame(data, columns=['words', 'counts'])  # 将数据转换成Pandas DataFrame
        # 使用Altair库绘制不同类型的图表...
        pass  # 同上

# Streamlit 应用程序的主界面配置
st.title("网页文本词频分析与可视化")  # 设置页面标题

# 用户界面配置部分
url = st.sidebar.text_input("请输入文章URL")  # 创建一个侧边栏输入框让用户输入文章的URL
selected_library = st.sidebar.selectbox("请选择可视化库", ["Pyecharts", "Plotly", "Altair"])  # 创建下拉菜单让用户选择可视化库

# 注意：这里原代码中的chart_type变量赋值方式是不正确的，st.sidebar.button不会接受列表作为参数。
# 我们应该使用selectbox或者radio等组件来创建一个可选择的选项列表。
chart_type = st.sidebar.radio("请选择图表类型", ["词云图", "柱状图", "饼图", "折线图", "散点图", "漏斗图", "雷达图"], index=0)

if url:  # 如果用户提供了有效的URL
    text = get_text_from_url(url)  # 调用get_text_from_url函数获取并清理文本
    if text:  # 如果成功获取到文本
        word_counts = word_frequency(text)  # 计算词频
        min_frequency = st.sidebar.slider("设置最低词频阈值", 1, min([count for _, count in word_counts]), 1)  # 创建滑块让用户设定最低词频阈值
        filtered_word_counts = [(word, count) for word, count in word_counts if count >= min_frequency]  # 筛选符合条件的词频

        chart = draw_chart(chart_type, filtered_word_counts, selected_library)  # 调用draw_chart函数绘制图表

        if selected_library in ['Plotly', 'Altair']:  # 如果选择了Plotly或Altair库
            st.write(chart)  # 直接显示图表
        else:  # 对于其他库（如Pyecharts）
            st.components.v1.html(chart.render_embed(), height=600)  # 渲染并嵌入图表
    else:
        st.sidebar.error("无法获取网页内容，请检查URL是否正确")  # 如果未能成功获取文本，显示错误信息
else:
    st.sidebar.warning("请输入有效的文章URL")  # 如果用户没有提供URL，提示他们输入