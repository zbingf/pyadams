# -*- coding: utf-8 -*-

# adams_py27.py

import re
import os.path


def edit_py_file_for_aview(var_name, file_path):
    """
        编辑py文件用于 adams-python 2.7的调用
        用途:
            编辑文件路径变量var_name的路径, 输出file_path的父目录
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    str_match = "(\s*{}\s*=\s*).*".format(var_name)
    for n_row, line in enumerate(lines):
        re_res = re.match(str_match, line)
        if re_res:
            file_dir = os.path.dirname(file_path)
            new_line = re_res.group(1) + 'r"{}"'.format(file_dir)
            lines[n_row] = new_line

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return True

