import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  SafetyCertificateOutlined,
  FundOutlined,
  CalendarOutlined,
  SettingOutlined,
  FieldBinaryOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  BellOutlined,
  EyeOutlined,
  BookOutlined,
  ExperimentOutlined,
  AppstoreOutlined,
  BulbOutlined,
  SearchOutlined,
  BarChartOutlined,
  DeploymentUnitOutlined,
  FileTextOutlined,
  SendOutlined,
  ToolOutlined,
  CodeOutlined,
  TeamOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (collapsed: boolean) => void;
}

const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '总览看板',
  },
  {
    key: 'audit',
    icon: <SafetyCertificateOutlined />,
    label: '数据质量稽核',
    children: [
      { key: '/audit/field-config', icon: <FieldBinaryOutlined />, label: '指标配置' },
      { key: '/audit/rule-generate', icon: <ThunderboltOutlined />, label: 'AI规则生成' },
      { key: '/audit/rule-confirm', icon: <CheckCircleOutlined />, label: '规则确认' },
      { key: '/audit/alert-manage', icon: <BellOutlined />, label: '告警管理' },
      { key: '/audit/result-view', icon: <EyeOutlined />, label: '结果视图' },
    ],
  },
  {
    key: 'root-cause',
    icon: <FundOutlined />,
    label: '根因分析',
    children: [
      { key: '/root-cause/knowledge-base', icon: <BookOutlined />, label: '知识库' },
      { key: '/root-cause/analysis', icon: <ExperimentOutlined />, label: '智能分析' },
      { key: '/root-cause/task-list', icon: <SearchOutlined />, label: '任务列表' },
      { key: '/root-cause/case-library', icon: <AppstoreOutlined />, label: '案例库' },
      { key: '/root-cause/suggestion', icon: <BulbOutlined />, label: '改进建议' },
      { key: '/root-cause/hermes', icon: <ExperimentOutlined />, label: 'Hermes实验' },
    ],
  },
  {
    key: 'monthly',
    icon: <CalendarOutlined />,
    label: '月账管理',
    children: [
      { key: '/monthly/daily-report', icon: <FileTextOutlined />, label: '出账日报' },
      { key: '/monthly/report-publish', icon: <SendOutlined />, label: '报表发布' },
      { key: '/monthly/ledger-display', icon: <BarChartOutlined />, label: '月账进度' },
      { key: '/monthly/config', icon: <SettingOutlined />, label: '月账配置' },
    ],
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    children: [
      { key: '/settings/tools', icon: <ToolOutlined />, label: '工具注册' },
      { key: '/settings/prompts', icon: <CodeOutlined />, label: 'Prompt管理' },
      { key: '/settings/knowledge-base', icon: <BookOutlined />, label: '知识库' },
      { key: '/settings/notifications', icon: <BellOutlined />, label: '通知配置' },
      { key: '/settings/user-manage', icon: <TeamOutlined />, label: '用户管理' },
    ],
  },
];

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onCollapse }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const findOpenKeys = () => {
    const path = location.pathname;
    if (path === '/dashboard') return [];
    if (path.startsWith('/audit')) return ['audit'];
    if (path.startsWith('/root-cause')) return ['root-cause'];
    if (path.startsWith('/monthly')) return ['monthly'];
    if (path.startsWith('/settings')) return ['settings'];
    return [];
  };

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key.startsWith('/')) {
      navigate(key);
    }
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={onCollapse}
      width={240}
      collapsedWidth={64}
      theme="light"
      style={{
        borderRight: '1px solid #f0f0f0',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div
          className="sidebar-logo"
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            background: 'linear-gradient(135deg, #1677ff 0%, #4096ff 100%)',
            flexShrink: 0,
          }}
          onClick={() => navigate('/dashboard')}
        >
          <SafetyCertificateOutlined style={{ fontSize: 28, color: '#fff' }} />
          {!collapsed && (
            <span style={{ marginLeft: 10, fontSize: 16, fontWeight: 600, color: '#fff', whiteSpace: 'nowrap' }}>
              数字员工平台
            </span>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={findOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          className="sidebar-menu"
          style={{ flex: 1, overflow: 'auto', borderRight: 0, marginTop: 4 }}
        />
        {!collapsed && (
          <div className="sidebar-bottom">
            <div className="sidebar-status">
              <span className="sidebar-status-dot" />
              <span>系统运行正常</span>
            </div>
            <span className="sidebar-version">v1.0.0</span>
          </div>
        )}
      </div>
    </Sider>
  );
};

export default Sidebar;
