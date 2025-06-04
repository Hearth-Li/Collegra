# MyCerts 模块

## 概述
MyCerts 是一个面向大学生的综合证书与成就管理模块。它允许用户上传、分类、整理并导出各类成长记录，包括比赛获奖、志愿服务证明、科研项目参与、奖学金以及实习经历等。

## 功能特点
- 仪表盘统计和最近上传记录
- 支持分类的证书上传
- 带筛选和排序的列表视图
- 证书详情查看
- 个人成就档案导出功能
- 支持多种文件格式（PDF、JPG、PNG）
- 志愿服务时长追踪
- 活动日期范围支持
- 中英双语支持

## 技术集成

### 数据库设置
1. 模块使用 SQLAlchemy 进行数据库操作
2. 所需数据表：
   - certificates（存储所有证书记录）
   - users（被证书引用的用户表）

### API 接口
```python
# 主要路由
GET  /mycerts              # 仪表盘视图
GET  /mycerts/upload       # 上传表单
POST /mycerts/upload       # 处理文件上传
GET  /mycerts/list         # 列出所有证书
GET  /mycerts/detail/<id>  # 查看证书详情
GET  /mycerts/export       # 导出表单
POST /mycerts/export       # 生成导出文件
GET  /mycerts/download/<id> # 下载证书文件
```

### 集成步骤
1. 将模块添加到 Flask 应用：
```python
from MyCerts import mycerts

app.register_blueprint(mycerts)
```

2. 配置数据库：
```python
from MyCerts.models import db

db.init_app(app)
```

3. 设置文件上传目录：
```python
UPLOAD_FOLDER = 'uploads/certificates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

### 依赖项
- Flask
- Flask-SQLAlchemy
- Werkzeug
- Python-dateutil

## 文件结构
```
MyCerts/
├── __init__.py
├── models.py
├── routes.py
├── README.md
├── README_zh.md
└── prototype/
    ├── main.html
    ├── upload.html
    ├── list.html
    ├── detail.html
    └── export.html
```

## 使用示例
```python
# 初始化模块
from MyCerts import mycerts
app.register_blueprint(mycerts)

# 访问证书统计信息
from MyCerts.models import Certificate
stats = Certificate.get_stats(user_id)
```

## 注意事项
- 所有文件上传限制在 10MB 以内
- 支持的文件格式：PDF、JPG、PNG
- 模块需要用户认证（必须提供 user_id）
- 所有日期以 UTC 时间存储
- 文件路径相对于应用根目录存储 