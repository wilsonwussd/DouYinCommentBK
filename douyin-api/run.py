from app import create_app
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from loguru import logger
import sys
import traceback
from werkzeug.exceptions import NotFound
from flask import jsonify, request

# 配置信息
EXTERNAL_DOMAIN = "https://slrgzucgttzq.sealoshzh.site"

# 配置日志记录
logger.remove()  # 移除默认的处理器
logger.add(sys.stderr, level="DEBUG", backtrace=True, diagnose=True)  # 添加标准错误输出处理器
logger.add("logs/app.log", rotation="500 MB", level="DEBUG", backtrace=True, diagnose=True)  # 添加文件处理器

app = create_app()

if __name__ == '__main__':
    try:
        config = HyperConfig()
        config.bind = ["0.0.0.0:8080"]
        config.error_logger = logger.error
        config.access_logger = logger.info
        logger.info(f"Starting server... External domain: {EXTERNAL_DOMAIN}")
        
        # 配置 404 错误处理
        @app.errorhandler(404)
        def not_found_error(error):
            logger.warning(f"404 错误: {request.url}")
            return jsonify({
                'error': '请求的 URL 不存在',
                'path': request.path,
                'external_url': f"{EXTERNAL_DOMAIN}{request.path}"
            }), 404
        
        # 配置通用错误处理
        @app.errorhandler(Exception)
        def handle_exception(e):
            if isinstance(e, NotFound):
                return not_found_error(e)
            logger.error(f"未处理的异常: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
            
        asyncio.run(serve(app, config))
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 