import { Card, Descriptions, Typography } from 'antd';

export default function Settings() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>系统设置</Typography.Title>
      </div>
      <Card title="AI 模型配置">
        <Descriptions column={1}>
          <Descriptions.Item label="Provider">mock</Descriptions.Item>
          <Descriptions.Item label="模型">mock-recruitment</Descriptions.Item>
          <Descriptions.Item label="接入方式">后端统一 LLM Provider，可接入通义千问、DeepSeek、智谱等</Descriptions.Item>
        </Descriptions>
      </Card>
    </>
  );
}
