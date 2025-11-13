"""
工具函数
"""

from models import AppointmentStatus, Gender, CounselorStatus, UserRole


def get_consult_method_display(method: str) -> str:
    """获取咨询方式的中文显示（兼容函数，现在method已经是中文）"""
    # 如果已经是中文，直接返回
    if method in ["线上视频", "线下面谈", "语音咨询", "文字咨询"]:
        return method
    # 兼容旧数据：如果是英文值，转换为中文
    method_map = {
        "video": "线上视频",
        "offline": "线下面谈",
        "voice": "语音咨询",
        "text": "文字咨询",
    }
    return method_map.get(method, method)


def get_appointment_status_display(status: AppointmentStatus) -> str:
    """获取预约状态的中文显示"""
    status_map = {
        AppointmentStatus.PENDING: "待确认",
        AppointmentStatus.CONFIRMED: "已确认",
        AppointmentStatus.COMPLETED: "已完成",
        AppointmentStatus.CANCELLED: "已取消",
        AppointmentStatus.REJECTED: "已拒绝",
    }
    return status_map.get(status, str(status))


def get_gender_display(gender: Gender) -> str:
    """获取性别的中文显示"""
    gender_map = {
        Gender.MALE: "男",
        Gender.FEMALE: "女",
        Gender.OTHER: "其他",
    }
    return gender_map.get(gender, str(gender))


def get_counselor_status_display(status: CounselorStatus) -> str:
    """获取咨询师状态的中文显示"""
    status_map = {
        CounselorStatus.PENDING: "待审核",
        CounselorStatus.ACTIVE: "在职",
        CounselorStatus.INACTIVE: "停职",
        CounselorStatus.REJECTED: "已拒绝",
    }
    return status_map.get(status, str(status))


def get_user_role_display(role: UserRole) -> str:
    """获取用户角色的中文显示"""
    role_map = {
        UserRole.USER: "普通用户",
        UserRole.COUNSELOR: "咨询师",
        UserRole.VOLUNTEER: "志愿者",
        UserRole.ADMIN: "管理员",
    }
    return role_map.get(role, str(role))

