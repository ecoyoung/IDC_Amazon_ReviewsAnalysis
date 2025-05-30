import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="Amazon评论分析 - 词云分析",
    page_icon="☁️",
    layout="wide"
)

import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import plotly.graph_objects as go
import json
import os
import io

# 添加自定义CSS样式 - 更新下载按钮为蓝色系
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #A23B72;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .stats-card {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .section-title {
        color: #2E86AB;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #2E86AB !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #1C6E9C !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    /* 更新下载按钮为蓝色系 */
    .download-button>button {
        background-color: #2E86AB !important;
        color: white !important;
    }
    .download-button>button:hover {
        background-color: #1C6E9C !important;
    }
    .negative-words-list {
        background-color: #e7f3ff;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 4px solid #2E86AB;
    }
    .wordcloud-container {
        display: flex;
        justify-content: center;
        padding: 1.5rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .download-container {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_stop_words():
    """加载停用词"""
    # 基础英文停用词
    stop_words = {
        # 人称代词
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
        "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself',
        'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        
        # 疑问词和指示词
        'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
        'where', 'when', 'why', 'how', 'whose',
        
        # 常见动词和助动词
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'shall',
        'should', 'can', 'could', 'may', 'might', 'must', 'ought', 'need', 'dare',
        
        # 介词和连词
        'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
        'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each',
        
        # 常见副词和形容词
        'just', 'now', 'only', 'very', 'really', 'quite', 'rather', 'somewhat',
        'more', 'most', 'much', 'many', 'some', 'such', 'no', 'nor', 'not',
        'too', 'very', 'same', 'different', 'other', 'another', 'like', 'unlike',
        
        # 时间相关词
        'today', 'tomorrow', 'yesterday', 'now', 'later', 'earlier', 'soon',
        'already', 'yet', 'still', 'always', 'never', 'ever', 'often', 'sometimes',
        
        # 数量词和序数词
        'one', 'two', 'three', 'first', 'second', 'third', 'next', 'last',
        'few', 'several', 'many', 'much', 'more', 'most', 'own', 'every',
        
        # 其他常见词
        'yes', 'no', 'maybe', 'ok', 'okay', 'right', 'wrong', 'well', 'anyway',
        'however', 'although', 'though', 'despite', 'unless', 'whereas',
        'whether', 'whatever', 'whoever', 'whenever', 'wherever', 'however',
        
        # 网络用语和缩写
        'lol', 'omg', 'idk', 'tbh', 'imo', 'imho', 'fyi', 'asap', 'aka'
    }
    
    # 添加一些自定义停用词（与产品评论相关）
    custom_stop_words = {
        # 评论常用词
        'would', 'could', 'get', 'use', 'using', 'used', 'recommend',
        'recommended', 'definitely', 'probably', 'maybe', 'think', 'thought',
        'seems', 'looked', 'looks', 'looking', 'came', 'come', 'goes', 'going',
        'got', 'getting', 'make', 'makes', 'made', 'making',
        
        # 时间和状态
        'day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years',
        'time', 'times', 'ago', 'since', 'far', 'long', 'short',
        
        # 评分相关
        'star', 'stars', 'rating', 'rated', 'review', 'reviews', 'reviewed'
    }
    
    return stop_words.union(custom_stop_words)

def load_negative_words():
    """从文件加载否定词列表"""
    if os.path.exists('negative_words.json'):
        with open('negative_words.json', 'r') as f:
            return set(json.load(f))
    return set()

def save_negative_words(words):
    """保存否定词列表到文件"""
    with open('negative_words.json', 'w') as f:
        json.dump(list(words), f)

def process_text(text, stop_words, negative_words):
    """处理文本，提取词语"""
    if pd.isna(text):
        return []
    
    # 转换为小写并分词
    text = str(text).lower()
    # 使用正则表达式分词，保留字母和数字
    words = re.findall(r'\b[a-z0-9]+\b', text)
    
    # 过滤词
    filtered_words = [word for word in words 
                     if word not in stop_words 
                     and word not in negative_words
                     and len(word) > 2]  # 移除过短的词
    
    return filtered_words

def create_wordcloud(text_data, negative_words):
    """创建词云图"""
    wordcloud = WordCloud(
        width=1600,
        height=800,
        background_color='white',
        max_words=150,
        stopwords=negative_words
    ).generate_from_frequencies(text_data)
    
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig, wordcloud

def save_wordcloud_to_png(wordcloud):
    """保存词云图为PNG格式"""
    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def create_word_freq_table(word_freq, top_n=50):
    """创建词频统计表"""
    df = pd.DataFrame(list(word_freq.items()), columns=['Word', 'Frequency'])
    df = df.sort_values('Frequency', ascending=False).head(top_n)
    
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=['词语', '频率'],
                fill_color='#2E86AB',
                font=dict(color='white', size=14),
                align='center'
            ),
            cells=dict(
                values=[df['Word'], df['Frequency']],
                fill_color='#fafafa',
                align='center',
                font=dict(size=13)
            )
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=600
    )
    
    return fig

def main():
    # 页面标题
    st.markdown('<div class="main-header">☁️ Amazon评论分析 - 词云分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">评论文本分析与词云图生成</div>', unsafe_allow_html=True)
    
    # 加载停用词和否定词
    stop_words = load_stop_words()
    negative_words = load_negative_words()
    
    # 文件上传卡片
    st.markdown("### 📤 上传数据文件")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "选择预处理后的Excel文件", 
            type=['xlsx'],
            help="请确保文件包含必要的列：ID, Asin, Title, Content, Model, Rating, Date, Review Type"
        )
        st.markdown('</div>', unsafe_allow_html=True)
            
    if uploaded_file is not None:
        try:
            with st.spinner('正在加载数据...'):
                df = pd.read_excel(uploaded_file)
            
            # 验证文件格式
            required_columns = ['Content', 'Review Type']
            if not all(col in df.columns for col in required_columns):
                st.error("❌ 请上传包含Content和Review Type列的预处理文件！")
                return
            
            st.success(f"✅ 文件上传成功！共 {len(df)} 条评论")
            
            # 选择评论类型
            st.markdown("### 🔍 选择分析范围")
            review_type = st.selectbox(
                "选择要分析的评论类型",
                ["所有评论", "Positive评论", "Negative评论", "Neutral评论"],
                index=0
            )
            
            # 根据选择筛选数据
            if review_type == "Positive评论":
                filtered_df = df[df['Review Type'].str.lower() == 'positive']
            elif review_type == "Negative评论":
                filtered_df = df[df['Review Type'].str.lower() == 'negative']
            elif review_type == "Neutral评论":
                filtered_df = df[df['Review Type'].str.lower() == 'neutral']
            else:
                filtered_df = df
            
            # 显示筛选后的数据量
            st.info(f"筛选出 **{len(filtered_df)}** 条 **{review_type}**")
            
            # 否定词管理卡片
            st.markdown("### 🚫 否定词管理")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ➕ 添加否定词")
                    new_negative_word = st.text_input("输入要添加的否定词", placeholder="例如：amazon, product", key="add_input")
                    if st.button("添加否定词", key="add_word") and new_negative_word:
                        negative_words.add(new_negative_word.lower())
                        save_negative_words(negative_words)
                        st.success(f"✅ 已添加否定词: **{new_negative_word}**")
                
                with col2:
                    st.markdown("#### ❌ 删除否定词")
                    if negative_words:
                        word_to_remove = st.selectbox("选择要删除的否定词", list(negative_words), key="remove_word")
                        if st.button("删除否定词", key="remove_btn"):
                            negative_words.remove(word_to_remove)
                            save_negative_words(negative_words)
                            st.success(f"✅ 已删除否定词: **{word_to_remove}**")
                    else:
                        st.info("当前没有设置否定词")
                
                # 显示当前否定词列表
                st.markdown("#### 📝 当前否定词列表")
                if negative_words:
                    # 使用英文逗号分隔，避免显示问题
                    st.markdown(f'<div class="negative-words-list">{", ".join(sorted(negative_words))}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.info("当前没有设置否定词")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 生成词云图按钮
            if st.button("☁️ 生成词云图", key="analyze", type="primary", use_container_width=True):
                with st.spinner('正在处理评论内容...'):
                    all_words = []
                    progress_bar = st.progress(0)
                    total = len(filtered_df)
                    
                    # 添加进度条更新逻辑
                    for i, text in enumerate(filtered_df['Content']):
                        words = process_text(text, stop_words, negative_words)
                        all_words.extend(words)
                        
                        # 每处理10条更新一次进度条
                        if i % 10 == 0 or i == total - 1:
                            progress_bar.progress((i + 1) / total)
                    
                    # 计算词频
                    word_freq = Counter(all_words)
                
                if word_freq:
                    st.success(f"✅ 分析完成！共提取 {len(word_freq)} 个有效词汇")
                    
                    # 显示统计卡片
                    st.markdown("### 📊 分析统计")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">评论总数</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{len(df)}</h2>
                            <p style="color: #666; margin: 0;">包含所有类型评论</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">分析评论</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{len(filtered_df)}</h2>
                            <p style="color: #666; margin: 0;">{review_type}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">有效词汇</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{len(word_freq)}</h2>
                            <p style="color: #666; margin: 0;">过滤后关键词</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 词云图展示
                    st.markdown("### ☁️ 词云图")
                    with st.container():
                        st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
                        wordcloud_fig, wordcloud = create_wordcloud(word_freq, negative_words)
                        st.pyplot(wordcloud_fig)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 添加词云图下载按钮（使用自定义类名）
                        wordcloud_png = save_wordcloud_to_png(wordcloud)
                        review_type_text = review_type.replace("评论", "").lower()
                        st.download_button(
                            label="📥 下载词云图",
                            data=wordcloud_png,
                            file_name=f"amazon_wordcloud_{review_type_text}.png",
                            mime="image/png",
                            key="download_wordcloud"
                        )
                    
                    # 词频统计表
                    st.markdown("### 📋 词频统计表")
                    with st.expander("点击展开/收起词频统计表", expanded=True):
                        freq_table = create_word_freq_table(word_freq)
                        st.plotly_chart(freq_table, use_container_width=True)
                        
                        # 添加统计表下载按钮（使用自定义类名）
                        df_freq = pd.DataFrame(list(word_freq.items()), columns=['词语', '频率'])
                        df_freq = df_freq.sort_values('频率', ascending=False)
                        csv = df_freq.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 下载词频数据(CSV)",
                            data=csv,
                            file_name=f"amazon_word_frequency_{review_type_text}.csv",
                            mime="text/csv",
                            key="download_csv"
                        )
                else:
                    st.warning("⚠️ 没有找到符合条件的词语，请调整分析条件或检查数据。")
        
        except Exception as e:
            st.error(f"❌ 处理文件时出错: {str(e)}")
    else:
        st.info("ℹ️ 请上传预处理后的Excel文件开始分析")

if __name__ == "__main__":
    main()