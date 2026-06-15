import { Button, Card, Form, Input, Typography } from 'antd';

export default function Login() {
  return (
    <div className="login-page">
      <Card title="AI 招聘管理系统">
        <Form layout="vertical">
          <Form.Item label="邮箱"><Input /></Form.Item>
          <Form.Item label="密码"><Input.Password /></Form.Item>
          <Button type="primary" block>登录</Button>
        </Form>
        <Typography.Text type="secondary">MVP 阶段登录接口已预留。</Typography.Text>
      </Card>
    </div>
  );
}
