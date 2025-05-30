import streamlit as st

# 设置页面配置必须是第一个st命令
st.set_page_config(
    page_title="Amazon评论分析 - 关键词匹配",
    page_icon="🔍",
    layout="wide"
)

import pandas as pd
import json
import os
from collections import defaultdict

# 预设人群类别和关键词
PRESET_CATEGORIES = {
    "儿童或青少年": "kids,girl,girls,boy,boys,children,teen,picky eater,child-friendly,baby,sugar coating,candy-like,my daughter,my son",
    "孕妇或哺乳期女性": "pregnant,pregnancy,nursing,breastfeeding,menstrual,period,hormonal support,prenatal,postpartum,label says do not use during pregnancy",
    "素食者或健康饮食者": "vegan,vegetarian,plant-based,no artificial,no gluten,no high fructose corn syrup,organic,non-GMO,natural ingredients,sugar-free,low sugar,stevia",
    "健身运动人群": "fitness,exercise,training,athlete,workout,gym,sports,muscle,strength,endurance,protein,Boosts endurance,Boosts strength"
}

def load_categories():
    """从文件加载已保存的类别和关键词"""
    if os.path.exists('categories.json'):
        with open('categories.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_categories(categories):
    """保存类别和关键词到文件"""
    with open('categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def match_keywords(text, keywords):
    """检查文本是否包含关键词列表中的任何词"""
    if pd.isna(text):
        return False
    text = str(text).lower()
    return any(keyword.lower().strip() in text for keyword in keywords)

def analyze_reviews(df, categories):
    """分析评论并进行分类"""
    # 创建结果DataFrame，保留ID列
    results = pd.DataFrame()
    results['ID'] = df['ID']  # 保留原始ID
    results['Content'] = df['Content']
    results['Original Review Type'] = df['Review Type']
    
    # 为每个类别创建一列
    for category in categories:
        keywords = [k.strip() for k in categories[category].split(',')]
        results[f'Is {category}'] = df['Content'].apply(
            lambda x: match_keywords(x, keywords)
        )
    
    # 统计每个类别的匹配数量
    stats = {}
    for category in categories:
        matched = results[f'Is {category}'].sum()
        stats[category] = {
            'matched': int(matched),
            'percentage': round(matched / len(df) * 100, 2)
        }
    
    return results, stats

def main():
    # 页面标题和样式
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
    .category-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .preset-category {
        background-color: #e7f3ff;
        border-left: 4px solid #2E86AB;
    }
    .stats-card {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🔍 Amazon评论分析 - 关键词匹配</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于关键词匹配的评论分类分析工具</div>', unsafe_allow_html=True)
    
    # 加载已保存的类别
    categories = load_categories()
    
    # 侧边栏：预设类别快速导入
    with st.sidebar:
        st.markdown("### 🎯 预设类别")
        st.markdown("---")
        
        for preset_name, preset_keywords in PRESET_CATEGORIES.items():
            with st.container():
                st.markdown(f"**{preset_name}**")
                
                # 显示关键词预览
                preview_keywords = preset_keywords.split(',')[:5]
                preview_text = ', '.join(preview_keywords)
                if len(preset_keywords.split(',')) > 5:
                    preview_text += f"... (共{len(preset_keywords.split(','))}个关键词)"
                
                st.markdown(f"<small style='color: #666;'>{preview_text}</small>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"一键导入", key=f"import_{preset_name}"):
                        categories[preset_name] = preset_keywords
                        save_categories(categories)
                        st.success("导入成功！")
                        st.rerun()
                
                with col2:
                    if preset_name in categories:
                        st.markdown("✅ 已导入")
                    else:
                        st.markdown("⭕ 未导入")
                
                st.markdown("---")
    
    # 主要内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 类别管理")
        
        # 添加新类别
        with st.container():
            st.markdown("#### 手动添加自定义类别")
            col_input, col_btn = st.columns([3, 1])
            
            with col_input:
                new_category = st.text_input("输入类别名称", placeholder="例如：慢性病老年人、孕期女性用户等")
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
                if st.button("添加类别", type="primary") and new_category:
                    if new_category not in categories:
                        categories[new_category] = ""
                        save_categories(categories)
                        st.success(f"✅ 已添加类别: {new_category}")
                        st.rerun()
                    else:
                        st.warning("⚠️ 该类别已存在！")
    
    with col2:
        if categories:
            st.markdown("### 📊 当前统计")
            st.metric("已配置类别", len(categories))
            
            # 显示类别概览
            category_summary = []
            for cat, keywords in categories.items():
                keyword_count = len([k for k in keywords.split(',') if k.strip()]) if keywords else 0
                category_summary.append({"类别": cat, "关键词数": keyword_count})
            
            if category_summary:
                summary_df = pd.DataFrame(category_summary)
                st.dataframe(summary_df, use_container_width=True)
    
    # 显示和编辑现有类别
    if categories:
        st.markdown("### ✏️ 编辑类别和关键词")
        
        edited_categories = {}
        
        for category in categories:
            # 判断是否为预设类别
            is_preset = category in PRESET_CATEGORIES
            card_class = "category-card preset-category" if is_preset else "category-card"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 6, 1])
            
            with col1:
                if is_preset:
                    st.markdown(f"**🎯 {category}**")
                    st.markdown("<small style='color: #2E86AB;'>预设类别</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**📝 {category}**")
                    st.markdown("<small style='color: #666;'>自定义类别</small>", unsafe_allow_html=True)
            
            with col2:
                keywords = st.text_area(
                    "关键词（用逗号分隔）",
                    value=categories[category],
                    key=f"keywords_{category}",
                    help="输入多个关键词，用逗号分隔。支持英文西语关键词。",
                    height=80
                )
                edited_categories[category] = keywords
                
                # 显示关键词统计
                if keywords:
                    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                    st.markdown(f"<small style='color: #666;'>共 {len(keyword_list)} 个关键词</small>", 
                              unsafe_allow_html=True)
            
            with col3:
                st.markdown("<br><br>", unsafe_allow_html=True)  # 对齐按钮
                if st.button("🗑️", key=f"delete_{category}", help="删除此类别"):
                    del categories[category]
                    save_categories(categories)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 如果关键词有修改，保存更新
        if edited_categories != categories:
            categories = edited_categories
            save_categories(categories)
        
        # 文件上传和分析
        st.markdown("---")
        st.markdown("### 📊 评论分析")
        
        uploaded_file = st.file_uploader(
            "选择预处理后的Excel文件", 
            type=['xlsx'],
            help="请上传包含ID、Content和Review Type列的Excel文件"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner('正在处理文件...'):
                    df = pd.read_excel(uploaded_file)
                
                # 验证文件格式
                required_columns = ['ID', 'Content', 'Review Type']
                if not all(col in df.columns for col in required_columns):
                    st.error("❌ 请上传包含ID、Content和Review Type列的预处理文件！")
                    return
                
                st.success(f"✅ 文件上传成功！共 {len(df)} 条评论")
                
                # 分析评论
                with st.spinner('正在分析评论...'):
                    results, stats = analyze_reviews(df, categories)
                
                # 显示统计信息
                st.markdown("### 📈 匹配统计结果")
                
                # 创建美观的统计卡片
                cols = st.columns(min(len(stats), 4))
                for i, (category, stat) in enumerate(stats.items()):
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4 style="color: #2E86AB; margin: 0;">{category}</h4>
                            <h2 style="color: #A23B72; margin: 0.5rem 0;">{stat['matched']}</h2>
                            <p style="color: #666; margin: 0;">匹配率: {stat['percentage']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 详细统计表格
                stats_df = pd.DataFrame([
                    {
                        '类别': category,
                        '匹配数量': stats[category]['matched'],
                        '匹配比例': f"{stats[category]['percentage']}%",
                        '未匹配数量': len(df) - stats[category]['matched']
                    }
                    for category in stats
                ])
                
                st.markdown("#### 📋 详细统计表")
                st.dataframe(stats_df, use_container_width=True)
                
                # 显示详细结果
                st.markdown("### 📄 详细分析结果")
                
                # 添加筛选选项
                col1, col2 = st.columns(2)
                with col1:
                    show_all = st.checkbox("显示所有记录", value=True)
                
                with col2:
                    if not show_all:
                        selected_category = st.selectbox(
                            "选择要查看的类别",
                            options=list(categories.keys())
                        )
                
                # 根据筛选条件显示结果
                if show_all:
                    st.dataframe(results, use_container_width=True)
                else:
                    filtered_results = results[results[f'Is {selected_category}'] == True]
                    st.dataframe(filtered_results, use_container_width=True)
                    st.info(f"显示 {len(filtered_results)} 条匹配 '{selected_category}' 的记录")
                

                
            except Exception as e:
                st.error(f"❌ 处理文件时出错: {str(e)}")
    else:
        st.info("👆 请先从侧边栏导入预设类别或添加自定义类别")

if __name__ == "__main__":
    main()