import React, { Suspense } from 'react';
import { Navigate, useRoutes } from 'react-router-dom';
import { Spin } from 'antd';
import MainLayout from '@/layouts/MainLayout';

const Loading = () => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '50vh',
    }}
  >
    <Spin size="large" tip="加载中..." />
  </div>
);

const SuspenseWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<Loading />}>{children}</Suspense>
);

const Dashboard = React.lazy(() => import('@/pages/Dashboard/index'));
const FieldConfig = React.lazy(() => import('@/pages/Audit/FieldConfig'));
const RuleGenerate = React.lazy(() => import('@/pages/Audit/RuleGenerate'));
const RuleConfirm = React.lazy(() => import('@/pages/Audit/RuleConfirm'));
const AlertManage = React.lazy(() => import('@/pages/Audit/AlertManage'));
const ResultView = React.lazy(() => import('@/pages/Audit/ResultView'));
const KnowledgeBase = React.lazy(() => import('@/pages/RootCause/KnowledgeBase'));
const Analysis = React.lazy(() => import('@/pages/RootCause/Analysis'));
const CaseLibrary = React.lazy(() => import('@/pages/RootCause/CaseLibrary'));
const Suggestions = React.lazy(() => import('@/pages/RootCause/Suggestions'));
const TaskList = React.lazy(() => import('@/pages/RootCause/TaskList'));
const DailyReport = React.lazy(() => import('@/pages/Monthly/DailyReport'));
const ReportPublish = React.lazy(() => import('@/pages/Monthly/ReportPublish'));
const LedgerDisplay = React.lazy(() => import('@/pages/Monthly/LedgerDisplay'));
const Tools = React.lazy(() => import('@/pages/Settings/Tools'));
const Prompts = React.lazy(() => import('@/pages/Settings/Prompts'));
const SettingsKnowledgeBase = React.lazy(() => import('@/pages/Settings/KnowledgeBase'));
const Notifications = React.lazy(() => import('@/pages/Settings/Notifications'));
const UserManage = React.lazy(() => import('@/pages/Settings/UserManage'));
const ConfigPage = React.lazy(() => import('@/pages/Config/ConfigPage'));
const HermesPlayground = React.lazy(() => import('@/pages/Hermes/Playground'));

const routeConfig = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <SuspenseWrapper><Dashboard /></SuspenseWrapper> },
      {
        path: 'audit',
        children: [
          { path: 'field-config', element: <SuspenseWrapper><FieldConfig /></SuspenseWrapper> },
          { path: 'rule-generate', element: <SuspenseWrapper><RuleGenerate /></SuspenseWrapper> },
          { path: 'rule-confirm', element: <SuspenseWrapper><RuleConfirm /></SuspenseWrapper> },
          { path: 'alert-manage', element: <SuspenseWrapper><AlertManage /></SuspenseWrapper> },
          { path: 'result-view', element: <SuspenseWrapper><ResultView /></SuspenseWrapper> },
        ],
      },
      {
        path: 'root-cause',
        children: [
          { path: 'knowledge-base', element: <SuspenseWrapper><KnowledgeBase /></SuspenseWrapper> },
          { path: 'analysis', element: <SuspenseWrapper><Analysis /></SuspenseWrapper> },
          { path: 'case-library', element: <SuspenseWrapper><CaseLibrary /></SuspenseWrapper> },
          { path: 'suggestion', element: <SuspenseWrapper><Suggestions /></SuspenseWrapper> },
          { path: 'task-list', element: <SuspenseWrapper><TaskList /></SuspenseWrapper> },
          { path: 'hermes', element: <SuspenseWrapper><HermesPlayground /></SuspenseWrapper> },
        ],
      },
      {
        path: 'monthly',
        children: [
          { path: 'daily-report', element: <SuspenseWrapper><DailyReport /></SuspenseWrapper> },
          { path: 'report-publish', element: <SuspenseWrapper><ReportPublish /></SuspenseWrapper> },
          { path: 'ledger-display', element: <SuspenseWrapper><LedgerDisplay /></SuspenseWrapper> },
          { path: 'config', element: <SuspenseWrapper><ConfigPage /></SuspenseWrapper> },
        ],
      },
      { path: 'config', element: <Navigate to="/monthly/config" replace /> },
      {
        path: 'settings',
        children: [
          { path: 'tools', element: <SuspenseWrapper><Tools /></SuspenseWrapper> },
          { path: 'prompts', element: <SuspenseWrapper><Prompts /></SuspenseWrapper> },
          { path: 'knowledge-base', element: <SuspenseWrapper><SettingsKnowledgeBase /></SuspenseWrapper> },
          { path: 'notifications', element: <SuspenseWrapper><Notifications /></SuspenseWrapper> },
          { path: 'user-manage', element: <SuspenseWrapper><UserManage /></SuspenseWrapper> },
        ],
      },
    ],
  },
];

const AppRoutes: React.FC = () => {
  return useRoutes(routeConfig);
};

export default AppRoutes;
