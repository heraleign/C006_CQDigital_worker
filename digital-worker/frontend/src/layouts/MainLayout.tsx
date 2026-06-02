import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Layout, Badge, Space, Typography } from 'antd';
import Sidebar from './Sidebar';
import Header from './Header';
import AssistantDrawer from './AssistantDrawer';

const { Content, Footer } = Layout;
const { Text } = Typography;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar collapsed={collapsed} onCollapse={setCollapsed} />
      <Layout
        style={{
          marginLeft: collapsed ? 64 : 240,
          transition: 'margin-left 0.2s',
        }}
      >
        <Header />
        <Content
          style={{
            padding: 20,
            background: '#f0f2f5',
            minHeight: 'calc(100vh - 56px - 50px)',
          }}
        >
          <Outlet />
        </Content>
        <Footer className="app-footer">
          <Space split={<span className="footer-divider" />}>
            <Text type="secondary" style={{ fontSize: 12 }}>数据运维数字员工 v1.0</Text>
            <Text type="secondary" style={{ fontSize: 12 }}>© 2026 重庆电信</Text>
            <span>
              <Badge status="success" />
              <Text type="secondary" style={{ fontSize: 12, marginLeft: 4 }}>系统运行正常</Text>
            </span>
          </Space>
        </Footer>
      </Layout>
      <AssistantDrawer />
    </Layout>
  );
};

export default MainLayout;
