import { ImportOutlined, PlusOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Space, Table, Tag, Typography } from 'antd';
import { fetchCandidates } from '../../api/candidates';

export default function Candidates() {
  const { data = [], isLoading } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>候选人管理</Typography.Title>
        <Space>
          <Button icon={<ImportOutlined />}>导入简历</Button>
          <Button type="primary" icon={<PlusOutlined />}>新建候选人</Button>
        </Space>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          columns={[
            { title: '姓名', dataIndex: 'name' },
            { title: '当前公司', dataIndex: 'current_company' },
            { title: '职位', dataIndex: 'current_title' },
            { title: '经验', dataIndex: 'years_of_experience', render: (value) => value ? `${value} 年` : '-' },
            { title: '来源', dataIndex: 'source', render: (value) => value ? <Tag>{value}</Tag> : '-' },
            { title: '状态', dataIndex: 'status' },
            { title: '操作', render: () => <Space><Button type="link">详情</Button><Button type="link">AI 分析</Button></Space> }
          ]}
        />
      </div>
    </>
  );
}
