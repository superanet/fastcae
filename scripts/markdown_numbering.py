#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown标题自动编号工具

功能：
- 自动识别并跳过文档标题和目录部分
- 为正文标题添加层次化编号（1., 1.1., 1.1.1.等格式）
- 支持清除已有编号并重新编号
- 提供文件备份功能

作者：AI Assistant
版本：1.0
"""

import re
import os
import sys
import argparse
import shutil
from typing import List, Tuple, Optional


class MarkdownNumbering:
    """Markdown标题编号处理类"""
    
    def __init__(self):
        # 匹配标题的正则表达式（支持1-6级标题）
        self.title_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
        # 匹配已有编号的正则表达式
        self.number_pattern = re.compile(r'^(\d+\.)*\d+\.\s+(.*)$')
        # 匹配目录链接的正则表达式
        self.toc_pattern = re.compile(r'^\[.*\]\(#.*\)$')
        
    def is_toc_section(self, lines: List[str], start_idx: int) -> Tuple[bool, int]:
        """
        判断是否为目录部分
        
        Args:
            lines: 文档行列表
            start_idx: 开始检查的行索引
            
        Returns:
            (是否为目录, 目录结束行索引)
        """
        if start_idx >= len(lines):
            return False, start_idx
            
        # 检查是否为目录标题
        line = lines[start_idx].strip()
        if not (line.startswith('# 目录') or line.startswith('## 目录') or 
                line.lower().startswith('# table of contents') or
                line.lower().startswith('## table of contents')):
            return False, start_idx
            
        # 查找目录内容
        idx = start_idx + 1
        toc_links_found = 0
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            # 空行跳过
            if not line:
                idx += 1
                continue
                
            # 分隔线跳过
            if line.startswith('---') or line.startswith('==='):
                idx += 1
                continue
                
            # 检查是否为目录链接
            if self.toc_pattern.match(line) or line.startswith('[') and '](#' in line:
                toc_links_found += 1
                idx += 1
                continue
                
            # 遇到下一个标题，目录结束
            if self.title_pattern.match(line):
                break
                
            # 其他内容，可能不是目录
            if toc_links_found == 0:
                return False, start_idx
            else:
                break
                
            idx += 1
            
        return toc_links_found > 0, idx
    
    def clean_existing_numbers(self, title_text: str) -> str:
        """
        清除标题中已有的编号
        
        Args:
            title_text: 标题文本
            
        Returns:
            清除编号后的标题文本
        """
        match = self.number_pattern.match(title_text.strip())
        if match:
            return match.group(2)
        return title_text.strip()
    
    def generate_number(self, level: int, counters: List[int]) -> str:
        """
        生成指定层级的编号
        
        Args:
            level: 标题层级（1-6）
            counters: 各层级计数器
            
        Returns:
            编号字符串（如"1.2.3."）
        """
        # 确保计数器列表足够长
        while len(counters) < level:
            counters.append(0)
            
        # 重置当前层级以下的计数器
        for i in range(level, len(counters)):
            counters[i] = 0
            
        # 当前层级计数器加1
        counters[level - 1] += 1
        
        # 生成编号字符串
        number_parts = []
        for i in range(level):
            if counters[i] > 0:
                number_parts.append(str(counters[i]))
            else:
                break
                
        return '.'.join(number_parts) + '.'
    
    def process_markdown(self, content: str) -> str:
        """
        处理Markdown内容，添加标题编号

        Args:
            content: 原始Markdown内容

        Returns:
            添加编号后的Markdown内容
        """
        lines = content.split('\n')
        result_lines = []
        counters = []  # 各层级计数器
        in_code_block = False  # 是否在代码块中
        in_html_comment = False  # 是否在HTML注释中

        # 代码块和注释的正则表达式
        code_block_pattern = re.compile(r'^```')
        html_comment_start = re.compile(r'<!--')
        html_comment_end = re.compile(r'-->')

        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()

            # 检查HTML注释开始和结束
            if html_comment_start.search(line) and not in_code_block:
                in_html_comment = True
            if html_comment_end.search(line) and in_html_comment:
                in_html_comment = False
                result_lines.append(line)
                i += 1
                continue

            # 检查代码块开始/结束
            if code_block_pattern.match(line_stripped):
                in_code_block = not in_code_block
                result_lines.append(line)
                i += 1
                continue

            # 如果在代码块或HTML注释中，直接复制行
            if in_code_block or in_html_comment:
                result_lines.append(line)
                i += 1
                continue

            # 检查是否为标题
            title_match = self.title_pattern.match(line)

            if title_match:
                # 检查是否为目录部分
                is_toc, toc_end = self.is_toc_section(lines, i)

                if is_toc:
                    # 目录部分不添加编号，直接复制
                    while i < toc_end:
                        result_lines.append(lines[i])
                        i += 1
                    continue

                # 处理正文标题
                hash_marks = title_match.group(1)
                title_text = title_match.group(2)
                level = len(hash_marks)

                # 清除已有编号
                clean_title = self.clean_existing_numbers(title_text)

                # 生成新编号
                number = self.generate_number(level, counters)

                # 构造新标题行
                new_title = f"{hash_marks} {number} {clean_title}"
                result_lines.append(new_title)
            else:
                # 非标题行直接复制
                result_lines.append(line)

            i += 1

        return '\n'.join(result_lines)
    
    def backup_file(self, file_path: str) -> str:
        """
        创建文件备份
        
        Args:
            file_path: 原文件路径
            
        Returns:
            备份文件路径
        """
        backup_path = file_path + '.backup'
        counter = 1
        
        # 如果备份文件已存在，添加数字后缀
        while os.path.exists(backup_path):
            backup_path = f"{file_path}.backup.{counter}"
            counter += 1
            
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def process_file(self, input_path: str, output_path: Optional[str] = None, 
                    create_backup: bool = True) -> bool:
        """
        处理Markdown文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（None表示覆盖原文件）
            create_backup: 是否创建备份
            
        Returns:
            处理是否成功
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                print(f"错误：输入文件不存在: {input_path}")
                return False
            
            # 读取文件内容
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 处理内容
            processed_content = self.process_markdown(content)
            
            # 确定输出路径
            if output_path is None:
                output_path = input_path
                
                # 创建备份
                if create_backup:
                    backup_path = self.backup_file(input_path)
                    print(f"已创建备份文件: {backup_path}")
            
            # 写入处理后的内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"处理完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"处理文件时发生错误: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='为Markdown文档标题自动添加层次化编号',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python markdown_numbering.py document.md                    # 覆盖原文件（自动备份）
  python markdown_numbering.py document.md -o output.md       # 输出到新文件
  python markdown_numbering.py document.md --no-backup        # 覆盖原文件（不备份）
  python markdown_numbering.py document.md -o output.md --no-backup  # 输出到新文件（不备份）
        """
    )
    
    parser.add_argument('input', help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--no-backup', action='store_true', 
                       help='不创建备份文件（仅在覆盖原文件时有效）')
    
    args = parser.parse_args()
    
    # 创建处理器实例
    processor = MarkdownNumbering()
    
    # 处理文件
    success = processor.process_file(
        input_path=args.input,
        output_path=args.output,
        create_backup=not args.no_backup
    )
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
