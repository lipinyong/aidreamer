"""
示例 API 接口
"""
from module.webhandle import webhandle
from fastapi import Request


@webhandle.route('/example/hello')
def hello(request: Request):
    """
    示例接口：返回 Hello World
    
    访问方式: GET /api/example/hello
    """
    return {
        'message': 'Hello, World!',
        'path': str(request.url.path),
        'method': request.method
    }
