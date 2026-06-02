import React from 'react';
import { Card, Statistic, Flex, Typography } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: 'up' | 'down';
  trendValue?: string;
  icon: React.ReactNode;
  color?: string;
  suffix?: string;
  precision?: number;
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  trend,
  trendValue,
  icon,
  color = '#1677ff',
  suffix,
  precision = 0,
  onClick,
}) => {
  return (
    <Card
      hoverable
      className="stat-card"
      onClick={onClick}
      styles={{ body: { padding: 20 } }}
    >
      <Flex align="flex-start" justify="space-between">
        <div>
          <Text type="secondary" style={{ fontSize: 13, marginBottom: 8, display: 'block' }}>
            {title}
          </Text>
          <Statistic
            value={value}
            suffix={suffix}
            precision={precision}
            valueStyle={{ fontSize: 28, fontWeight: 600, color: '#262626' }}
          />
          {trend && trendValue && (
            <div style={{ marginTop: 8 }}>
              <span
                className={trend === 'up' ? 'trend-up' : 'trend-down'}
                style={{ fontSize: 12, display: 'inline-flex', alignItems: 'center', gap: 2 }}
              >
                {trend === 'up' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                {trendValue}
              </span>
              <Text type="secondary" style={{ fontSize: 12, marginLeft: 4 }}>
                较昨日
              </Text>
            </div>
          )}
        </div>
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: 12,
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24,
            color,
            flexShrink: 0,
          }}
        >
          {icon}
        </div>
      </Flex>
    </Card>
  );
};

export default MetricCard;
