import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Col, Form, Modal, Row, Select, Space, Table, Tag, Typography, message } from 'antd';
import { useMemo, useState } from 'react';
import { createApplication, fetchApplications, updateApplicationStage } from '../../api/applications';
import { fetchCandidates } from '../../api/candidates';
import { fetchJobs } from '../../api/jobs';
import type { Application } from '../../types/application';

const stages = [
  { label: '初筛', value: 'screening' },
  { label: '待沟通', value: 'contacting' },
  { label: '一面', value: 'first_interview' },
  { label: '二面', value: 'second_interview' },
  { label: '终面', value: 'final_interview' },
  { label: 'Offer', value: 'offer' },
  { label: '已入职', value: 'hired' }
];

const stageLabel = Object.fromEntries(stages.map((stage) => [stage.value, stage.label]));

export default function Applications() {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['applications'], queryFn: fetchApplications });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const candidateMap = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate.name])), [candidates]);
  const createMutation = useMutation({
    mutationFn: createApplication,
    onSuccess: () => {
      message.success('应聘记录已创建');
      setOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    }
  });
  const stageMutation = useMutation({
    mutationFn: ({ id, to_stage }: { id: number; to_stage: string }) => updateApplicationStage(id, { to_stage }),
    onSuccess: () => {
      message.success('阶段已更新');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    }
  });

  const byStage = useMemo(() => {
    return data.reduce<Record<string, Application[]>>((acc, application) => {
      acc[application.current_stage] = [...(acc[application.current_stage] ?? []), application];
      return acc;
    }, {});
  }, [data]);

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>招聘流程</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>新增应聘</Button>
      </div>
      <Row gutter={12}>
        {stages.map((stage, index) => (
          <Col flex="1" key={stage.value}>
            <Card size="small" title={stage.label}>
              <Tag color={index < 3 ? 'blue' : 'green'}>{byStage[stage.value]?.length ?? 0} 人</Tag>
            </Card>
          </Col>
        ))}
      </Row>
      <div className="panel section-panel">
        <Table
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          columns={[
            { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
            { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
            { title: '阶段', dataIndex: 'current_stage', render: (value) => <Tag>{stageLabel[value] ?? value}</Tag> },
            { title: '状态', dataIndex: 'status' },
            { title: '来源', dataIndex: 'source', render: (value) => value ?? '-' },
            { title: '应聘时间', dataIndex: 'applied_at', render: (value) => new Date(value).toLocaleString() },
            {
              title: '流转',
              width: 180,
              render: (_, record) => (
                <Select
                  size="small"
                  value={record.current_stage}
                  options={stages}
                  style={{ width: 150 }}
                  onChange={(to_stage) => stageMutation.mutate({ id: record.id, to_stage })}
                />
              )
            }
          ]}
        />
      </div>
      <Modal
        title="新增应聘"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item label="职位" name="job_id" rules={[{ required: true, message: '请选择职位' }]}>
            <Select showSearch optionFilterProp="label" options={jobs.map((job) => ({ label: job.title, value: job.id }))} />
          </Form.Item>
          <Form.Item label="候选人" name="candidate_id" rules={[{ required: true, message: '请选择候选人' }]}>
            <Select showSearch optionFilterProp="label" options={candidates.map((candidate) => ({ label: candidate.name, value: candidate.id }))} />
          </Form.Item>
          <Form.Item label="来源" name="source">
            <Select
              allowClear
              options={[
                { label: '内推', value: 'referral' },
                { label: '招聘网站', value: 'job_board' },
                { label: '猎头', value: 'headhunter' },
                { label: '主动投递', value: 'inbound' }
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
