from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User, Comment
from .services import CommentService
import asyncio
import os
import traceback
from loguru import logger
from datetime import datetime
from sqlalchemy import text
import re

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/test/env', methods=['GET'])
@jwt_required()
def test_env():
    """测试环境变量接口"""
    return jsonify({
        'cookie_length': len(current_app.config['DOUYIN_COOKIE']) if current_app.config['DOUYIN_COOKIE'] else 0,
        'cookie_preview': current_app.config['DOUYIN_COOKIE'][:50] if current_app.config['DOUYIN_COOKIE'] else None,
        'env_vars': dict(os.environ)
    })

@api.route('/users/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
            
        # 更新最后登录时间
        user.update_login_time()
            
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '登录失败',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api.route('/users/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
            
        user = User(username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '注册失败',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api.route('/users/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        # 从 JWT 中获取用户名
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        return jsonify({
            'username': user.username,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'status': 'active'
        }), 200
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '获取用户信息失败',
            'detail': str(e)
        }), 500

def extract_video_id(url_or_id: str) -> str:
    """从URL或ID字符串中提取视频ID
    
    Args:
        url_or_id: 视频URL或ID字符串
        
    Returns:
        str: 提取的视频ID
    """
    # 如果输入的是纯数字，直接返回
    if url_or_id.isdigit():
        return url_or_id
        
    # 尝试从URL中提取ID
    patterns = [
        r'video/(\d+)',  # 匹配 video/数字
        r'/(\d+)/?$',    # 匹配URL末尾的数字
        r'item_ids=(\d+)'  # 匹配 item_ids=数字
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
            
    # 如果无法提取，返回原始输入
    return url_or_id

@api.route('/comments/collect', methods=['POST', 'GET'])
@jwt_required()
async def collect_comments():
    """采集视频评论"""
    try:
        # 从请求中获取参数
        if request.method == 'POST':
            data = request.get_json()
            video_id = data.get('video_id')
            max_comments = data.get('max_comments', 100)
            page = data.get('page', 1)
            per_page = data.get('per_page', 100)
        else:  # GET方法
            video_id = request.args.get('video_id')
            max_comments = request.args.get('max_comments', 100, type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
        
        if not video_id:
            return jsonify({'error': '请提供视频ID'}), 400
            
        # 从URL中提取视频ID（如果是完整URL）
        video_id = extract_video_id(video_id)
        current_app.logger.debug(f"处理后的视频ID: {video_id}")
        
        # 初始化评论服务
        comment_service = CommentService()
        current_app.logger.debug(f"开始采集视频评论, video_id: {video_id}, page: {page}, per_page: {per_page}")
        
        # 采集评论
        comments = await comment_service.collect_comments(video_id, max_comments)
        
        if not comments:
            return jsonify({'message': '没有找到评论'}), 404
            
        return jsonify({
            'video_id': video_id,
            'total': len(comments),
            'comments': comments
        })
        
    except Exception as e:
        current_app.logger.error(f"采集评论失败: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': '采集评论失败',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api.route('/comments/<video_id>', methods=['GET'])
@jwt_required()
def get_comments(video_id):
    """获取评论接口"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        comments = Comment.query.filter_by(video_id=video_id)\
            .order_by(Comment.created_at.desc())\
            .paginate(page=page, per_page=per_page)
            
        return jsonify({
            'total': comments.total,
            'pages': comments.pages,
            'current_page': comments.page,
            'comments': [comment.to_dict() for comment in comments.items]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching comments: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '获取评论失败',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api.route('/cookie/verify', methods=['GET'])
@jwt_required()
async def verify_cookie():
    """验证 cookie 是否有效"""
    try:
        comment_service = CommentService()
        result = await comment_service.verify_cookie()
        return jsonify(result)
    except Exception as e:
        logger.error(f"验证cookie时出错: {str(e)}")
        return jsonify({
            'error': '验证cookie失败',
            'detail': str(e)
        }), 500

@api.route('/cookie/update', methods=['POST'])
@jwt_required()
async def update_cookie():
    """更新 cookie"""
    try:
        data = request.get_json()
        
        # 支持两种格式：字符串格式和 JSON 数组格式
        if isinstance(data.get('cookie'), list):
            # JSON 数组格式
            cookies_json = data.get('cookie')
            comment_service = CommentService()
            result = await comment_service.update_cookie_from_json(cookies_json)
        elif isinstance(data.get('cookie'), str):
            # 字符串格式
            new_cookie = data.get('cookie')
            if not new_cookie:
                return jsonify({'error': '请提供新的cookie'}), 400
            comment_service = CommentService()
            result = await comment_service.update_cookie(new_cookie)
        else:
            return jsonify({'error': '无效的cookie格式，请提供字符串或JSON数组格式的cookie'}), 400
            
        if result['success']:
            # 更新成功后，同时更新环境变量中的cookie
            current_app.config['DOUYIN_COOKIE'] = result.get('cookie', '')
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"更新cookie时出错: {str(e)}")
        return jsonify({
            'error': '更新cookie失败',
            'detail': str(e)
        }), 500 