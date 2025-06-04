# Collegra

[中文版](readme_ch.md)

**Collegra** (College + Agora) is a lightweight software platform designed to help college students thrive academically, professionally, and personally by integrating a suite of useful tools.

---

## 🚀 Installation

1. Create and activate a virtual environment using conda:
```bash
conda create -n collegra python=3.9
conda activate collegra
```

2. Install required dependencies:
```bash
pip install flask flask_sqlalchemy flask_babel
```

3. Navigate to the project directory and run the application:
```bash
cd Collegra
python app.py
```

4. Open your browser and visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📁 Project Structure

```bash
Collegra
    |-- app.py
    |-- README.md
    |-- readme_ch.md
    |-- text2cv.py
    |-- static/
    |-- templates/
        |-- CourseScheduler/
        |-- PathRecommender/
        |-- base.html
        |-- index.html
```

- **`app.py`**: The main Flask application file that defines routes, initializes the app, and launches the server.
- **`base.html`**: Defines the top navigation bar (logo, slogan, language toggle, and menu) and the gradient background.
- **`index.html`**: The homepage of *Collegra*.
- **Other folders under `templates/`**: Contain module-specific pages.
- **`static/`**: Contains static assets such as CSS, JavaScript, and images.
- **`text2cv.py`**: A script for generating a resume from user input (if applicable).

---

## 🤝 Contribution Guidelines

To contribute a new module that benefits college students:

1. Place your module’s main `HTML` file directly under the `templates/` folder.
2. If your module contains multiple pages, create a subfolder under `templates/` to organize them.
3. Register a route in `app.py`:
   ```python
   @app.route('/<your_module>')
   def your_module():
       return render_template('<your_main_html_path>')
   ```
   You may also need to define additional Python functions depending on your module’s logic.

4. Add a menu entry in `base.html`:
   ```html
   <a href="{{ url_for('your_module') }}">
       <span class="lang-en hidden">Your Module Name</span>
       <span class="lang-zh">你的模块名称</span>
   </a>
   ```

5. All HTML templates should extend `base.html` to maintain a consistent layout.
6. Ensure your proposed module is distinct and not duplicative of existing features.


