"""
为现有心理咨询师创建账户密码
密码规则：123456 + 姓名首字母小写缩写
例如：张心怡 -> 123456zxy
"""

from database import SessionLocal
from models import Counselor, User, UserRole, Gender, CounselorStatus
from auth import get_password_hash
import re

def get_name_initials(name: str) -> str:
    """获取姓名首字母小写缩写"""
    if not name:
        return ""
    # 移除空格
    name = name.strip()
    # 获取每个字符的首字母（支持中文）
    initials = []
    for char in name:
        if char.isalpha():
            # 如果是中文，取拼音首字母（简化版，实际应该用拼音库）
            # 这里简化处理，直接取字符
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                # 简单映射一些常见姓氏
                common_surnames = {
                    '张': 'z', '王': 'w', '李': 'l', '刘': 'l', '陈': 'c',
                    '杨': 'y', '黄': 'h', '赵': 'z', '吴': 'w', '周': 'z',
                    '徐': 'x', '孙': 's', '马': 'm', '朱': 'z', '胡': 'h',
                    '郭': 'g', '何': 'h', '高': 'g', '林': 'l', '罗': 'l',
                    '郑': 'z', '梁': 'l', '谢': 'x', '宋': 's', '唐': 't',
                    '许': 'x', '韩': 'h', '冯': 'f', '邓': 'd', '曹': 'c',
                    '彭': 'p', '曾': 'z', '萧': 'x', '田': 't', '董': 'd',
                    '袁': 'y', '潘': 'p', '于': 'y', '蒋': 'j', '蔡': 'c',
                    '余': 'y', '杜': 'd', '叶': 'y', '程': 'c', '魏': 'w',
                    '苏': 's', '吕': 'l', '丁': 'd', '任': 'r', '卢': 'l',
                    '姚': 'y', '沈': 's', '钟': 'z', '姜': 'j', '崔': 'c',
                    '谭': 't', '陆': 'l', '范': 'f', '汪': 'w', '廖': 'l',
                    '石': 's', '金': 'j', '韦': 'w', '贾': 'j', '夏': 'x',
                    '付': 'f', '方': 'f', '邹': 'z', '熊': 'x', '白': 'b',
                    '孟': 'm', '秦': 'q', '邱': 'q', '江': 'j', '尹': 'y',
                    '薛': 'x', '闫': 'y', '段': 'd', '雷': 'l', '侯': 'h',
                    '龙': 'l', '史': 's', '陶': 't', '黎': 'l', '贺': 'h',
                    '顾': 'g', '毛': 'm', '郝': 'h', '龚': 'g', '邵': 's',
                    '万': 'w', '钱': 'q', '严': 'y', '覃': 'q', '武': 'w',
                    '戴': 'd', '莫': 'm', '孔': 'k', '向': 'x', '汤': 't',
                }
                # 获取姓氏拼音首字母
                if char in common_surnames:
                    initials.append(common_surnames[char])
                else:
                    # 如果不在常见姓氏中，使用拼音首字母（简化处理）
                    initials.append(char.lower() if char.isascii() else 'x')
            else:
                # 英文字母
                initials.append(char.lower())
    # 取前三个字符的首字母
    if len(initials) >= 3:
        return ''.join(initials[:3])
    elif len(initials) >= 2:
        return ''.join(initials[:2]) + 'x'
    elif len(initials) >= 1:
        return initials[0] + 'xx'
    else:
        return 'xxx'

def create_counselor_accounts():
    """为所有没有账户的咨询师创建账户"""
    db = SessionLocal()
    try:
        # 获取所有活跃的咨询师
        counselors = db.query(Counselor).filter(
            Counselor.status == CounselorStatus.ACTIVE
        ).all()
        
        created_count = 0
        skipped_count = 0
        
        for counselor in counselors:
            # 检查是否已经有用户账户
            if counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()
                if user:
                    skipped_count += 1
                    print(f"跳过：{counselor.real_name} 已有账户 (用户名: {user.username})")
                    continue
            
            # 生成用户名（使用姓名）
            username = counselor.real_name
            
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                # 如果用户名已存在，添加后缀
                username = f"{counselor.real_name}_{counselor.id}"
            
            # 生成密码：123456 + 姓名首字母小写
            initials = get_name_initials(counselor.real_name)
            password = f"123456{initials}"
            
            # 创建用户账户
            new_user = User(
                username=username,
                password_hash=get_password_hash(password),
                role=UserRole.COUNSELOR,
                is_active=True,
                nickname=counselor.real_name,
                phone=None,
                email=None
            )
            
            db.add(new_user)
            db.flush()  # 获取 user.id
            
            # 更新咨询师的 user_id
            counselor.user_id = new_user.id
            
            db.commit()
            
            created_count += 1
            print(f"✓ 创建账户：{counselor.real_name} (用户名: {username}, 密码: {password})")
        
        print(f"\n完成！创建了 {created_count} 个账户，跳过了 {skipped_count} 个已有账户的咨询师")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始为心理咨询师创建账户...")
    create_counselor_accounts()

