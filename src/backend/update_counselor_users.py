"""
更新咨询师用户密码并初始化咨询师信息
为以下用户重置密码并初始化咨询师信息：
- 一颗米粒
- 泡泡金鱼
- 烤焦面包
- 包袱
- 梅干
"""

from database import SessionLocal
from models import Counselor, User, UserRole, Gender, CounselorStatus
from auth import get_password_hash
from sqlalchemy import text
import json
import random

def get_name_initials(name: str) -> str:
    """获取姓名首字母小写缩写"""
    if not name:
        return ""
    # 移除空格
    name = name.strip()
    
    # 特殊处理：针对这些特定用户名
    special_names = {
        '一颗米粒': 'ykl',
        '泡泡金鱼': 'ppj',
        '烤焦面包': 'kjm',
        '包袱': 'bf',
        '梅干': 'mg'
    }
    
    if name in special_names:
        return special_names[name]
    
    # 获取每个字符的首字母（支持中文）
    initials = []
    # 中文拼音首字母映射（扩展版）
    pinyin_map = {
        '一': 'y', '颗': 'k', '米': 'm', '粒': 'l',
        '泡': 'p', '金': 'j', '鱼': 'y',
        '烤': 'k', '焦': 'j', '面': 'm', '包': 'b',
        '袱': 'f',
        '梅': 'm', '干': 'g',
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
    
    for char in name:
        if char.isalpha():
            # 如果是中文，取拼音首字母
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                if char in pinyin_map:
                    initials.append(pinyin_map[char])
                else:
                    # 如果不在映射中，使用默认值
                    initials.append('x')
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

# 擅长领域选项
SPECIALTIES = [
    "学业压力", "情感困扰", "人际关系", "情绪管理", "焦虑抑郁",
    "职业规划", "家庭关系", "自我成长", "心理创伤", "睡眠问题",
    "社交恐惧", "强迫症", "适应障碍", "压力管理", "情绪调节"
]

# 咨询方式选项
CONSULT_METHODS = ["线下", "视频", "文字", "语音"]

# 资质证书选项
QUALIFICATIONS = [
    "国家二级心理咨询师",
    "国家三级心理咨询师",
    "心理学硕士",
    "心理学博士",
    "心理咨询师职业资格证"
]

def get_random_specialties():
    """随机选择2-4个擅长领域"""
    count = random.randint(2, 4)
    return random.sample(SPECIALTIES, count)

def get_random_consult_methods():
    """随机选择1-3种咨询方式"""
    count = random.randint(1, 3)
    return random.sample(CONSULT_METHODS, count)

def get_random_gender():
    """随机性别"""
    return random.choice([Gender.MALE, Gender.FEMALE, Gender.OTHER])

def update_counselor_users():
    """更新咨询师用户密码并初始化信息"""
    db = SessionLocal()
    try:
        # 先检查并添加age字段（如果不存在）
        try:
            db.execute(text("ALTER TABLE counselors ADD COLUMN age INT NULL"))
            db.commit()
            print("[OK] 已添加 age 字段到 counselors 表")
        except Exception as e:
            # 字段可能已存在，忽略错误
            db.rollback()
            if "Duplicate column name" not in str(e) and "already exists" not in str(e).lower():
                print(f"  注意: {str(e)}")
        # 需要更新的用户列表
        usernames = ["一颗米粒", "泡泡金鱼", "烤焦面包", "包袱", "梅干"]
        
        updated_count = 0
        created_counselor_count = 0
        
        for username in usernames:
            # 查找用户
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                print(f"[ERROR] 用户不存在: {username}")
                continue
            
            # 1. 更新密码
            initials = get_name_initials(username)
            password = f"123456{initials}"
            user.password_hash = get_password_hash(password)
            
            # 2. 确保角色是COUNSELOR
            user.role = UserRole.COUNSELOR
            user.is_active = True
            
            # 3. 检查是否有Counselor记录（只查询基本字段）
            result = db.execute(
                text("SELECT id, user_id, real_name, specialty, status FROM counselors WHERE user_id = :user_id"),
                {"user_id": user.id}
            ).fetchone()
            
            if not result:
                # 创建Counselor记录
                specialties = get_random_specialties()
                consult_methods = get_random_consult_methods()
                gender = get_random_gender()
                age = random.randint(25, 45)
                experience_years = random.randint(2, 10)
                fee = random.choice([50.0, 80.0, 100.0, 120.0, 150.0])
                qualification = random.choice(QUALIFICATIONS)
                specialty_json = json.dumps(specialties, ensure_ascii=False)
                consult_methods_json = json.dumps(consult_methods, ensure_ascii=False)
                bio_text = f"我是一位经验丰富的心理咨询师，专注于{specialties[0]}和{specialties[1]}等领域。"
                intro_text = f"我拥有{experience_years}年的心理咨询经验，擅长通过{consult_methods[0]}等方式为来访者提供专业的心理支持。"
                
                # 使用原始SQL插入，只插入基本必需字段
                # 先尝试插入所有字段，如果失败则只插入基本字段
                try:
                    db.execute(
                        text("""
                            INSERT INTO counselors 
                            (user_id, real_name, gender, age, specialty, experience_years, qualification, 
                             bio, intro, consult_methods, fee, consult_place, max_daily_appointments, status)
                            VALUES 
                            (:user_id, :real_name, :gender, :age, :specialty, :experience_years, :qualification,
                             :bio, :intro, :consult_methods, :fee, :consult_place, :max_daily_appointments, :status)
                        """),
                        {
                            "user_id": user.id,
                            "real_name": username,
                            "gender": gender.value,
                            "age": age,
                            "specialty": specialty_json,
                            "experience_years": experience_years,
                            "qualification": qualification,
                            "bio": bio_text,
                            "intro": intro_text,
                            "consult_methods": consult_methods_json,
                            "fee": fee,
                            "consult_place": "心理咨询中心",
                            "max_daily_appointments": random.randint(3, 5),
                            "status": CounselorStatus.ACTIVE.value
                        }
                    )
                except Exception as e:
                    # 如果字段不存在，只插入基本字段
                    db.rollback()
                    db.execute(
                        text("""
                            INSERT INTO counselors 
                            (user_id, real_name, gender, specialty, experience_years, status)
                            VALUES 
                            (:user_id, :real_name, :gender, :specialty, :experience_years, :status)
                        """),
                        {
                            "user_id": user.id,
                            "real_name": username,
                            "gender": gender.value,
                            "specialty": specialty_json,
                            "experience_years": experience_years,
                            "status": CounselorStatus.ACTIVE.value
                        }
                    )
                db.commit()
                created_counselor_count += 1
                print(f"[OK] 创建咨询师记录: {username}")
            else:
                # 更新现有Counselor记录（如果信息不完整）
                counselor_id, _, _, specialty, status_val = result
                
                update_fields = {}
                
                # 检查并更新specialty
                if not specialty or specialty == "[]":
                    specialties = get_random_specialties()
                    update_fields["specialty"] = json.dumps(specialties, ensure_ascii=False)
                
                # 检查并更新status
                if status_val != CounselorStatus.ACTIVE.value:
                    update_fields["status"] = CounselorStatus.ACTIVE.value
                
                # 尝试更新其他字段（如果存在）
                try:
                    # 检查consult_methods字段
                    consult_methods_result = db.execute(
                        text("SELECT consult_methods FROM counselors WHERE id = :counselor_id"),
                        {"counselor_id": counselor_id}
                    ).fetchone()
                    if consult_methods_result and (not consult_methods_result[0] or consult_methods_result[0] == "[]"):
                        consult_methods_list = get_random_consult_methods()
                        update_fields["consult_methods"] = json.dumps(consult_methods_list, ensure_ascii=False)
                except:
                    pass
                
                try:
                    # 检查bio字段
                    bio_result = db.execute(
                        text("SELECT bio FROM counselors WHERE id = :counselor_id"),
                        {"counselor_id": counselor_id}
                    ).fetchone()
                    if bio_result and not bio_result[0]:
                        update_fields["bio"] = "我是一位经验丰富的心理咨询师，专注于帮助来访者解决心理困扰。"
                except:
                    pass
                
                try:
                    # 检查fee字段
                    fee_result = db.execute(
                        text("SELECT fee FROM counselors WHERE id = :counselor_id"),
                        {"counselor_id": counselor_id}
                    ).fetchone()
                    if fee_result and (not fee_result[0] or fee_result[0] == 0):
                        update_fields["fee"] = random.choice([50.0, 80.0, 100.0, 120.0, 150.0])
                except:
                    pass
                
                try:
                    # 检查qualification字段
                    qual_result = db.execute(
                        text("SELECT qualification FROM counselors WHERE id = :counselor_id"),
                        {"counselor_id": counselor_id}
                    ).fetchone()
                    if qual_result and not qual_result[0]:
                        update_fields["qualification"] = random.choice(QUALIFICATIONS)
                except:
                    pass
                
                try:
                    # 检查age字段
                    age_result = db.execute(
                        text("SELECT age FROM counselors WHERE id = :counselor_id"),
                        {"counselor_id": counselor_id}
                    ).fetchone()
                    if age_result and (not age_result[0] or age_result[0] == 0):
                        update_fields["age"] = random.randint(25, 45)
                except:
                    pass
                
                if update_fields:
                    set_clauses = ", ".join([f"{k} = :{k}" for k in update_fields.keys()])
                    update_sql = f"UPDATE counselors SET {set_clauses} WHERE id = :counselor_id"
                    update_fields["counselor_id"] = counselor_id
                    db.execute(text(update_sql), update_fields)
                    db.commit()
                    print(f"[OK] 更新咨询师记录: {username}")
                else:
                    print(f"[OK] 咨询师记录已完整: {username}")
            
            # 提交用户更改
            db.commit()
            updated_count += 1
            
            print(f"  → 用户名: {username}")
            print(f"  → 新密码: {password}")
            print(f"  → 角色: COUNSELOR")
            # 查询咨询师信息用于显示
            counselor_info = db.execute(
                text("SELECT id, specialty, consult_methods, status FROM counselors WHERE user_id = :user_id"),
                {"user_id": user.id}
            ).fetchone()
            if counselor_info:
                counselor_id, specialty, consult_methods, status_val = counselor_info
                print(f"  → 咨询师ID: {counselor_id}")
                print(f"  → 状态: {status_val}")
                try:
                    specialty_list = json.loads(specialty) if specialty and specialty != "[]" else []
                    print(f"  → 擅长领域: {specialty_list}")
                except:
                    print(f"  → 擅长领域: {specialty if specialty else '[]'}")
                try:
                    methods_list = json.loads(consult_methods) if consult_methods and consult_methods != "[]" else []
                    print(f"  → 咨询方式: {methods_list}")
                except:
                    print(f"  → 咨询方式: {consult_methods if consult_methods else '[]'}")
            print()
        
        print(f"\n{'='*60}")
        print(f"完成！")
        print(f"  - 更新了 {updated_count} 个用户密码")
        print(f"  - 创建了 {created_counselor_count} 个咨询师记录")
        print(f"  - 更新了 {updated_count - created_counselor_count} 个咨询师记录")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始更新咨询师用户密码并初始化信息...")
    print("="*60)
    update_counselor_users()

