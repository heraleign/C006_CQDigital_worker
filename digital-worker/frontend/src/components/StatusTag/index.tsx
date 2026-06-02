import React from 'react';
import { Tag } from 'antd';
import {
  CheckCircleOutlined,
  SyncOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  MinusCircleOutlined,
  EditOutlined,
} from '@ant-design/icons';

interface StatusTagProps {
  status: string;
  type?: 'audit' | 'task' | 'alert' | 'common';
}

const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
  // Common statuses
  active: { color: 'success', icon: <CheckCircleOutlined />, text: '启用' },
  inactive: { color: 'default', icon: <MinusCircleOutlined />, text: '停用' },
  draft: { color: 'gold', icon: <EditOutlined />, text: '草稿' },

  // Task statuses
  running: { color: 'processing', icon: <SyncOutlined spin />, text: '运行中' },
  completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
  failed: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
  pending: { color: 'warning', icon: <ClockCircleOutlined />, text: '待处理' },
  waiting: { color: 'default', icon: <MinusCircleOutlined />, text: '等待中' },
  success: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },

  // Alert statuses
  new: { color: 'error', icon: <CloseCircleOutlined />, text: '新增' },
  processing: { color: 'processing', icon: <SyncOutlined spin />, text: '处理中' },
  resolved: { color: 'success', icon: <CheckCircleOutlined />, text: '已解决' },
  ignored: { color: 'default', icon: <MinusCircleOutlined />, text: '已忽略' },

  // Alert levels
  high: { color: 'error', icon: <CloseCircleOutlined />, text: '严重' },
  medium: { color: 'warning', icon: <ClockCircleOutlined />, text: '警告' },
  low: { color: 'default', icon: <MinusCircleOutlined />, text: '提示' },

  // Monthly statuses
  scheduled: { color: 'processing', icon: <SyncOutlined />, text: '已计划' },
  published: { color: 'success', icon: <CheckCircleOutlined />, text: '已发布' },
  generating: { color: 'processing', icon: <SyncOutlined spin />, text: '生成中' },
  archived: { color: 'default', icon: <MinusCircleOutlined />, text: '已归档' },

  // Analysis statuses
  analyzing: { color: 'processing', icon: <SyncOutlined spin />, text: '分析中' },

  // Suggestion / case statuses
  accepted: { color: 'success', icon: <CheckCircleOutlined />, text: '已采纳' },
  implemented: { color: 'processing', icon: <SyncOutlined />, text: '实施中' },
  rejected: { color: 'default', icon: <MinusCircleOutlined />, text: '已驳回' },
};

const getDefaultConfig = (status: string) => {
  if (status === 'active' || status === 'completed' || status === 'published' || status === 'resolved' || status === 'success' || status === 'accepted') {
    return { color: 'success' as const, icon: <CheckCircleOutlined />, text: status };
  }
  if (status === 'running' || status === 'processing' || status === 'analyzing' || status === 'scheduled' || status === 'generating') {
    return { color: 'processing' as const, icon: <SyncOutlined />, text: status };
  }
  if (status === 'failed' || status === 'new' || status === 'high') {
    return { color: 'error' as const, icon: <CloseCircleOutlined />, text: status };
  }
  if (status === 'pending' || status === 'medium' || status === 'draft') {
    return { color: 'warning' as const, icon: <ClockCircleOutlined />, text: status };
  }
  return { color: 'default' as const, icon: <MinusCircleOutlined />, text: status };
};

const StatusTag: React.FC<StatusTagProps> = ({ status, type }) => {
  const config = statusConfig[status] || getDefaultConfig(status);

  return (
    <Tag color={config.color} icon={config.icon} style={{ borderRadius: 4, margin: 0 }}>
      {config.text}
    </Tag>
  );
};

export default StatusTag;
