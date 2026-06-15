import { ImportOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Form, Input, InputNumber, Modal, Space, Table, Tag, Typography, message } from 'antd';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCandidate, fetchCandidates } from '../../api/candidates';

export default function Candidates() {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const createMutation = useMutation({
    mutationFn: createCandidate,
    onSuccess: () => {
      message.success('候选人已创建');
      setOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    }
  });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>候选人管理</Typography.Title>
        <Space>
          <Button icon={<ImportOutlined />} onClick={() => navigate('/resume-import')}>导入简历</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>新建候选人</Button>
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
      <Modal
        title="新建候选人"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ status: 'active' }}
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="手机" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="邮箱" name="email">
            <Input />
          </Form.Item>
          <Form.Item label="当前公司" name="current_company">
            <Input />
          </Form.Item>
          <Form.Item label="当前职位" name="current_title">
            <Input />
          </Form.Item>
          <Form.Item label="工作年限" name="years_of_experience">
            <InputNumber min={0} max={60} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="来源" name="source">
            <Input placeholder="Boss / 猎头 / 内推" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
