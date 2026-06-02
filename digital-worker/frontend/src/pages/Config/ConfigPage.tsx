import React from 'react';
import { Tabs, Card, Typography } from 'antd';
import { SettingOutlined, BranchesOutlined, FlagOutlined, ScheduleOutlined, UnorderedListOutlined } from '@ant-design/icons';
import StageConfigTab from './StageConfigTab';
import MilestoneConfigTab from './MilestoneConfigTab';
import WorkPlanConfigTab from './WorkPlanConfigTab';
import TaskConfigTab from './TaskConfigTab';

const { Title } = Typography;

const ConfigPage: React.FC = () => {
  return (
    <div style={{ padding: 16 }}>
      <Card style={{ marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          <SettingOutlined style={{ marginRight: 8, color: '#1677ff' }} />
          配置中心
        </Title>
      </Card>
      <Card>
        <Tabs
          items={[
            {
              key: 'stages',
              label: (
                <span>
                  <BranchesOutlined style={{ marginRight: 4 }} />
                  作业阶段
                </span>
              ),
              children: <StageConfigTab />,
            },
            {
              key: 'milestones',
              label: (
                <span>
                  <FlagOutlined style={{ marginRight: 4 }} />
                  里程碑
                </span>
              ),
              children: <MilestoneConfigTab />,
            },
            {
              key: 'workplans',
              label: (
                <span>
                  <ScheduleOutlined style={{ marginRight: 4 }} />
                  作业计划
                </span>
              ),
              children: <WorkPlanConfigTab />,
            },
            {
              key: 'tasks',
              label: (
                <span>
                  <UnorderedListOutlined style={{ marginRight: 4 }} />
                  任务列表
                </span>
              ),
              children: <TaskConfigTab />,
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default ConfigPage;
