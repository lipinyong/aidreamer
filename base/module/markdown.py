"""
Markdown 渲染器模块
"""
import markdown
from pathlib import Path
from typing import Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re


class MarkdownRenderer:
    """Markdown 渲染器"""
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'nl2br',
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                },
                'toc': {
                    'permalink': True,
                }
            }
        )
    
    def render(self, content: str, title: Optional[str] = None) -> str:
        """
        渲染 Markdown 内容为 HTML
        
        Args:
            content: Markdown 内容
            title: 页面标题（可选）
        
        Returns:
            HTML 字符串
        """
        html = self.md.convert(content)
        
        # 生成完整的 HTML 页面
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Document'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 16px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: 600;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 16px 0;
            padding-left: 16px;
            color: #666;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .highlight {{
            margin: 16px 0;
        }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""
        return html_template
    
    def render_file(self, file_path: Path) -> Optional[str]:
        """
        渲染 Markdown 文件
        
        Args:
            file_path: Markdown 文件路径
        
        Returns:
            HTML 字符串，文件不存在返回 None
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = file_path.stem
            return self.render(content, title)
        
        except Exception as e:
            print(f"渲染 Markdown 文件失败 {file_path}: {e}")
            return None
    
    def reset(self):
        """重置 Markdown 解析器（用于重新加载）"""
        self.md = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'nl2br',
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                },
                'toc': {
                    'permalink': True,
                }
            }
        )
