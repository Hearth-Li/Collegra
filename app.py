from flask import Flask, render_template, request, send_file
import os
import tempfile
from text2cv import text2Latex, compileLatex
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/recommender')
def recommender():
    return render_template('recommender.html')

@app.route('/llm')
def llm():
    return render_template('PathRecommender/LLM/main.html')

@app.route('/aigc')
def aigc():
    return render_template('PathRecommender/AIGC/main.html')

@app.route('/embodied')
def embodied():
    return render_template('PathRecommender/Embodied/main.html')

@app.route('/algorithms')
def algorithms():
    return render_template('PathRecommender/embodied/algorithms.html')

@app.route('/control_and_robotics')
def control_and_robotics():
    return render_template('PathRecommender/embodied/control_and_robotics.html')

@app.route('/llm_basics')
def llm_basics():
    return render_template('PathRecommender/llm/llm_basics.html')

@app.route('/modern_algorithm_architecture')
def modern_algorithm_architecture():
    return render_template('PathRecommender/llm/modern_algorithm_architecture.html')


@app.route('/resume')
def resume():
    return render_template('resume.html')

# Route to handle CV generation
@app.route('/generate_cv', methods=['POST'])
def generate_cv_route():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Generate the LaTeX file using a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'cv.tex')
            text2Latex(data, tex_file)  # Generate the LaTeX file
            
            # Compile the LaTeX file to PDF
            compileLatex(tex_file)
            pdf_file = os.path.join(temp_dir, 'cv.pdf')
            
            # Check if the PDF was created
            if not os.path.exists(pdf_file):
                raise Exception("PDF generation failed")

            # Send the PDF as a downloadable file
            return send_file(
                pdf_file,
                as_attachment=True,
                download_name='cv.pdf',
                mimetype='application/pdf'
            )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
