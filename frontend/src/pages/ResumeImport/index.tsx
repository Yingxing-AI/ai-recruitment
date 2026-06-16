import { InboxOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Form, Input, Select, Table, Tag, Typography, Upload, message } from 'antd';
import type { UploadFile } from 'antd';
import { useMemo, useState } from 'react';
import { fetchMatches } from '../../api/ai';
import { fetchCandidates } from '../../api/candidates';
import { fetchJobs } from '../../api/jobs';
import { fetchResumes, uploadResume } from '../../api/resumes';

export default function ResumeImport() {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['resumes'], queryFn: fetchResumes });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: matches = [] } = useQuery({ queryKey: ['ai', 'matches'], queryFn: fetchMatches });
  const latestMatchByCandidate = useMemo(() => {
    const result = new Map<number, (typeof matches)[number]>();
    matches.forEach((match) => {
      if (!result.has(match.candidate_id)) {
        result.set(match.candidate_id, match);
      }
    });
    return result;
  }, [matches]);
  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      message.success('简历已导入');
      form.resetFields();
      setFileList([]);
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['ai'] });
    }
  });

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>简历导入</Typography.Title>
      </div>
      <div className="panel">
        <Form
          form={form}
          layout="vertical"
          style={{ maxWidth: 720 }}
          onFinish={(values) => {
            const file = fileList[0]?.originFileObj;
            if (!file) {
              message.warning('请先选择简历文件');
              return;
            }
            uploadMutation.mutate({
              candidate_id: values.candidate_id,
              job_id: values.job_id,
              raw_text: values.raw_text,
              file
            });
          }}
        >
          <Form.Item label="候选人" name="candidate_id" extra="可选。留空时系统会按简历中的手机号或邮箱复用候选人，找不到则自动创建。">
            <Select
              allowClear
              showSearch
              optionFilterProp="label"
              placeholder="选择已有候选人，或留空自动识别"
              options={candidates.map((candidate) => ({
                label: `${candidate.name}${candidate.current_title ? ` - ${candidate.current_title}` : ''}`,
                value: candidate.id
              }))}
            />
          </Form.Item>
          <Form.Item label="关联职位" name="job_id" extra="可选。选择后会自动生成该职位下的应聘记录。">
            <Select
              allowClear
              showSearch
              optionFilterProp="label"
              placeholder="选择目标职位"
              options={jobs.map((job) => ({
                label: `${job.title}${job.location ? ` - ${job.location}` : ''}`,
                value: job.id
              }))}
            />
          </Form.Item>
          <Form.Item label="上传简历">
            <Upload.Dragger
              name="file"
              multiple={false}
              maxCount={1}
              fileList={fileList}
              beforeUpload={() => false}
              onChange={({ fileList: nextFileList }) => setFileList(nextFileList)}
            >
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p className="ant-upload-text">拖拽 PDF / DOCX 简历到此处，或点击选择文件</p>
            </Upload.Dragger>
          </Form.Item>
          <Form.Item label="简历文本" name="raw_text">
            <Input.TextArea rows={5} placeholder="可粘贴简历原文，便于后续 AI 分析" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={uploadMutation.isPending}>开始导入</Button>
        </Form>
      </div>
      <div className="panel section-panel">
        <Typography.Title level={4}>导入记录</Typography.Title>
        <Table
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          columns={[
            { title: '文件名', dataIndex: 'file_name' },
            { title: '候选人 ID', dataIndex: 'candidate_id', width: 120 },
            { title: '姓名', width: 120, render: (_, record) => record.parsed_json?.name || '-' },
            { title: '联系方式', width: 220, render: (_, record) => record.parsed_json?.phone || record.parsed_json?.email || '-' },
            { title: '当前职位', width: 140, render: (_, record) => record.parsed_json?.current_title || '-' },
            {
              title: 'AI 匹配',
              width: 180,
              render: (_, record) => {
                const match = latestMatchByCandidate.get(record.candidate_id);
                return match ? `${match.total_score ?? '-'} / ${match.level ?? '-'}` : '-';
              }
            },
            { title: '大小', dataIndex: 'file_size', width: 120, render: (value) => value ? `${Math.ceil(value / 1024)} KB` : '-' },
            { title: '状态', dataIndex: 'parse_status', width: 120, render: (value) => <Tag>{value}</Tag> },
            { title: '存储路径', dataIndex: 'file_path' },
            { title: '导入时间', dataIndex: 'created_at', render: (value) => new Date(value).toLocaleString() }
          ]}
        />
      </div>
    </>
  );
}
