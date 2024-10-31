@echo off
:: 获取当前目录
set current_dir=%~dp0

:: 设置Python文件名
set script_name=main.py

:: 构建完整路径
set script_path=%current_dir%%script_name%

:: 检查 main.py 是否存在
if exist "%script_path%" (
    echo Running main.py...
    :: 使用 start /b /wait 运行脚本，使其在当前窗口下独立执行
    start "" /b /wait python "%script_path%"
) else (
    echo %script_name% does not exist in %current_dir%
)

:: 直接结束，不暂停
exit