import { Card, Col, Descriptions, Row, Typography } from 'antd';

export default function Settings() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>系统设置</Typography.Title>
      </div>
      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="AI 模型配置" className="section-panel">
            <Descriptions column={1}>
              <Descriptions.Item label="Provider">mock</Descriptions.Item>
              <Descriptions.Item label="模型">mock-recruitment</Descriptions.Item>
              <Descriptions.Item label="接入方式">后端统一 LLM Provider，可接入通义千问、DeepSeek、智谱等</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="发布与安全" className="section-panel">
            <Descriptions column={1}>
              <Descriptions.Item label="发布流程">先验证，再更新 CHANGELOG，最后打版本 tag</Descriptions.Item>
              <Descriptions.Item label="生产基线">强 SECRET_KEY、非 SQLite、非通配 CORS、替换 MinIO 凭据</Descriptions.Item>
              <Descriptions.Item label="运维入口">见 docs/RELEASE.md 和 docs/PRODUCTION_SECURITY.md</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="数据留存" className="section-panel">
            <Descriptions column={1}>
              <Descriptions.Item label="审计日志">保留 180 天</Descriptions.Item>
              <Descriptions.Item label="AI 中间响应">保留 90 天后清空</Descriptions.Item>
              <Descriptions.Item label="执行脚本">后端 retention_cleanup 可做 dry run</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </>
  );
}
