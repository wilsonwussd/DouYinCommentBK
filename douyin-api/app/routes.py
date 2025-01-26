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

@api.route('/comments/collect', methods=['POST'])
@jwt_required()
async def collect_comments():
    """采集评论接口"""
    try:
        data = request.get_json()
        if not data:
            logger.error("Request body is empty")
            return jsonify({'error': '请求体不能为空'}), 400
            
        video_id = data.get('video_id')
        max_comments = data.get('max_comments', 100)
        
        if not video_id:
            logger.error("Video ID is missing")
            return jsonify({'error': '视频ID不能为空'}), 400
            
        if not isinstance(max_comments, int) or max_comments <= 0:
            logger.error(f"Invalid max_comments value: {max_comments}")
            return jsonify({'error': '评论数量必须是正整数'}), 400
            
        cookie = current_app.config.get('DOUYIN_COOKIE')
        if not cookie:
            logger.error("DOUYIN_COOKIE is not set in configuration")
            return jsonify({'error': '抖音cookie未配置'}), 500
            
        logger.info(f"Starting comment collection for video {video_id}")
        logger.debug(f"Cookie length: {len(cookie)}")
        logger.debug(f"Request parameters - video_id: {video_id}, max_comments: {max_comments}")
        
        try:
            service = CommentService(cookie)
            comments = await service.collect_comments(video_id, max_comments)
            
            if not comments:
                logger.warning(f"No comments collected for video {video_id}")
                return jsonify({
                    'message': '未采集到评论',
                    'comments': []
                }), 200
                
            saved_comments = Comment.query.filter_by(video_id=video_id).all()
            logger.info(f"Successfully collected and saved {len(saved_comments)} comments")
            
            return jsonify({
                'message': f'成功采集 {len(comments)} 条评论',
                'comments': [comment.to_dict() for comment in saved_comments]
            }), 200
            
        except ValueError as e:
            logger.error(f"Value error in comment collection: {str(e)}")
            return jsonify({
                'error': '参数错误',
                'detail': str(e)
            }), 400
            
        except Exception as e:
            logger.error(f"Error collecting comments: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': '采集评论失败',
                'detail': str(e),
                'traceback': traceback.format_exc()
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': '请求处理失败',
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