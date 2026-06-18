import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Form, Input, InputNumber, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob, fetchJobs } from '../../api/jobs';

const statusMap: Record<string, string> = {
  draft: '草稿',
  open: '开放',
  paused: '暂停',
  closed: '关闭'
};

export default function Jobs() {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const createMutation = useMutation({
    mutationFn: createJob,
    onSuccess: () => {
      message.success('职位已创建');
      setOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    }
  });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>职位管理</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>新建职位</Button>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          columns={[
            { title: '职位', dataIndex: 'title' },
            { title: '地点', dataIndex: 'location' },
            { title: '人数', dataIndex: 'headcount', width: 90 },
            { title: '状态', dataIndex: 'status', render: (status) => <Tag>{statusMap[status] ?? status}</Tag> },
            { title: '更新时间', dataIndex: 'updated_at', render: (value) => new Date(value).toLocaleString() },
            {
              title: '操作',
              render: (_, record) => (
                <Space>
                  <Button type="link" onClick={() => navigate(`/jobs/${record.id}`)}>详情</Button>
                  <Button type="link" onClick={() => navigate('/ai-recruitment')}>匹配</Button>
                </Space>
              )
            }
          ]}
        />
      </div>
      <Modal
        title="新建职位"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ headcount: 1, status: 'open' }}
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item label="职位名称" name="title" rules={[{ required: true, message: '请输入职位名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="地点" name="location">
            <Input />
          </Form.Item>
          <Form.Item label="人数" name="headcount">
            <InputNumber min={1} max={999} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="状态" name="status">
            <Select
              options={[
                { label: '开放', value: 'open' },
                { label: '草稿', value: 'draft' },
                { label: '暂停', value: 'paused' },
                { label: '关闭', value: 'closed' }
              ]}
            />
          </Form.Item>
          <Form.Item label="职位描述" name="jd_text" rules={[{ required: true, message: '请输入职位描述' }]}>
            <Input.TextArea rows={5} />
          </Form.Item>
          <Form.Item label="任职要求" name="requirements_text">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
