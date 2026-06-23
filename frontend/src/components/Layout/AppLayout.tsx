import {
  ApartmentOutlined,
  BankOutlined,
  CalendarOutlined,
  DashboardOutlined,
  FileSearchOutlined,
  MessageOutlined,
  SettingOutlined,
  TeamOutlined,
  SolutionOutlined
} from '@ant-design/icons';
import { Layout, Menu, Spin, Typography } from 'antd';
import { Suspense } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const items = [
  { key: '/', icon: <DashboardOutlined />, label: '仪表盘' },
  {
    key: 'recruitment-center',
    icon: <ApartmentOutlined />,
    label: '招聘中心',
    children: [
      { key: '/jobs', icon: <ApartmentOutlined />, label: '职位' },
      { key: '/candidates', icon: <SolutionOutlined />, label: '候选人' },
      { key: '/applications', icon: <FileSearchOutlined />, label: '招聘流程' }
    ]
  },
  {
    key: 'interview-center',
    icon: <CalendarOutlined />,
    label: '面试中心',
    children: [
      { key: '/interviews/schedule', icon: <CalendarOutlined />, label: '面试安排' },
      { key: '/interviews/feedback', icon: <MessageOutlined />, label: '面试反馈' }
    ]
  },
  { key: '/talent-pool', icon: <TeamOutlined />, label: '人才库' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' }
];

const leafKeys = ['/', '/jobs', '/candidates', '/applications', '/interviews/schedule', '/interviews/feedback', '/talent-pool', '/settings'];

function getSelectedKey(pathname: string) {
  if (pathname.startsWith('/jobs')) return '/jobs';
  if (pathname.startsWith('/candidates')) return '/candidates';
  if (pathname.startsWith('/applications')) return '/applications';
  if (pathname.startsWith('/interviews/feedback')) return '/interviews/feedback';
  if (pathname.startsWith('/interviews')) return '/interviews/schedule';
  if (pathname.startsWith('/talent-pool')) return '/talent-pool';
  if (pathname.startsWith('/settings')) return '/settings';
  return '/';
}

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedKey = getSelectedKey(location.pathname);
  const openKeys = selectedKey.startsWith('/interviews')
    ? ['interview-center']
    : selectedKey === '/jobs' || selectedKey === '/candidates' || selectedKey === '/applications'
      ? ['recruitment-center']
      : [];

  return (
    <Layout className="app-shell">
      <Sider width={224} className="app-sider">
        <div className="brand">
          <BankOutlined />
          <span>AI 招聘</span>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          defaultOpenKeys={openKeys}
          items={items}
          onClick={({ key }) => {
            if (leafKeys.includes(String(key))) {
              navigate(String(key));
            }
          }}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Typography.Text strong>企业招聘管理工作台</Typography.Text>
        </Header>
        <Content className="app-content">
          <Suspense
            fallback={
              <div className="route-loading">
                <Spin />
              </div>
            }
          >
            <Outlet />
          </Suspense>
        </Content>
      </Layout>
    </Layout>
  );
}
