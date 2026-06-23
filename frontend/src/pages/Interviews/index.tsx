import { CalendarOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Empty, Form, Input, InputNumber, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import { useMemo, useState } from 'react';
import { fetchApplications } from '../../api/applications';
import { fetchCandidates } from '../../api/candidates';
import { createInterview, fetchInterviews } from '../../api/interviews';
import { fetchJobs } from '../../api/jobs';

const typeLabel: Record<string, string> = {
  phone: '电话',
  video: '视频',
  onsite: '现场'
};

export default function Interviews() {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['interviews'], queryFn: fetchInterviews });
  const { data: applications = [] } = useQuery({ queryKey: ['applications'], queryFn: fetchApplications });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const candidateMap = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate.name])), [candidates]);
  const applicationMap = useMemo(() => new Map(applications.map((application) => [application.id, application])), [applications]);
  const createMutation = useMutation({
    mutationFn: createInterview,
    onSuccess: () => {
      message.success('面试已安排');
      setOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    }
  });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>面试安排</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>安排面试</Button>
      </div>
      <div className="panel">
        {data.length === 0 && !isLoading ? (
          <Empty image={<CalendarOutlined style={{ fontSize: 48 }} />} description="暂无面试安排">
            <Space>
              <Button type="primary" onClick={() => setOpen(true)}>新建安排</Button>
            </Space>
          </Empty>
        ) : (
          <Table
            rowKey="id"
            loading={isLoading}
            dataSource={data}
            columns={[
              { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
              { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
              { title: '轮次', dataIndex: 'round', width: 90, render: (value) => `第 ${value} 轮` },
              { title: '类型', dataIndex: 'interview_type', width: 100, render: (value) => typeLabel[value] ?? value },
              { title: '开始时间', dataIndex: 'scheduled_start_at', render: (value) => value ? new Date(value).toLocaleString() : '-' },
              { title: '地点/链接', render: (_, record) => record.meeting_link || record.location || '-' },
              { title: '状态', dataIndex: 'status', width: 110, render: (value) => <Tag>{value}</Tag> }
            ]}
          />
        )}
      </div>
      <Modal
        title="安排面试"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ round: 1, interview_type: 'video' }}
          onFinish={(values) => {
            const application = applicationMap.get(values.application_id);
            if (!application) {
              message.warning('请选择有效的应聘记录');
              return;
            }
            createMutation.mutate({
              ...values,
              job_id: application.job_id,
              candidate_id: application.candidate_id,
              scheduled_start_at: values.scheduled_start_at ? new Date(values.scheduled_start_at).toISOString() : undefined,
              scheduled_end_at: values.scheduled_end_at ? new Date(values.scheduled_end_at).toISOString() : undefined
            });
          }}
        >
          <Form.Item label="应聘记录" name="application_id" rules={[{ required: true, message: '请选择应聘记录' }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={applications.map((application) => ({
                value: application.id,
                label: `${candidateMap.get(application.candidate_id) ?? `#${application.candidate_id}`} - ${jobMap.get(application.job_id) ?? `#${application.job_id}`}`
              }))}
            />
          </Form.Item>
          <Form.Item label="轮次" name="round">
            <InputNumber min={1} max={10} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="类型" name="interview_type">
            <Select
              options={[
                { label: '视频', value: 'video' },
                { label: '电话', value: 'phone' },
                { label: '现场', value: 'onsite' }
              ]}
            />
          </Form.Item>
          <Form.Item label="开始时间" name="scheduled_start_at">
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item label="结束时间" name="scheduled_end_at">
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item label="地点" name="location">
            <Input />
          </Form.Item>
          <Form.Item label="会议链接" name="meeting_link">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
