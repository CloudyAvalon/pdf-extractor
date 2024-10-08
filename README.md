# table_maker
基于pyside2实现GUI，使用pymupdf实现pdf内容提取和数据写回，使用openpyxl提取和写入excel文件

功能包括：  
1. 根据配置文件从pdf中提取关注的数据
2. 将数据写入指定样式的excel
3. 通过部分数据项，与excel表格项进行匹配，获得匹配到的数据
4. 将匹配到的数据写回pdf

## 修改界面
pyside6-designer.exe .\mainwindow.ui
## 更新资源与界面程序
pyside6-project.exe build .\table_maker.pyproject


## Install
pyside6-deploy -c pysidedeploy.spec
