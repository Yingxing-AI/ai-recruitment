import { SearchOutlined } from '@ant-design/icons';
import { Button, Input, Space, Table, Tag, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const candidates = [
  { id: 1, name: '示例候选人', skills: ['Java', '微服务', '金融'], status: '可联系' }
];

export default function TalentPool() {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState('');
  const [searchText, setSearchText] = useState('');

  const filteredCandidates = useMemo(() => {
    const term = searchText.trim().toLowerCase();
    if (!term) {
      return candidates;
    }

    return candidates.filter((candidate) => {
      const haystack = [candidate.name, candidate.status, ...candidate.skills].join(' ').toLowerCase();
      return haystack.includes(term);
    });
  }, [searchText]);

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>人才库</Typography.Title>
        <Space>
          <Input
            prefix={<SearchOutlined />}
            placeholder="搜索技能、公司、职位"
            style={{ width: 280 }}
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            onPressEnter={() => setSearchText(keyword)}
          />
          <Button onClick={() => setSearchText(keyword)}>筛选</Button>
        </Space>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          dataSource={filteredCandidates}
          columns={[
            { title: '姓名', dataIndex: 'name' },
            { title: '标签', dataIndex: 'skills', render: (skills: string[]) => skills.map((skill) => <Tag key={skill}>{skill}</Tag>) },
            { title: '状态', dataIndex: 'status' },
            { title: '操作', render: () => <Button type="link" onClick={() => navigate('/jobs')}>推荐到职位</Button> }
          ]}
        />
      </div>
    </>
  );
}
