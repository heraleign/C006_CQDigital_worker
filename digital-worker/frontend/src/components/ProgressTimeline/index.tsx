import React from 'react';
import { Steps, Typography } from 'antd';
import {
  CheckCircleOutlined,
  SyncOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface MilestoneItem {
  name: string;
  status: string;
  time: string;
}

interface ProgressTimelineProps {
  milestones: MilestoneItem[];
  current?: number;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircleOutlined />;
    case 'running':
    case 'processing':
      return <SyncOutlined spin />;
    case 'failed':
      return <CloseCircleOutlined />;
    case 'pending':
    case 'waiting':
      return <ClockCircleOutlined />;
    default:
      return <MinusCircleOutlined />;
  }
};

const getStatusForStep = (status: string): 'wait' | 'process' | 'finish' | 'error' => {
  switch (status) {
    case 'completed':
      return 'finish';
    case 'running':
    case 'processing':
      return 'process';
    case 'failed':
      return 'error';
    case 'pending':
    case 'waiting':
    default:
      return 'wait';
  }
};

const ProgressTimeline: React.FC<ProgressTimelineProps> = ({ milestones, current }) => {
  if (!milestones || milestones.length === 0) {
    return <Text type="secondary">暂无里程碑数据</Text>;
  }

  return (
    <div style={{ padding: '16px 0', overflowX: 'auto' }}>
      <Steps
        current={current ?? milestones.findIndex((m) => m.status === 'running' || m.status === 'processing')}
        size="small"
        style={{ minWidth: milestones.length * 160 }}
      >
        {milestones.map((milestone, index) => (
          <Steps.Step
            key={index}
            status={getStatusForStep(milestone.status)}
            title={
              <Text style={{ fontSize: 13, whiteSpace: 'nowrap' }}>{milestone.name}</Text>
            }
            description={
              milestone.time ? (
                <Text type="secondary" style={{ fontSize: 11, whiteSpace: 'nowrap' }}>
                  {milestone.time}
                </Text>
              ) : undefined
            }
            icon={getStatusIcon(milestone.status)}
          />
        ))}
      </Steps>
    </div>
  );
};

export default ProgressTimeline;
