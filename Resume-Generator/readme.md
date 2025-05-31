#### 接口说明
`text2cv.py`中包含两个主要接口:
* `text2Latex(input, output_path)`将输入的信息转换为`tex`文件, 存储在`output_path`
* `compileLatex(tex_file)`将`tex`文件编译为pdf, 这里实现了本地编译

#### 本地编译准备
本地编译需要`pdflatex`, 可以从https://miktex.org/download 下载轻量化的miktex, 在编译过程中会有一些宏是未下载的, 第一次编译会在遇到未下载宏时提示用户下载. 考虑把整个安装过程和宏的补充下载过程写在代码脚本中

#### 在线编译
更好的方法应该是在线编译, 可以进一步考虑使用`Overleaf`或其它在线`Latex`编译器编译, 但是目前没有找到很好的方法.

#### 输入规范
应该将用户输入转换成`text2cv.py`中说明的字典结构.