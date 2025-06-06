# NoteBox

[English Version](README.md)

**NoteBox** 是一个轻量级的笔记管理和知识卡片应用，旨在帮助学生有效地组织学习资料和复习知识。

---

## 🚀 安装指南

1. 使用 conda 创建并激活虚拟环境：
```bash
conda create -n notebox python=3.9
conda activate notebox
```

2. 安装所需依赖：
```bash
pip install flask
```

3. 进入项目目录并运行程序：
```bash
cd NoteBox
python app.py
```

4. 在浏览器中访问：[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📁 项目结构

```bash
NoteBox
    |-- app.py              # Flask 主应用文件
    |-- README.md           # 英文文档
    |-- readme_ch.md        # 中文文档
    |-- requirements.txt    # Python 依赖
    |-- prd.md             # 产品需求文档
    |-- data/              # 数据存储目录
        |-- notes.json     # 笔记数据
        |-- cards.json     # 知识卡片数据
    |-- static/            # 静态资源
    |-- prototype/         # HTML 模板
        |-- base.html      # 基础模板
        |-- main.html      # 主面板
        |-- note_list.html # 笔记列表视图
        |-- edit_note.html # 笔记编辑器
        |-- cards.html     # 知识卡片视图
        |-- review.html    # 复习界面
```

- **`app.py`**: Flask 应用主文件，定义路由和处理数据管理。
- **`base.html`**: 定义通用布局和导航的基础模板。
- **`main.html`**: 显示统计信息和快捷操作的面板。
- **`note_list.html`**: 查看和筛选笔记的界面。
- **`edit_note.html`**: 创建和编辑笔记的富文本编辑器。
- **`cards.html`**: 查看和管理知识卡片的界面。
- **`review.html`**: 间隔重复复习系统界面。
- **`data/`**: 以 JSON 格式存储笔记和知识卡片数据的目录。
- **`static/`**: 包含 CSS、JavaScript 和图像等静态资源。

---

## 🎯 功能特点

1. **笔记管理**
   - 创建、编辑和删除笔记
   - 使用课程和标签组织笔记
   - 支持 Markdown 的富文本编辑
   - 搜索和筛选笔记

2. **知识卡片系统**
   - 从笔记生成知识卡片
   - 设置难度等级
   - 使用间隔重复进行复习
   - 跟踪学习进度

3. **复习系统**
   - 交互式卡片翻转
   - 难度评级
   - 进度跟踪
   - 时间记录

4. **用户界面**
   - 简洁直观的设计
   - 响应式布局
   - 双语支持（英文/中文）
   - 深色模式支持

---

## 🤝 贡献指南

要参与 NoteBox 的开发：

1. Fork 项目仓库
2. 创建特性分支
3. 进行修改
4. 提交 Pull Request

请确保你的代码遵循现有的代码风格，并包含适当的测试。

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。 