import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

def process_data(df):
    """数据预处理函数"""
    # 确保所需列存在
    required_columns = ['Asin', 'Title', 'Content', 'Model', 'Rating', 'Date']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"缺少必要的列: {col}")
            return None
    
    # 数据预处理
    # 1. 只保留必要的列
    df = df[required_columns].copy()
    
    # 2. 清理数据
    # 处理Rating列，确保为数值类型
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    # 处理日期列，确保为日期类型
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 清理文本列中的空白字符
    text_columns = ['Title', 'Content', 'Model']
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # 3. 添加ID列
    df.insert(0, 'ID', range(1, len(df) + 1))
    
    # 4. 添加Review Type列
    def get_review_type(rating):
        try:
            rating = float(rating)
            if rating >= 4:
                return 'positive'
            elif rating == 3:
                return 'neutral'
            else:
                return 'negative'
        except:
            return 'unknown'
    
    df['Review Type'] = df['Rating'].apply(get_review_type)
    
    # 5. 重新排序列
    column_order = ['ID', 'Asin', 'Title', 'Content', 'Model', 'Rating', 'Date', 'Review Type']
    df = df[column_order]
    
    return df

def calculate_review_stats(df):
    """计算评论类型的统计信息"""
    # 计算各类型数量
    review_counts = df['Review Type'].value_counts()
    
    # 计算百分比
    review_percentages = (review_counts / len(df) * 100).round(2)
    
    # 合并统计信息
    stats_df = pd.DataFrame({
        '数量': review_counts,
        '占比(%)': review_percentages
    })
    
    return stats_df, review_counts, review_percentages

def create_pie_chart(review_counts, title='评论类型分布'):
    """创建饼图"""
    fig = px.pie(
        values=review_counts.values,
        names=review_counts.index,
        title=title,
        color_discrete_map={
            'positive': '#2ECC71',
            'neutral': '#F1C40F',
            'negative': '#E74C3C',
            'unknown': '#95A5A6'
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def analyze_by_group(df, group_by):
    """按指定字段进行分组分析"""
    if isinstance(group_by, list):
        # 创建组合键
        df['Group'] = df['Asin'] + ' - ' + df['Model']
        # 按组合维度计算统计信息
        group_stats = df.groupby('Group').agg({
            'Rating': ['count', 'mean', 'std'],
            'Review Type': lambda x: x.value_counts().to_dict()
        }).round(2)
        
        # 计算组合维度的评分分布
        rating_dist = df.groupby(['Group', 'Rating']).size().unstack(fill_value=0)
        rating_dist_pct = rating_dist.div(rating_dist.sum(axis=1), axis=0) * 100
        
        group_by_trend = 'Group'
    else:
        # 按ASIN维度计算统计信息
        group_stats = df.groupby('Asin').agg({
            'Rating': ['count', 'mean', 'std'],
            'Review Type': lambda x: x.value_counts().to_dict()
        }).round(2)
        
        # 计算ASIN维度的评分分布
        rating_dist = df.groupby(['Asin', 'Rating']).size().unstack(fill_value=0)
        rating_dist_pct = rating_dist.div(rating_dist.sum(axis=1), axis=0) * 100
        
        group_by_trend = 'Asin'
    
    # 重命名列
    group_stats.columns = ['评论数量', '平均评分', '标准差', '评论类型分布']
    
    return group_stats, rating_dist_pct, group_by_trend

def create_rating_trend_chart(df, group_by):
    """创建评分趋势图"""
    # 按时间和分组计算平均评分
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend_data = df.groupby(['Month', group_by])['Rating'].mean().reset_index()
    
    # 创建趋势图
    title = 'Asin-Model组合随时间的平均评分变化' if group_by == 'Group' else 'Asin随时间的平均评分变化'
    
    fig = px.line(trend_data, 
                  x='Month', 
                  y='Rating', 
                  color=group_by,
                  title=title,
                  labels={'Rating': '平均评分', 'Month': '月份'})
    
    fig.update_xaxes(tickangle=45)
    return fig

def create_rating_heatmap(rating_dist_pct, title):
    """创建评分分布热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=rating_dist_pct.values,
        x=rating_dist_pct.columns,
        y=rating_dist_pct.index,
        colorscale='RdYlGn',
        text=rating_dist_pct.round(1).values,
        texttemplate='%{text}%',
        textfont={"size": 10},
        hoverongaps=False))
    
    fig.update_layout(
        title=title,
        xaxis_title='评分',
        yaxis_title='产品',
        height=max(300, len(rating_dist_pct) * 30))
    
    return fig

def save_fig_to_html(fig, filename):
    """保存图表为HTML文件"""
    return fig.to_html()

def get_download_data(df, file_format='excel'):
    """准备下载数据"""
    if file_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        data = output.getvalue()
        return data
    else:  # txt format
        # 将DataFrame转换为格式化的文本
        output = io.StringIO()
        
        # 写入表头
        headers = df.columns.tolist()
        output.write('\t'.join(headers) + '\n')
        output.write('-' * 100 + '\n')  # 分隔线
        
        # 写入数据行
        for _, row in df.iterrows():
            # 确保所有值都转换为字符串，并处理可能的空值
            row_values = [str(val) if pd.notna(val) else '' for val in row]
            # 使用制表符分隔，这样在文本编辑器中会对齐
            output.write('\t'.join(row_values) + '\n')
        
        return output.getvalue().encode('utf-8') 