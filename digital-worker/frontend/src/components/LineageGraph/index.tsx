import React, { useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react';
import type { LineageNode, LineageEdge } from '@/types';

interface LineageGraphProps {
  nodes: LineageNode[];
  edges: LineageEdge[];
  width?: number;
  height?: number;
}

const nodeColors: Record<string, string> = {
  source: '#1677ff',
  ods: '#52c41a',
  dwd: '#faad14',
  dws: '#722ed1',
  ads: '#eb2f96',
  table: '#13c2c2',
  report: '#fa8c16',
};

const LineageGraph: React.FC<LineageGraphProps> = ({ nodes, edges, width, height = 400 }) => {
  const option = useMemo(() => ({
    tooltip: {
      trigger: 'item' as const,
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<div style="font-size:12px">
            <strong>${params.name}</strong><br/>
            类型: ${params.data.itemType || params.data.type || '未知'}
          </div>`;
        }
        if (params.dataType === 'edge') {
          return `<div style="font-size:12px">
            关系: ${params.data.relation || '数据流转'}
          </div>`;
        }
        return '';
      },
      backgroundColor: 'rgba(0,0,0,0.75)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 12 },
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        force: {
          repulsion: 500,
          edgeLength: [150, 300],
          gravity: 0.1,
          friction: 0.1,
        },
        roam: true,
        draggable: true,
        symbolSize: 50,
        label: {
          show: true,
          position: 'bottom',
          fontSize: 11,
          color: '#595959',
          formatter: (params: any) => params.name,
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 10],
        lineStyle: {
          color: '#bfbfbf',
          width: 2,
          curveness: 0.2,
        },
        data: nodes.map((node) => ({
          ...node,
          itemStyle: {
            color: nodeColors[node.type] || '#1677ff',
            borderRadius: 8,
          },
          symbol: 'roundRect',
          symbolSize: [80, 36],
        })),
        edges: edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
          lineStyle: {
            color: '#bfbfbf',
          },
        })),
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4,
            color: '#1677ff',
          },
        },
      },
    ],
  }), [nodes, edges]);

  if (!nodes || nodes.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#999',
        }}
      >
        暂无数据血缘数据
      </div>
    );
  }

  return (
    <ReactEChartsCore
      option={option}
      style={{ width: '100%', height }}
      notMerge
      lazyUpdate
    />
  );
};

export default LineageGraph;
