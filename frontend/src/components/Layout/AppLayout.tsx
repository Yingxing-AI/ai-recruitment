import {
  ApartmentOutlined,
  BankOutlined,
  CalendarOutlined,
  DashboardOutlined,
  FileSearchOutlined,
  ImportOutlined,
  SettingOutlined,
  TeamOutlined,
  SolutionOutlined
} from '@ant-design/icons';
import { Layout, Menu, Typography } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const items = [
  { key: '/', icon: <DashboardOutlined />, label: '概览' },
  { key: '/jobs', icon: <ApartmentOutlined />, label: '职位管理' },
  { key: '/candidates', icon: <SolutionOutlined />, label: '候选人' },
  { key: '/resume-import', icon: <ImportOutlined />, label: '简历导入' },
  { key: '/applications', icon: <FileSearchOutlined />, label: '招聘流程' },
  { key: '/interviews', icon: <CalendarOutlined />, label: '面试管理' },
  { key: '/talent-pool', icon: <TeamOutlined />, label: '人才库' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' }
];

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedKey = items.find((item) => item.key !== '/' && location.pathname.startsWith(item.key))?.key ?? '/';

  return (
    <Layout className="app-shell">
      <Sider width={224} className="app-sider">
        <div className="brand">
          <BankOutlined />
          <span>AI 招聘</span>
        </div>
        <Menu mode="inline" selectedKeys={[selectedKey]} items={items} onClick={({ key }) => navigate(key)} />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Typography.Text strong>企业招聘管理工作台</Typography.Text>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
