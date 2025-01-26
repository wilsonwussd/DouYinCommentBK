from app import create_app
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from loguru import logger
import sys
import traceback

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
        logger.info("Starting server...")
        
        # 配置错误处理
        @app.errorhandler(Exception)
        def handle_exception(e):
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "traceback": traceback.format_exc()}, 500
            
        asyncio.run(serve(app, config))
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 