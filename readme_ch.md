# Collegra
[English version](README.md)

Collegra（由 College 和 Agora 组成）是一个轻量级的软件平台，集成了多种实用功能，旨在支持大学生的学习、职业发展和日常生活。

## 已完成的内容
以下模块的基本功能已实现：
* 简历生成器（Resume-Generator）：学生提供个人信息后，生成器会自动返回一份 LaTeX（.tex）格式的简历或 PDF 版本。
* 学习路径推荐器（LearningPath-Recommender）：该模块为对特定领域感兴趣的学生推荐学习路径，涵盖在线课程、博客、论文等多种资源。
* 课程表生成器（Timetable-Generator）：该模块帮助学生高效地安排课程时间表。

另外, 完成了两个版本的logo, 在目录 `./assets`下.

## 贡献规范
如果你希望添加对大学生在学习、职业发展或日常生活有帮助的新模块，请按以下步骤操作：
1. 将你的实现集成到一个新的目录中。
2. 你的所有`html`文件应该继承`base.html`文件以实现协调的GUI主题。
3. 在该目录下包含一个 main.html 文件，作为模块的主界面。
4. 提交一个 Pull Request。
5. 希望你可以包含中英文两个版本, `base.html`中实现了语言切换的按钮。
