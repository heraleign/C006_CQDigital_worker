import React from 'react';
import { useLocation } from 'react-router-dom';
import { Layout, Badge, Popover, List, Button, Avatar, Dropdown, Space, Typography } from 'antd';
import {
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/useAuthStore';

const { Text } = Typography;

const breadcrumbMap: Record<string, string> = {
  '/dashboard': '总览看板',
  '/audit/field-config': '指标配置',
  '/audit/rule-generate': 'AI规则生成',
  '/audit/rule-confirm': '规则确认',
  '/audit/alert-manage': '告警管理',
  '/audit/result-view': '结果视图',
  '/root-cause/knowledge-base': '知识库',
  '/root-cause/analysis': '智能分析',
  '/root-cause/case-library': '案例库',
  '/root-cause/suggestion': '改进建议',
  '/monthly/daily-report': '出账日报',
  '/monthly/ledger-display': '月账进度',
  '/monthly/report-publish': '报表发布',
  '/settings/tools': '工具注册',
  '/settings/prompts': 'Prompt管理',
  '/settings/knowledge-base': '知识库',
  '/settings/notifications': '通知配置',
  '/settings/user-manage': '用户管理',
};

const notifications = [
  { id: '1', title: '稽核任务TASK_0005执行失败', time: '5分钟前', type: 'error' },
  { id: '2', title: '收入数据异常波动告警', time: '15分钟前', type: 'warning' },
  { id: '3', title: '月账处理进度已达75%', time: '1小时前', type: 'info' },
];

const Header: React.FC = () => {
  const location = useLocation();
  const { currentUser, logout } = useAuthStore();
  const currentPage = breadcrumbMap[location.pathname] || '';

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '账号设置',
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
      onClick: () => logout(),
    },
  ];

  const notificationContent = (
    <div style={{ width: 320 }}>
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid #f0f0f0',
          fontWeight: 600,
          fontSize: 14,
        }}
      >
        消息通知
      </div>
      <List
        dataSource={notifications}
        renderItem={(item) => (
          <List.Item
            style={{ padding: '10px 16px', cursor: 'pointer' }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#f5f5f5';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'transparent';
            }}
          >
            <List.Item.Meta
              title={
                <Space size={4}>
                  <Badge
                    status={
                      item.type === 'error'
                        ? 'error'
                        : item.type === 'warning'
                        ? 'warning'
                        : 'processing'
                    }
                  />
                  <Text style={{ fontSize: 13 }}>{item.title}</Text>
                </Space>
              }
              description={<Text type="secondary" style={{ fontSize: 12 }}>{item.time}</Text>}
            />
          </List.Item>
        )}
      />
      <div
        style={{
          padding: '8px 16px',
          borderTop: '1px solid #f0f0f0',
          textAlign: 'center',
        }}
      >
        <Button type="link" size="small">
          查看全部
        </Button>
      </div>
    </div>
  );

  return (
    <Layout.Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#fff',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 99,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          数据运维数字员工
        </Text>
        {currentPage && (
          <>
            <span style={{ margin: '0 8px', color: '#d9d9d9' }}>/</span>
            <Text strong style={{ fontSize: 14 }}>
              {currentPage}
            </Text>
          </>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <Popover content={notificationContent} trigger="click" placement="bottomRight">
          <Badge count={notifications.length} size="small">
            <BellOutlined style={{ fontSize: 18, cursor: 'pointer', color: '#595959' }} />
          </Badge>
        </Popover>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar
              size={32}
              icon={<UserOutlined />}
              style={{ backgroundColor: '#1677ff' }}
            />
            <span style={{ fontSize: 13 }}>{currentUser?.real_name || '管理员'}</span>
          </Space>
        </Dropdown>
      </div>
    </Layout.Header>
  );
};

export default Header;
