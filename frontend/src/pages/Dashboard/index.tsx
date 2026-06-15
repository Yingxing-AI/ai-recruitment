import { Card, Col, Progress, Row, Table, Typography } from 'antd';

const pipeline = [
  { stage: '初筛', count: 18 },
  { stage: '一面', count: 9 },
  { stage: '二面', count: 5 },
  { stage: 'Offer', count: 2 }
];

export default function Dashboard() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>招聘概览</Typography.Title>
      </div>
      <div className="metric-grid">
        <Card><Typography.Text type="secondary">开放职位</Typography.Text><Typography.Title level={2}>12</Typography.Title></Card>
        <Card><Typography.Text type="secondary">候选人</Typography.Text><Typography.Title level={2}>286</Typography.Title></Card>
        <Card><Typography.Text type="secondary">待面试</Typography.Text><Typography.Title level={2}>14</Typography.Title></Card>
        <Card><Typography.Text type="secondary">AI 已分析</Typography.Text><Typography.Title level={2}>73%</Typography.Title></Card>
      </div>
      <Row gutter={16}>
        <Col span={14}>
          <div className="panel">
            <Typography.Title level={5}>招聘漏斗</Typography.Title>
            <Table
              rowKey="stage"
              pagination={false}
              dataSource={pipeline}
              columns={[
                { title: '阶段', dataIndex: 'stage' },
                { title: '候选人数', dataIndex: 'count' },
                { title: '占比', render: (_, item) => <Progress percent={Math.min(item.count * 5, 100)} size="small" /> }
              ]}
            />
          </div>
        </Col>
        <Col span={10}>
          <div className="panel">
            <Typography.Title level={5}>AI 能力状态</Typography.Title>
            <Typography.Paragraph>简历摘要、技能提取、人岗匹配评分和面试问题生成已预留后端接口层。</Typography.Paragraph>
            <Typography.Text type="secondary">当前 Provider：mock，可切换国内大模型 API。</Typography.Text>
          </div>
        </Col>
      </Row>
    </>
  );
}
