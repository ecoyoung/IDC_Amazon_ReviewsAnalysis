# Amazon评论分析工具
这是一个用于分析Amazon产品评论的应用程序。
开发团队：海翼IDC
数据源：Shulex批量提取的评论
格式：.XLSX

## 功能特点

- 数据预处理：
  - 支持Excel文件上传
  - 保留关键列：Asin, Title, Content, Model, Rating, Date
  - 自动添加ID列用于评论排序
  - 导出处理后的数据为新的Excel文件

## 安装说明
1. 安装所需依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
streamlit run app.py
```

## 使用说明

1. 启动应用后
2. 点击"浏览文件"上传Excel文件
3. 点击“数据处理”，处理数据并显示结果将保留Asin、Title、Content、Model、Rating、Rating、Date ，同时根据Rating对评论进行分类，列名为Review Type，如果Rating为4或5则为positive，3则为neutral，2或者1则为negtive,并新增一列ID列放在第一列，用来定位评论
4. 可以点击"下载处理后的数据"按钮导出处理后的文件，格式允许TXT和EXCEL；两种格式，除了下载所有评论外，同时可以下载positive或者negtive等

## 输入文件要求
Excel文件包含以下列：
- Asin
- Title
- Content
- Model
- Rating
- Date 