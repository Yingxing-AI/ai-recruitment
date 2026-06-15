import { CalendarOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Empty, Space, Typography } from 'antd';

export default function Interviews() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>面试管理</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />}>安排面试</Button>
      </div>
      <div className="panel">
        <Empty image={<CalendarOutlined style={{ fontSize: 48 }} />} description="暂无面试安排">
          <Space>
            <Button>查看本周</Button>
            <Button type="primary">新建安排</Button>
          </Space>
        </Empty>
      </div>
    </>
  );
}
