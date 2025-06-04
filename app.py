from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
import base64
from text2cv import text2Latex, compileLatex

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommender')
def recommender():
    return render_template('recommender.html')

@app.route('/llm')
def llm():
    return render_template('PathRecommender/llm/main.html')

@app.route('/aigc')
def aigc():
    return render_template('PathRecommender/aigc/main.html')

@app.route('/embodied')
def embodied():
    return render_template('PathRecommender/embodied/main.html')

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

@app.route('/preview')
def preview():
    return render_template('preview.html')

@app.route('/MiKTeX_installation.html')
def MiKTeX_installation():
    return render_template('MiKTeX_installation.html')


@app.route('/todo')
def todo():
    return render_template('todo.html')

@app.route('/api/preview-resume', methods=['POST'])
def preview_resume():
    try:
        data = request.get_json()
        print('Received preview data:', data)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        download_option = data.get('download_option', 'pdf')
        print(f'Processing preview for {download_option}')
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'cv.tex')
            latex_content = text2Latex(data, tex_file)
            if download_option == 'pdf':
                compileLatex(tex_file, temp_dir)
                pdf_file = os.path.join(temp_dir, 'cv.pdf')
                print(f'PDF exists: {os.path.exists(pdf_file)}, size: {os.path.getsize(pdf_file) if os.path.exists(pdf_file) else 0}')
                if not os.path.exists(pdf_file):
                    return jsonify({"error": "PDF generation failed: No PDF file produced"}), 500
                with open(pdf_file, 'rb') as f:
                    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
                print(f'PDF base64 length: {len(pdf_base64)}, starts with: {pdf_base64[:10]}...')
                result = {"type": "pdf", "content": pdf_base64}
            else:
                result = {"type": "latex", "content": latex_content}
            print(f'Returning {result["type"]} content, length: {len(result["content"])}')
            return jsonify(result), 200
    except Exception as e:
        print(f"Error in preview_resume: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_cv_route():
    try:
        data = request.get_json()
        print('Received generate data:', data)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        download_option = data.get('download_option', 'pdf')
        print(f'Generating {download_option} file')
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'cv.tex')
            text2Latex(data, tex_file)
            if download_option == 'latex':
                return send_file(
                    tex_file,
                    as_attachment=True,
                    download_name='resume.tex',
                    mimetype='text/x-tex'
                )
            else:
                compileLatex(tex_file, temp_dir)
                pdf_file = os.path.join(temp_dir, 'cv.pdf')
                print(f'PDF exists: {os.path.exists(pdf_file)}, size: {os.path.getsize(pdf_file) if os.path.exists(pdf_file) else 0}')
                if not os.path.exists(pdf_file):
                    return jsonify({"error": "PDF generation failed: No PDF file produced"}), 500
                return send_file(
                    pdf_file,
                    as_attachment=True,
                    download_name='resume.pdf',
                    mimetype='application/pdf'
                )
    except Exception as e:
        print(f"Error in generate_cv_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print('Starting Flask server')
    app.run(debug=True, port=8000)

