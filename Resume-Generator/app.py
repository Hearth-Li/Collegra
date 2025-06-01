from flask import Flask, request, send_file
import os
from text2cv import text2Latex, compileLatex  # Import your functions

app = Flask(__name__)

# Serve index.html at root URL
@app.route('/')
def serve_html():
    return send_file('index.html')

# Optional: Serve a favicon to avoid 404 errors
@app.route('/favicon.ico')
def serve_favicon():
    # If you have a favicon.ico file in your project directory, serve it
    # Otherwise, return an empty response to avoid 404
    if os.path.exists('favicon.ico'):
        return send_file('favicon.ico')
    return '', 204  # No content response

# Generate CV endpoint
@app.route('/generate_cv', methods=['POST'])
def generate_cv():
    try:
        # Get JSON data from request
        data = request.json

        # Generate LaTeX file
        tex_file = 'cv.tex'
        text2Latex(data, tex_file)

        # Compile LaTeX to PDF
        compileLatex(tex_file)

        # Check if PDF was created
        pdf_file = 'cv.pdf'
        if not os.path.exists(pdf_file):
            return {"error": "Failed to generate PDF"}, 500

        # Send PDF file to client
        response = send_file(pdf_file, as_attachment=True, download_name='cv.pdf')

        # Clean up temporary files
        for ext in ['tex', 'pdf', 'aux', 'log', 'out']:
            file_path = f'cv.{ext}'
            if os.path.exists(file_path):
                os.remove(file_path)

        return response
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)