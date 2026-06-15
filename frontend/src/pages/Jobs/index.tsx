import { PlusOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Space, Table, Tag, Typography } from 'antd';
import { fetchJobs } from '../../api/jobs';

const statusMap: Record<string, string> = {
  draft: '默认',
  open: '绿色',
  paused: '橙色',
  closed: '红色'
};

export default function Jobs() {
  const { data = [], isLoading } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>职位管理</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />}>新建职位</Button>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          columns={[
            { title: '职位', dataIndex: 'title' },
            { title: '地点', dataIndex: 'location' },
            { title: '人数', dataIndex: 'headcount', width: 90 },
            { title: '状态', dataIndex: 'status', render: (status) => <Tag>{statusMap[status] ?? status}</Tag> },
            { title: '更新时间', dataIndex: 'updated_at', render: (value) => new Date(value).toLocaleString() },
            { title: '操作', render: () => <Space><Button type="link">详情</Button><Button type="link">匹配</Button></Space> }
          ]}
        />
      </div>
    </>
  );
}
