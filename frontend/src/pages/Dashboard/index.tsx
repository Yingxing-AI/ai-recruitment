import { BarChartOutlined, CheckCircleOutlined, FileSearchOutlined, TeamOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Alert, Card, Col, Progress, Row, Space, Table, Tag, Typography } from 'antd';
import { fetchDashboardSummary } from '../../api/dashboard';

const metricMeta = [
  { key: 'job_count', label: '职位数量', icon: <BarChartOutlined /> },
  { key: 'candidate_count', label: '候选人数', icon: <TeamOutlined /> },
  { key: 'resume_count', label: '简历数量', icon: <FileSearchOutlined /> },
  { key: 'interviewing_count', label: '面试中人数', icon: <TeamOutlined /> },
  { key: 'offer_count', label: 'Offer人数', icon: <CheckCircleOutlined /> },
  { key: 'hired_count', label: '录用人数', icon: <CheckCircleOutlined /> }
] as const;

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: fetchDashboardSummary
  });

  const metricValues: Record<string, number> | undefined = data
    ? {
        job_count: data.job_count,
        candidate_count: data.candidate_count,
        resume_count: data.resume_count,
        interviewing_count: data.interviewing_count,
        offer_count: data.offer_count,
        hired_count: data.hired_count
      }
    : undefined;
  const totalCandidates = Math.max(data?.candidate_count ?? 0, 1);

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div className="page-header">
        <Space direction="vertical" size={4}>
          <Typography.Title level={3} style={{ margin: 0 }}>
            招聘管理仪表盘
          </Typography.Title>
          <Typography.Text type="secondary">聚焦招聘闭环、漏斗进展和规则版 AI 产出状态</Typography.Text>
        </Space>
        <Tag color="blue">Phase 4 · V1 产品化</Tag>
      </div>

      <Row gutter={[16, 16]}>
        {metricMeta.map((metric) => (
          <Col xs={12} lg={4} key={metric.key}>
            <Card loading={isLoading} className="metric-card">
              <Space direction="vertical" size={8}>
                <Space size={8} align="center">
                  <span className="metric-icon">{metric.icon}</span>
                  <Typography.Text type="secondary">{metric.label}</Typography.Text>
                </Space>
                <Typography.Title level={2} style={{ margin: 0 }}>
                  {metricValues?.[metric.key] ?? '-'}
                </Typography.Title>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16}>
        <Col xs={24} lg={15}>
          <Card title="招聘漏斗" loading={isLoading} className="section-panel">
            <Table
              rowKey="stage"
              pagination={false}
              dataSource={data?.funnel ?? []}
              columns={[
                { title: '阶段', dataIndex: 'label' },
                { title: '人数', dataIndex: 'count' },
                {
                  title: '占比',
                  render: (_, item: { count: number }) => (
                    <Progress percent={Math.min(Math.round((item.count / totalCandidates) * 100), 100)} size="small" />
                  )
                }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={9}>
          <Card title="产品化说明" loading={isLoading} className="section-panel">
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Alert
                type="info"
                showIcon
                message="当前 AI 为规则版"
                description="简历解析、候选人总结、岗位匹配和面试题生成都通过本地规则实现，不接付费 AI API。"
              />
              <Typography.Paragraph style={{ marginBottom: 0 }}>
                后续如果需要接真实 LLM Provider，可以保持当前业务接口不变，只替换后端 Provider 实现。
              </Typography.Paragraph>
              <Typography.Paragraph style={{ marginBottom: 0 }}>
                演示数据已包含示例职位、候选人、简历和 AI 分析结果，适合本地联调与现场演示。
              </Typography.Paragraph>
            </Space>
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
