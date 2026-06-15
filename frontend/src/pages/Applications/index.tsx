import { Card, Col, Row, Tag, Typography } from 'antd';

const stages = ['初筛', '待沟通', '一面', '二面', '终面', 'Offer', '已入职'];

export default function Applications() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>招聘流程</Typography.Title>
      </div>
      <Row gutter={12}>
        {stages.map((stage, index) => (
          <Col flex="1" key={stage}>
            <Card size="small" title={stage}>
              <Tag color={index < 3 ? 'blue' : 'green'}>{Math.max(1, 9 - index)} 人</Tag>
            </Card>
          </Col>
        ))}
      </Row>
    </>
  );
}
