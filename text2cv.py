import subprocess
import os

def compileLatex(tex_file, output_dir):
    result = subprocess.run(["pdflatex", tex_file], cwd=output_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"pdflatex failed: {result.stderr}")
    aux_extensions = ['.aux', '.log', '.out']
    for ext in aux_extensions:
        aux_file = os.path.splitext(tex_file)[0] + ext
        try:
            if os.path.exists(aux_file):
                os.remove(aux_file)
        except PermissionError:
            pass

def escape_latex(text):
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\~{}', '^': r'\^{}', '\\': r'\textbackslash{}'
    }
    for char, replacement in replacements.items():
        text = str(text).replace(char, replacement)
    return text

def text2Latex(input, output_path=None):
    language = input.get('language', 'en')
    assert language in ['en', 'ch'], "Language must be 'en' or 'ch'"

    result = header

    name = escape_latex(input.get('Name', '').strip())
    location = escape_latex(input.get('Location', '').strip())
    email = escape_latex(input.get('Email', '').strip())

    result += rf"""
    \begin{{header}}
        \fontsize{{25 pt}}{{25 pt}}\selectfont {name}

        \vspace{{5 pt}}

        \normalsize
        \mbox{{{location}}}%
        \kern 5.0 pt%
        \AND%
        \kern 5.0 pt%
        \mbox{{\hrefWithoutArrow{{mailto:{email}}}{{{email}}}}}%
    \end{{header}}

    \vspace{{5 pt - 0.3 cm}}
    """

    for section, content in input.items():
        if section == 'Education':
            result += education(language, content)
        elif section == 'Experience':  
            result += experience(language, content)
        elif section == 'Publications':
            result += publications(language, content, name)
        elif section == 'Projects':
            result += projects(language, content)
        elif section == 'Skills':
            result += skills(language, content)

    result += r"""\end{document}"""
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
    return result

def education(language, educations):
    assert language in ['en', 'ch']
    result = '\\section{Education}' if language == 'en' else '\\section{教育经历}'
    result += '\n'

    for edu in educations:
        institution = escape_latex(edu.get('institution', ''))
        duration = escape_latex(edu.get('duration', ''))
        degree = escape_latex(edu.get('degree', ''))

        entry = (
            f"\\begin{{twocolentry}}{{{duration}}}{{\\textbf{{{institution}}}, {degree}}}\n"
        )

        extras = [k for k in edu.keys() if k not in ['institution', 'duration', 'degree']]
        if extras:
            entry += "\\begin{onecolentry}\n\\begin{highlights}\n"
            for key in extras:
                value = escape_latex(edu[key])
                key = escape_latex(key)
                entry += f"\\item \\textbf{{{key}}}: {value}\n"
            entry += "\\end{highlights}\n\\end{onecolentry}\n"

        entry += "\\end{twocolentry}\n"
        result += entry

    return result

def experience(language, experiences):
    assert language in ['en', 'ch']
    result = '\\section{Experience}' if language == 'en' else '\\section{工作经历}'
    result += '\n'

    for exp in experiences:
        affiliation = escape_latex(exp.get('affiliation', ''))
        location = escape_latex(exp.get('location', ''))
        duration = escape_latex(exp.get('duration', ''))
        position = escape_latex(exp.get('position', ''))
        descriptions = [escape_latex(desc) for desc in exp.get('descriptions', [])]

        entry = (
            f"\\begin{{twocolentry}}{{{duration}}}{{\\textbf{{{affiliation}}}, {location}}}\n"
        )

        entry += f"\\textit{{{position}}}\n"
        entry += f"\\vspace{{0.1cm}}\n"

        if descriptions:
            entry += "\\begin{onecolentry}\n\\begin{highlights}\n"
            for desc in descriptions:
                entry += f"\\item {desc}\n"
            entry += "\\end{highlights}\n\\end{onecolentry}\n"

        entry += "\\end{twocolentry}\n\n"
        result += entry

    return result

def publications(language, publications, host):
    assert language in ['en', 'ch']
    result = '\\section{Publications}' if language == 'en' else '\\section{论文发表}'
    result += '\n\\begin{samepage}\n\\begin{onecolentry}\n\\begin{itemize}\n'

    for pub in publications:
        authors = [escape_latex(a) for a in pub.get('authors', [])]
        title = escape_latex(pub.get('title', ''))
        venue = escape_latex(pub.get('venue', ''))
        year = escape_latex(pub.get('year', ''))
        url = escape_latex(pub.get('url', ''))

        formatted_authors = []
        for author in authors:
            if author == host:
                formatted_authors.append(f"\\textbf{{{author}}}")
            else:
                formatted_authors.append(author)
        authors_str = ', '.join(formatted_authors)

        entry = f"\\item {authors_str}. \\textit{{{title}}}. {venue}, {year}."
        if url:
            entry += f" \\href{{{url}}}{{[Link]}}"
        entry += '\n'

        result += entry

    result += '\\end{itemize}\n\\end{onecolentry}\n\\end{samepage}\n'

    return result

def projects(language, projects):
    assert language in ['en', 'ch']
    result = '\\section{Projects}' if language == 'en' else '\\section{项目}'
    result += '\n'

    for project in projects:
        title = escape_latex(project.get('title', ''))
        descriptions = [escape_latex(desc) for desc in project.get('descriptions', [])]

        entry = f"\\begin{{onecolentry}}\n"
        entry += f"\\textbf{{{title}}}\\\\\n"
        entry += f"\\vspace{{0.1cm}}\n"

        if descriptions:
            entry += "\\begin{highlights}\n"
            for desc in descriptions:
                entry += f"\\item {desc}\n"
            entry += "\\end{highlights}\n"

        entry += "\\end{onecolentry}\n"
        result += entry

    return result

def skills(language, skills):
    assert language in ['en', 'ch']
    result = '\\section{Skills}' if language == 'en' else '\\section{技能}'
    result += '\n'

    for category, items in skills.items():
        category = escape_latex(category)
        items = escape_latex(items)
        result += f"\\begin{{onecolentry}}\n\\textbf{{{category}}}: {items}\n\\end{{onecolentry}}\n"
    
    return result
                
header = r"""
    \documentclass[10pt, letterpaper]{article}

    % Packages:
    \usepackage[
        ignoreheadfoot, % set margins without considering header and footer
        top=2 cm, % seperation between body and page edge from the top
        bottom=2 cm, % seperation between body and page edge from the bottom
        left=2 cm, % seperation between body and page edge from the left
        right=2 cm, % seperation between body and page edge from the right
        footskip=1.0 cm, % seperation between body and footer
    ]{geometry}
    \usepackage{titlesec}
    \usepackage{tabularx}
    \usepackage{array}
    \usepackage[dvipsnames]{xcolor}
    \definecolor{primaryColor}{RGB}{0, 0, 0}
    \usepackage{enumitem}
    \usepackage{fontawesome5}
    \usepackage{amsmath}
    \usepackage[
        pdftitle={John Doe's CV},
        pdfauthor={John Doe},
        pdfcreator={LaTeX with RenderCV},
        colorlinks=true,
        urlcolor=primaryColor
    ]{hyperref}
    \usepackage[pscoord]{eso-pic}
    \usepackage{calc}
    \usepackage{bookmark}
    \usepackage{lastpage}
    \usepackage{changepage}
    \usepackage{paracol}
    \usepackage{ifthen}
    \usepackage{needspace}
    \usepackage{iftex}

    \ifPDFTeX
        \input{glyphtounicode}
        \pdfgentounicode=1
        \usepackage[T1]{fontenc}
        \usepackage[utf8]{inputenc}
        \usepackage{lmodern}
    \fi

    \usepackage{charter}

    \raggedright
    \AtBeginEnvironment{adjustwidth}{\partopsep0pt}
    \pagestyle{empty}
    \setcounter{secnumdepth}{0}
    \setlength{\parindent}{0pt}
    \setlength{\topskip}{0pt}
    \setlength{\columnsep}{0.15cm}
    \pagenumbering{gobble}

    \titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]

    \titlespacing{\section}{-1pt}{0.3 cm}{0.2 cm}

    \renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}
    \newenvironment{highlights}{
        \begin{itemize}[
            topsep=0.10 cm,
            parsep=0.10 cm,
            partopsep=0pt,
            itemsep=0pt,
            leftmargin=0 cm + 10pt
        ]
    }{
        \end{itemize}
    }

    \newenvironment{highlightsforbulletentries}{
        \begin{itemize}[
            topsep=0.10 cm,
            parsep=0.10 cm,
            partopsep=0pt,
            itemsep=0pt,
            leftmargin=10pt
        ]
    }{
        \end{itemize}
    }

    \newenvironment{onecolentry}{
        \begin{adjustwidth}{0 cm + 0.00001 cm}{0 cm + 0.00001 cm}
    }{
        \end{adjustwidth}
    }

    \newenvironment{twocolentry}[2][]{
        \onecolentry
        \def\secondColumn{#2}
        \setcolumnwidth{\fill, 4.5 cm}
        \begin{paracol}{2}
    }{
        \switchcolumn \raggedleft \secondColumn
        \end{paracol}
        \endonecolentry
    }

    \newenvironment{threecolentry}[3][]{
        \onecolentry
        \def\thirdColumn{#3}
        \setcolumnwidth{, \fill, 4.5 cm}
        \begin{paracol}{3}
        {\raggedright #2} \switchcolumn
    }{
        \switchcolumn \raggedleft \thirdColumn
        \end{paracol}
        \endonecolentry
    }

    \newenvironment{header}{
        \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.5}
    }{
        \par\kern\topsep
    }

    \newcommand{\placelastupdatedtext}{
        \AddToShipoutPictureFG*{
            \put(
                \LenToUnit{\paperwidth-2 cm-0 cm+0.05cm},
                \LenToUnit{\paperheight-1.0 cm}
            ){\vtop{{\null}\makebox[0pt][c]{
                \small\color{gray}\textit{Last updated in September 2024}\hspace{\widthof{Last updated in September 2024}}
            }}}
        }
    }

    \let\hrefWithoutArrow\href

    \begin{document}
        \newcommand{\AND}{\unskip
            \cleaders\copy\ANDbox\hskip\wd\ANDbox
            \ignorespaces
        }
        \newsavebox\ANDbox
        \sbox\ANDbox{$|$}
"""

if __name__ == "__main__":
    input = {'language': 'ch', 'download_option': 'latex', 'Name': 'John Doe', 'Location': 'Guangzhou, PRC', 'Email': 'zhangwei@sysu.com', 'Education': [], 'Experience': [], 'Publications': [], 'Projects': [], 'Skills': {}}
    text2Latex(input)
    compileLatex('./cv.tex', '.')