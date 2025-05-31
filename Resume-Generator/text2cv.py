import requests
import urllib.parse
import subprocess
"""
Here is a example for the input:
输入中的值可以改成中文, 对应"language"也改成'ch', 但是键需严格按照例子中命名
input = {
    "language": "en",
    "Name": "John Doe",
    "Location": "Guangzhou, PRC",
    "Email": "...@...",
    "Education": [
        {
            "institution": "Sun Yat-sen University",
            "duration": "Sep 2023 - Present",
            "degree": "BEng in Computer Science and Technology",
            "GPA": "4.0/4.0,
            "Core Courses": ...
        }
    ]
    "Experience": [
        {
            "affiliation": "Sun Yat-sen University",
            "location": "Guangzhou, PRC",
            "duration": "Jun 2024 - Present",
            "descriptions": [
                ...,
                ...
            ]
        }
    ]
    "Publications": [
    {
        "authors": [...]
        "title": "...",
        "venue": "NeurIPS",
        "year": 2025,
        "url": "https:..."
    }]
    "Projects":[
        {
            "title": "...",
            "descriptions": [
                ...,
                ...
            ]
        }
    ]

    "Skills": {
        "Programming Languages": "C/C++, Python, Java",
        "Packages/Frameworks": "TensorFlow, PyTorch",
        ...: ...
    }
    
}
"""
def compileLatex(tex_file):
    subprocess.run(["pdflatex", tex_file])
    
def text2Latex(input, output_path = './cv.tex'):
    language = input.get('language', 'en')
    assert language in ['en', 'ch'], "Language must be 'en' or 'ch'"

    result = header

    name = input.get('Name', '').strip()
    location = input.get('Location', '').strip()
    email = input.get('Email', '').strip()

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
    with open(output_path, 'w') as f:
        f.write(result)
    return result

def education(language, educations):
    """
    Generate the education section of a CV in LaTeX format.
    生成简历的教育经历板块
    Params:
        language (str): Language of the section, options: ['en', 'ch']
        educations (list): List of dicts, each with keys: 'institution', 'duration', 'degree', and optional extras
    Returns:
        result (str): LaTeX formatted education section

    educations example
    [
        {
            "institution": "Sun Yat-sen University",
            "duration": "Sep 2023 - Present",
            "degree": "BEng in Computer Science and Technology",
            "GPA": "4.0/4.0,
            "Core Courses": ...
        }
    ]
    """
    assert language in ['en', 'ch']
    result = '\\section{Education}' if language == 'en' else '\\section{教育经历}'
    result += '\n'

    for edu in educations:
        institution = edu.get('institution', '')
        duration = edu.get('duration', '')
        degree = edu.get('degree', '')

        # Main entry
        entry = (
            f"\\begin{{twocolentry}}{{{duration}}}{{\\textbf{{{institution}}}, {degree}}}\n"
        )

        # Optional details
        extras = [k for k in edu.keys() if k not in ['institution', 'duration', 'degree']]
        if extras:
            entry += "\\begin{onecolentry}\n\\begin{highlights}\n"
            for key in extras:
                value = edu[key]
                entry += f"\\item \\textbf{{{key}}}: {value}\n"
            entry += "\\end{highlights}\n\\end{onecolentry}\n"

        entry += "\\end{twocolentry}\n"
        result += entry

    return result

def experience(language, experiences):
    """
    Generate the experience (Research, work...) section of a CV in LaTeX format.

    Params:
        language (str): 'en' or 'ch'
        experiences (list): List of dicts with keys:
            'affiliation', 'location', 'duration', 'position', 'descriptions' (list)

    Returns:
        str: LaTeX-formatted experience section
    """
    assert language in ['en', 'ch']
    result = '\\section{Experience}' if language == 'en' else '\\section{工作经历}'
    result += '\n'

    for exp in experiences:
        affiliation = exp.get('affiliation', '')
        location = exp.get('location', '')
        duration = exp.get('duration', '')
        position = exp.get('position', '')
        descriptions = exp.get('descriptions', [])

        # Main entry block
        entry = (
            f"\\begin{{twocolentry}}{{{duration}}}{{\\textbf{{{affiliation}}}, {location}}}\n"
        )

        # Position title in italic
        entry += f"\\textit{{{position}}}\n"
        entry += f"\\vspace{{0.1cm}}\n"

        # Descriptions
        if descriptions:
            entry += "\\begin{onecolentry}\n\\begin{highlights}\n"
            for desc in descriptions:
                entry += f"\\item {desc}\n"
            entry += "\\end{highlights}\n\\end{onecolentry}\n"

        entry += "\\end{twocolentry}\n\n"
        result += entry

    return result

def publications(language, publications, host):
    """
    Generate the publications section of a CV in LaTeX format.
    
    Params:
        language (str): 'en' or 'ch'
        publications (list): List of publication dictionaries
        host (str): Name of the CV owner (to bold in author list)
    Returns:
        str: LaTeX-formatted publications section
    """
    assert language in ['en', 'ch']
    result = '\\section{Publications}' if language == 'en' else '\\section{论文发表}'
    result += '\n\\begin{samepage}\n\\begin{onecolentry}\n\\begin{itemize}\n'

    for pub in publications:
        authors = pub.get('authors', [])
        title = pub.get('title', '')
        venue = pub.get('venue', '')
        year = pub.get('year', '')
        url = pub.get('url', '')

        # Format author list, bolding the host
        formatted_authors = []
        for author in authors:
            if author == host:
                formatted_authors.append(f"\\textbf{{{author}}}")
            else:
                formatted_authors.append(author)
        authors_str = ', '.join(formatted_authors)

        # Format entry
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
        title = project.get('title', '')
        descriptions = project.get('descriptions', [])

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
        % showframe % for debugging 
    ]{geometry} % for adjusting page geometry
    \usepackage{titlesec} % for customizing section titles
    \usepackage{tabularx} % for making tables with fixed width columns
    \usepackage{array} % tabularx requires this
    \usepackage[dvipsnames]{xcolor} % for coloring text
    \definecolor{primaryColor}{RGB}{0, 0, 0} % define primary color
    \usepackage{enumitem} % for customizing lists
    \usepackage{fontawesome5} % for using icons
    \usepackage{amsmath} % for math
    \usepackage[
        pdftitle={John Doe's CV},
        pdfauthor={John Doe},
        pdfcreator={LaTeX with RenderCV},
        colorlinks=true,
        urlcolor=primaryColor
    ]{hyperref} % for links, metadata and bookmarks
    \usepackage[pscoord]{eso-pic} % for floating text on the page
    \usepackage{calc} % for calculating lengths
    \usepackage{bookmark} % for bookmarks
    \usepackage{lastpage} % for getting the total number of pages
    \usepackage{changepage} % for one column entries (adjustwidth environment)
    \usepackage{paracol} % for two and three column entries
    \usepackage{ifthen} % for conditional statements
    \usepackage{needspace} % for avoiding page brake right after the section title
    \usepackage{iftex} % check if engine is pdflatex, xetex or luatex

    % Ensure that generate pdf is machine readable/ATS parsable:
    \ifPDFTeX
        \input{glyphtounicode}
        \pdfgentounicode=1
        \usepackage[T1]{fontenc}
        \usepackage[utf8]{inputenc}
        \usepackage{lmodern}
    \fi

    \usepackage{charter}

    % Some settings:
    \raggedright
    \AtBeginEnvironment{adjustwidth}{\partopsep0pt} % remove space before adjustwidth environment
    \pagestyle{empty} % no header or footer
    \setcounter{secnumdepth}{0} % no section numbering
    \setlength{\parindent}{0pt} % no indentation
    \setlength{\topskip}{0pt} % no top skip
    \setlength{\columnsep}{0.15cm} % set column seperation
    \pagenumbering{gobble} % no page numbering

    \titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]

    \titlespacing{\section}{
        % left space:
        -1pt
    }{
        % top space:
        0.3 cm
    }{
        % bottom space:
        0.2 cm
    } % section title spacing

    \renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$} % custom bullet points
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
    } % new environment for highlights


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
    } % new environment for highlights for bullet entries

    \newenvironment{onecolentry}{
        \begin{adjustwidth}{
            0 cm + 0.00001 cm
        }{
            0 cm + 0.00001 cm
        }
    }{
        \end{adjustwidth}
    } % new environment for one column entries

    \newenvironment{twocolentry}[2][]{
        \onecolentry
        \def\secondColumn{#2}
        \setcolumnwidth{\fill, 4.5 cm}
        \begin{paracol}{2}
    }{
        \switchcolumn \raggedleft \secondColumn
        \end{paracol}
        \endonecolentry
    } % new environment for two column entries

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
    } % new environment for three column entries

    \newenvironment{header}{
        \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.5}
    }{
        \par\kern\topsep
    } % new environment for the header

    \newcommand{\placelastupdatedtext}{% \placetextbox{<horizontal pos>}{<vertical pos>}{<stuff>}
    \AddToShipoutPictureFG*{% Add <stuff> to current page foreground
        \put(
            \LenToUnit{\paperwidth-2 cm-0 cm+0.05cm},
            \LenToUnit{\paperheight-1.0 cm}
        ){\vtop{{\null}\makebox[0pt][c]{
            \small\color{gray}\textit{Last updated in September 2024}\hspace{\widthof{Last updated in September 2024}}
        }}}%
    }%
    }%

    % save the original href command in a new command:
    \let\hrefWithoutArrow\href

    \begin{document}
        \newcommand{\AND}{\unskip
            \cleaders\copy\ANDbox\hskip\wd\ANDbox
            \ignorespaces
        }
        \newsavebox\ANDbox
        \sbox\ANDbox{$|$}
"""

if __name__ == '__main__':
    input = {
    "language": "en",
    "Name": "John Doe",
    "Location": "Guangzhou, PRC",
    "Email": "...@...",
    "Education": [
        {
            "institution": "Sun Yat-sen University",
            "duration": "Sep 2023 - Present",
            "degree": "BEng in Computer Science and Technology",
            "GPA": "4.0/4.0",
            "Core Courses": "Math"
        }
    ],
    "Experience": [
        {
            "affiliation": "Sun Yat-sen University",
            "location": "Guangzhou, PRC",
            "duration": "Jun 2024 - Present",
            "descriptions": [
                "First",
                "Second"
            ]
        }
    ],
    "Publications": [
    {
        "authors": ['Jhon Doe', 'Jane Smith'],
        "title": "Distilling LLM Prior to Flow Model for Generlizable Agent's Hallucination",
        "venue": "NeurIPS",
        "year": 2025,
        # "url": "https:..."
    }],
    "Projects":[
        {
            "title": "Distilling",
            "descriptions": [
                "First",
                "Second"
            ]
        }
    ],

    "Skills": {
        "Programming Languages": "C/C++, Python, Java",
        "Packages/Frameworks": "TensorFlow, PyTorch"
    }
    
}
    
    text2Latex(input)
    compileLatex('./cv.tex')