# Collegra

[English Version](README.md)

**Collegra**（College + Agora）是一个轻量级的软件平台，集成了多种实用功能，旨在帮助大学生在学业、职业发展和日常生活中全面成长。

---

## 🚀 安装指南

1. 使用 conda 创建并激活虚拟环境：
```bash
conda create -n collegra python=3.9
conda activate collegra
```

2. 安装所需依赖：
```bash
pip install flask flask_sqlalchemy flask_babel
```

3. 进入项目目录并运行程序：
```bash
cd Collegra
python app.py
```

4. 在浏览器中访问：[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📁 项目结构

```bash
Collegra
    |-- app.py
    |-- README.md
    |-- readme_ch.md
    |-- text2cv.py
    |-- static
    |-- templates
        |-- CourseScheduler
        |-- PathRecommender
        |-- base.html
        |-- index.html
```

- **`app.py`**：Flask 应用的主文件，定义路由、初始化程序并启动服务器。
- **`base.html`**：定义顶栏（包括 logo、标语、语言切换和菜单）以及渐变背景的基础模板。
- **`index.html`**：Collegra 的主页。
- **`templates/` 下的其他文件夹**：包含各个模块的页面。
- **`static/`**：包含静态资源，如 CSS、JavaScript 和图像等。
- **`text2cv.py`**：用于将文本生成简历的脚本（如需也可补充用途说明）。

---

## 🤝 贡献指南

如果你想贡献一个对大学生有帮助的新模块，请遵循以下步骤：

1. 将你的模块主页的 `HTML` 文件直接放入 `templates/` 文件夹中。
2. 如果你的模块包含多个页面，请在 `templates/` 下创建一个新文件夹，并将辅助页面放入其中。
3. 在 `app.py` 中注册模块路由，例如：
   ```python
   @app.route('/<your_module>')
   def your_module():
       return render_template('<your_main_html_path>')
   ```
   根据实现的复杂程度，你可能还需要添加更多的 Python 接口逻辑。

4. 更新 `base.html` 中的导航菜单，添加模块链接：
   ```html
   <a href="{{ url_for('your_module') }}">
       <span class="lang-en hidden">Your Module Name</span>
       <span class="lang-zh">你的模块名称</span>
   </a>
   ```

5. 所有的 `HTML` 页面应继承自 `base.html`，以保持一致的页面结构和样式。
6. 请确保你提议的模块与现有模块不相似或重复。

