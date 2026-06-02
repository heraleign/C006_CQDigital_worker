import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


class SysUser(Base):
    """系统用户"""
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, comment="用户名")
    password = Column(String(200), nullable=False, comment="密码")
    real_name = Column(String(100), comment="真实姓名")
    email = Column(String(200), comment="邮箱")
    phone = Column(String(20), comment="手机号")
    avatar = Column(String(500), comment="头像")
    department_id = Column(Integer, ForeignKey("sys_department.id"), comment="部门ID")
    position = Column(String(100), comment="职位")
    status = Column(Integer, default=1, comment="状态: 0禁用 1启用")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    last_login_time = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    remark = Column(Text, comment="备注")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    department = relationship("SysDepartment", backref="users")
    roles = relationship("SysRole", secondary="sys_user_role", back_populates="users")


class SysRole(Base):
    """系统角色"""
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), unique=True, nullable=False, comment="角色名称")
    role_code = Column(String(100), unique=True, comment="角色编码")
    description = Column(Text, comment="描述")
    status = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    users = relationship("SysUser", secondary="sys_user_role", back_populates="roles")
    permissions = relationship("SysPermission", secondary="sys_role_permission", back_populates="roles")


class SysUserRole(Base):
    """用户角色关联"""
    __tablename__ = "sys_user_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


class SysPermission(Base):
    """系统权限"""
    __tablename__ = "sys_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_name = Column(String(100), nullable=False, comment="权限名称")
    permission_code = Column(String(100), unique=True, comment="权限编码")
    menu_path = Column(String(200), comment="菜单路径")
    parent_id = Column(Integer, ForeignKey("sys_permission.id"), comment="父权限ID")
    permission_type = Column(String(20), default="menu", comment="类型: menu/button/api")
    icon = Column(String(100), comment="图标")
    sort_order = Column(Integer, default=0)
    description = Column(Text, comment="描述")
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    children = relationship("SysPermission", backref="parent", remote_side=[id])
    roles = relationship("SysRole", secondary="sys_role_permission", back_populates="permissions")


class SysRolePermission(Base):
    """角色权限关联"""
    __tablename__ = "sys_role_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("sys_permission.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


class SysDepartment(Base):
    """部门"""
    __tablename__ = "sys_department"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(200), nullable=False, comment="部门名称")
    dept_code = Column(String(100), unique=True, comment="部门编码")
    parent_id = Column(Integer, ForeignKey("sys_department.id"), comment="上级部门ID")
    dept_level = Column(Integer, default=1, comment="部门层级")
    dept_type = Column(String(50), comment="部门类型")
    manager = Column(String(100), comment="部门负责人")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(200), comment="邮箱")
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    description = Column(Text, comment="描述")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    children = relationship("SysDepartment", backref="parent", remote_side=[id])


class SysAuditLog(Base):
    """操作审计日志"""
    __tablename__ = "sys_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), comment="用户ID")
    username = Column(String(100), comment="用户名")
    action_type = Column(String(50), comment="操作类型: create/update/delete/query/login/logout")
    module = Column(String(50), comment="功能模块")
    action_detail = Column(Text, comment="操作详情")
    request_url = Column(String(500), comment="请求URL")
    request_method = Column(String(10), comment="请求方法")
    request_params = Column(JSON, comment="请求参数")
    response_code = Column(Integer, comment="响应码")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="User-Agent")
    duration_ms = Column(Integer, comment="耗时(毫秒)")
    status = Column(String(10), default="success", comment="状态: success/failure")
    created_at = Column(DateTime, default=datetime.datetime.now)


class SysConfig(Base):
    """系统配置"""
    __tablename__ = "sys_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(200), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, comment="配置值")
    config_type = Column(String(50), comment="配置类型: system/business/alert/notification")
    description = Column(Text, comment="描述")
    is_encrypted = Column(Boolean, default=False, comment="是否加密")
    status = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class SysDataDict(Base):
    """数据字典"""
    __tablename__ = "sys_data_dict"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dict_key = Column(String(100), comment="字典键")
    dict_value = Column(String(200), nullable=False, comment="字典值")
    dict_type = Column(String(100), nullable=False, comment="字典类型")
    parent_id = Column(Integer, ForeignKey("sys_data_dict.id"), comment="父字典ID")
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class SysNotificationRecord(Base):
    """通知记录"""
    __tablename__ = "sys_notification_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_type = Column(String(50), comment="通知类型: alert/reminder/system/business")
    title = Column(String(300), comment="标题")
    content = Column(Text, comment="内容")
    receiver_id = Column(Integer, ForeignKey("sys_user.id"), comment="接收人ID")
    receiver_name = Column(String(100), comment="接收人名称")
    channel = Column(String(50), comment="渠道: system/email/sms/dingtalk/wechat")
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_time = Column(DateTime, comment="阅读时间")
    status = Column(String(20), default="sent", comment="状态: sent/delivered/failed")
    send_time = Column(DateTime, comment="发送时间")
    created_at = Column(DateTime, default=datetime.datetime.now)
