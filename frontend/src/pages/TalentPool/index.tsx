import { SearchOutlined } from '@ant-design/icons';
import { Button, Input, Space, Table, Tag, Typography } from 'antd';

export default function TalentPool() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>人才库</Typography.Title>
        <Space>
          <Input prefix={<SearchOutlined />} placeholder="搜索技能、公司、职位" style={{ width: 280 }} />
          <Button>筛选</Button>
        </Space>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          dataSource={[
            { id: 1, name: '示例候选人', skills: ['Java', '微服务', '金融'], status: '可联系' }
          ]}
          columns={[
            { title: '姓名', dataIndex: 'name' },
            { title: '标签', dataIndex: 'skills', render: (skills: string[]) => skills.map((skill) => <Tag key={skill}>{skill}</Tag>) },
            { title: '状态', dataIndex: 'status' },
            { title: '操作', render: () => <Button type="link">推荐到职位</Button> }
          ]}
        />
      </div>
    </>
  );
}
