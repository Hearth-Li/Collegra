# NoteBox

[中文版](readme_ch.md)

**NoteBox** is a lightweight note-taking and flashcard application designed to help students organize their study materials and review knowledge effectively.

---

## 🚀 Installation

1. Create and activate a virtual environment using conda:
```bash
conda create -n notebox python=3.9
conda activate notebox
```

2. Install required dependencies:
```bash
pip install flask
```

3. Navigate to the project directory and run the application:
```bash
cd NoteBox
python app.py
```

4. Open your browser and visit: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📁 Project Structure

```bash
NoteBox
    |-- app.py              # Main Flask application
    |-- README.md           # English documentation
    |-- readme_ch.md        # Chinese documentation
    |-- requirements.txt    # Python dependencies
    |-- prd.md             # Product requirements document
    |-- data/              # Data storage directory
        |-- notes.json     # Notes data
        |-- cards.json     # Flashcards data
    |-- static/            # Static assets
    |-- prototype/         # HTML templates
        |-- base.html      # Base template
        |-- main.html      # Main dashboard
        |-- note_list.html # Note list view
        |-- edit_note.html # Note editor
        |-- cards.html     # Flashcard view
        |-- review.html    # Review interface
```

- **`app.py`**: The main Flask application file that defines routes and handles data management.
- **`base.html`**: Base template that defines the common layout and navigation.
- **`main.html`**: Dashboard showing statistics and quick actions.
- **`note_list.html`**: Interface for viewing and filtering notes.
- **`edit_note.html`**: Rich text editor for creating and editing notes.
- **`cards.html`**: Interface for viewing and managing flashcards.
- **`review.html`**: Spaced repetition review system interface.
- **`data/`**: Directory for storing notes and flashcards data in JSON format.
- **`static/`**: Contains static assets such as CSS, JavaScript, and images.

---

## 🎯 Features

1. **Note Management**
   - Create, edit, and delete notes
   - Organize notes with courses and tags
   - Rich text editing with Markdown support
   - Search and filter notes

2. **Flashcard System**
   - Generate flashcards from notes
   - Set difficulty levels
   - Review cards with spaced repetition
   - Track learning progress

3. **Review System**
   - Interactive card flipping
   - Difficulty rating
   - Progress tracking
   - Time tracking

4. **User Interface**
   - Clean and intuitive design
   - Responsive layout
   - Bilingual support (English/Chinese)
   - Dark mode support

---

## 🤝 Contributing

To contribute to NoteBox:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your code follows the existing style and includes appropriate tests.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 