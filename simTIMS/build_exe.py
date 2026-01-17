#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化打包脚本
用于将Python项目编译成exe文件
"""

import os
import sys
import subprocess
import shutil


def install_requirements():
    """安装必要的依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False
    return True

def build_exe(spec_file, program_name):
    """使用PyInstaller打包exe"""
    print(f"正在打包 {program_name}...")
    try:
        cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean"]
        # if version_file:
        #     cmd += ["--version-file", version_file]
        # 使用spec文件打包
        subprocess.check_call(cmd)
        print(f"{program_name} 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{program_name} 打包失败: {e}")
        return False


def clean_build_files():
    """清理构建文件"""
    print("正在清理构建文件...")
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["*.spec"]

    # 清理spec文件（保留我们需要的）
    for file_pattern in files_to_clean:
        for file in os.listdir("build"):
            if file.endswith(".spec") and file not in ["simTIMS.spec"]:
                os.remove(file)
                print(f"已删除文件: {file}")

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除目录: {dir_name}")


def main():
    """主函数"""
    print("开始打包程序...")

    # 1. 安装依赖
    if not install_requirements():
        return

    # 2. 清理之前的构建文件
    clean_build_files()

    # 3. 打包程序
    if os.path.exists("simTIMS.spec"):
        if build_exe("simTIMS.spec", "simTIMS"):
            print("日志读取程序exe文件位于: dist/simTIMS.exe")

    print("打包完成！")
    print("所有exe文件都在 dist/ 目录中")


if __name__ == "__main__":
    main()

