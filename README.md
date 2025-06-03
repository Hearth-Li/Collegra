# Collegra 
[中文版](readme_ch.md)

Collegra (College + Agora) is a lightweight software platform that integrates multiple useful features to support college students in their studies, career pursuits, and daily life.

## What has been done? 
The basic functionality of the following modules has been implemented:
* Resume-Generator: Students provide their information, and the generator automatically returns a LaTeX (.tex) file or a PDF version of their resume.
* LearningPath-Recommendator: This module recommends learning paths for students interested in specific areas. Various resources such as online courses, blogs, and research papers are suggested.
* Timetable-Generator: This module helps students schedule their classes efficiently.

By the way, two versions of logo are completed, under the directory `./assets`.

## Conduct codes for contribution
To contribute new modules that you believe will benefit college students in their studies, career pursuits, or daily life, simply:
1. Integrate your implementation into a new directory.
2. All your `html` file should be derived from the `base.html` file for consistent theme.
3. Include a `main.html` or `index.html` file as the main interface under that directory.
4. Submit a pull request.
5. You are highly recommended to implement both Chinese and English version. The `base.html` file has implemented the language toggle buttom. 

## TODO
##### timetable generator 
- [ ] Adjust GUI interface

##### resume generator
- [x] main source codes
- [x] entire I/O stream line 
- [x] guide for installing `pdflatex` locally
- [ ] online compilation method?

##### learning path recommender
- [x] Add more details to each node to the aigc learning path
- [x] Improve the design of user interface 
- [x] Other paths design  
- [ ] Validate all urls.