import { ArrowLeftOutlined, ExperimentOutlined, InboxOutlined, TrophyOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Form,
  Input,
  List,
  Row,
  Select,
  Space,
  Table,
  Tag,
  Timeline,
  Typography,
  Upload,
  message
} from 'antd';
import type { UploadFile } from 'antd';
import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  fetchAnalysesByCandidate,
  fetchAuditLogs,
  fetchMatchesByFilters,
  generateInterviewQuestions,
  matchCandidate,
  parseResume,
  summarizeResume
} from '../../api/ai';
import { fetchApplications } from '../../api/applications';
import { fetchCandidate } from '../../api/candidates';
import { fetchInterviews } from '../../api/interviews';
import { fetchJobs } from '../../api/jobs';
import { fetchResumes, uploadResume } from '../../api/resumes';

function renderList(items?: unknown[]) {
  if (!items?.length) {
    return <Typography.Text type="secondary">暂无</Typography.Text>;
  }

  return (
    <List
      size="small"
      dataSource={items.map(String)}
      renderItem={(item) => <List.Item>{item}</List.Item>}
    />
  );
}

export default function CandidateDetail() {
  const navigate = useNavigate();
  const params = useParams();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [selectedJobId, setSelectedJobId] = useState<number>();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const candidateId = Number(params.candidateId);
  const { data: candidate, isLoading: candidateLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => fetchCandidate(candidateId),
    enabled: Number.isFinite(candidateId)
  });
  const { data: analyses = [] } = useQuery({
    queryKey: ['ai', 'analyses', candidateId],
    queryFn: () => fetchAnalysesByCandidate(candidateId),
    enabled: Number.isFinite(candidateId)
  });
  const { data: matches = [] } = useQuery({
    queryKey: ['ai', 'matches', candidateId],
    queryFn: () => fetchMatchesByFilters({ candidateId }),
    enabled: Number.isFinite(candidateId)
  });
  const { data: applications = [] } = useQuery({ queryKey: ['applications'], queryFn: fetchApplications });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: interviews = [] } = useQuery({ queryKey: ['interviews'], queryFn: fetchInterviews });
  const { data: resumes = [] } = useQuery({ queryKey: ['resumes'], queryFn: fetchResumes });
  const { data: auditLogs = [] } = useQuery({
    queryKey: ['audit-logs', 'candidate', candidateId],
    queryFn: () => fetchAuditLogs({ targetType: 'candidate', targetId: candidateId, limit: 20 }),
    enabled: Number.isFinite(candidateId)
  });

  const refreshCandidateWorkspace = () => {
    queryClient.invalidateQueries({ queryKey: ['resumes'] });
    queryClient.invalidateQueries({ queryKey: ['applications'] });
    queryClient.invalidateQueries({ queryKey: ['interviews'] });
    queryClient.invalidateQueries({ queryKey: ['jobs'] });
    queryClient.invalidateQueries({ queryKey: ['candidates'] });
    queryClient.invalidateQueries({ queryKey: ['ai'] });
  };

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      message.success('简历已上传到候选人档案');
      form.resetFields();
      setFileList([]);
      refreshCandidateWorkspace();
    }
  });
  const parseMutation = useMutation({
    mutationFn: parseResume,
    onSuccess: () => {
      message.success('简历解析完成');
      refreshCandidateWorkspace();
    }
  });
  const summaryMutation = useMutation({
    mutationFn: summarizeResume,
    onSuccess: () => {
      message.success('候选人总结已生成');
      refreshCandidateWorkspace();
    }
  });
  const matchMutation = useMutation({
    mutationFn: matchCandidate,
    onSuccess: () => {
      message.success('岗位匹配评分已生成');
      refreshCandidateWorkspace();
    }
  });
  const questionMutation = useMutation({
    mutationFn: generateInterviewQuestions,
    onSuccess: () => {
      message.success('面试问题已生成');
      refreshCandidateWorkspace();
    }
  });

  const candidateApplications = useMemo(() => applications.filter((application) => application.candidate_id === candidateId), [applications, candidateId]);
  const candidateInterviews = useMemo(() => interviews.filter((interview) => interview.candidate_id === candidateId), [interviews, candidateId]);
  const candidateResumes = useMemo(() => resumes.filter((resume) => resume.candidate_id === candidateId), [resumes, candidateId]);
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const latestAnalysis = analyses[0];
  const jobOptions = candidateApplications.map((application) => ({
    value: application.job_id,
    label: jobMap.get(application.job_id) ?? `#${application.job_id}`
  }));
  const selectedMatch = matches.find((match) => match.job_id === selectedJobId) ?? matches[0];

  if (!Number.isFinite(candidateId)) {
    return <Empty description="无效的候选人编号" />;
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div className="page-header">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/candidates')}>
            返回候选人列表
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            候选人工作台
          </Typography.Title>
        </Space>
        <Button onClick={() => navigate('/applications')}>查看招聘流程</Button>
      </div>

      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card title="候选人信息" className="section-panel" loading={candidateLoading}>
            {candidate ? (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="姓名">{candidate.name}</Descriptions.Item>
                <Descriptions.Item label="当前公司">{candidate.current_company || '-'}</Descriptions.Item>
                <Descriptions.Item label="当前职位">{candidate.current_title || '-'}</Descriptions.Item>
                <Descriptions.Item label="经验">{candidate.years_of_experience ? `${candidate.years_of_experience} 年` : '-'}</Descriptions.Item>
                <Descriptions.Item label="邮箱">{candidate.email || '-'}</Descriptions.Item>
                <Descriptions.Item label="电话">{candidate.phone || '-'}</Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag>{candidate.status}</Tag>
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty description="未找到候选人" />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="当前招聘进度" className="section-panel">
            <Space wrap>
              <Tag color="blue">简历 {candidateResumes.length}</Tag>
              <Tag color="gold">匹配 {matches.length}</Tag>
              <Tag color="green">面试 {candidateInterviews.length}</Tag>
            </Space>
            <div style={{ marginTop: 16 }}>
              <Typography.Text type="secondary">
                推荐路径：上传简历后先完成解析与总结，再针对目标职位生成匹配评分和面试问题。
              </Typography.Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} lg={11}>
          <Card title="简历上传" className="section-panel">
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => {
                const file = fileList[0]?.originFileObj;
                if (!file) {
                  message.warning('请先选择简历文件');
                  return;
                }
                uploadMutation.mutate({
                  candidate_id: candidateId,
                  job_id: values.job_id,
                  raw_text: values.raw_text,
                  file
                });
              }}
            >
              <Form.Item label="关联职位" name="job_id" extra="可选。选择后会自动挂到该职位招聘流程中。">
                <Select
                  allowClear
                  showSearch
                  optionFilterProp="label"
                  placeholder="选择当前推进中的职位"
                  options={jobOptions}
                />
              </Form.Item>
              <Form.Item label="上传简历">
                <Upload.Dragger
                  name="file"
                  multiple={false}
                  maxCount={1}
                  beforeUpload={() => false}
                  fileList={fileList}
                  onChange={({ fileList: nextFileList }) => setFileList(nextFileList)}
                >
                  <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                  <p className="ant-upload-text">拖拽 PDF / DOCX / TXT 简历到此处，或点击选择文件</p>
                </Upload.Dragger>
              </Form.Item>
              <Form.Item label="简历文本" name="raw_text">
                <Input.TextArea rows={4} placeholder="可选：补充或粘贴原始简历内容，便于规则版 AI 分析。" />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={uploadMutation.isPending}>
                上传到候选人档案
              </Button>
            </Form>
          </Card>
        </Col>
        <Col xs={24} lg={13}>
          <Card title="AI 分析工作台" className="section-panel">
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <Select
                allowClear
                showSearch
                optionFilterProp="label"
                placeholder="选择目标职位，为当前候选人生成匹配和面试问题"
                value={selectedJobId}
                onChange={setSelectedJobId}
                options={jobOptions}
              />
              <Space wrap>
                <Button
                  icon={<TrophyOutlined />}
                  type="primary"
                  disabled={!selectedJobId}
                  loading={matchMutation.isPending}
                  onClick={() => selectedJobId && matchMutation.mutate({ jobId: selectedJobId, candidateId })}
                >
                  生成岗位匹配
                </Button>
                <Button
                  icon={<ExperimentOutlined />}
                  disabled={!selectedJobId}
                  loading={questionMutation.isPending}
                  onClick={() => selectedJobId && questionMutation.mutate({ jobId: selectedJobId, candidateId })}
                >
                  生成面试问题
                </Button>
              </Space>
              {latestAnalysis ? (
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="最新总结">{latestAnalysis.summary || '-'}</Descriptions.Item>
                  <Descriptions.Item label="优势">{renderList(latestAnalysis.strengths_json)}</Descriptions.Item>
                  <Descriptions.Item label="风险">{renderList(latestAnalysis.risks_json)}</Descriptions.Item>
                  <Descriptions.Item label="面试问题">
                    {latestAnalysis.interview_questions_json?.length ? (
                      <List
                        size="small"
                        dataSource={latestAnalysis.interview_questions_json}
                        renderItem={(item) => (
                          <List.Item>
                            <Space direction="vertical" size={0}>
                              <Typography.Text strong>{item.question}</Typography.Text>
                              <Typography.Text type="secondary">{item.type} / {item.focus}</Typography.Text>
                            </Space>
                          </List.Item>
                        )}
                      />
                    ) : (
                      <Typography.Text type="secondary">暂无面试问题，请先选择职位并生成。</Typography.Text>
                    )}
                  </Descriptions.Item>
                </Descriptions>
              ) : (
                <Empty description="暂无候选人分析，请先解析简历并生成总结" />
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      <Card title="简历档案与解析结果" className="section-panel">
        <Table
          rowKey="id"
          dataSource={candidateResumes}
          columns={[
            { title: '文件名', dataIndex: 'file_name' },
            { title: '解析状态', dataIndex: 'parse_status', render: (value) => <Tag>{value}</Tag> },
            { title: '姓名', render: (_, record) => record.parsed_json?.name || '-' },
            { title: '技能', render: (_, record) => record.parsed_json?.skills?.join(' / ') || '-' },
            { title: '联系方式', render: (_, record) => record.parsed_json?.phone || record.parsed_json?.email || '-' },
            {
              title: '动作',
              render: (_, record) => (
                <Space wrap>
                  <Button size="small" onClick={() => parseMutation.mutate(record.id)} loading={parseMutation.isPending}>
                    解析简历
                  </Button>
                  <Button size="small" type="primary" onClick={() => summaryMutation.mutate(record.id)} loading={summaryMutation.isPending}>
                    生成总结
                  </Button>
                </Space>
              )
            }
          ]}
          pagination={false}
        />
      </Card>

      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="岗位匹配结果" className="section-panel">
            <Table
              rowKey="id"
              dataSource={matches}
              pagination={false}
              columns={[
                { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
                { title: '分数', dataIndex: 'total_score' },
                { title: '等级', dataIndex: 'level', render: (value) => <Tag>{value || '-'}</Tag> },
                { title: '推荐', dataIndex: 'recommendation' }
              ]}
            />
            {selectedMatch ? (
              <Descriptions column={1} bordered size="small" style={{ marginTop: 16 }}>
                <Descriptions.Item label="匹配亮点">{renderList(selectedMatch.matched_points_json)}</Descriptions.Item>
                <Descriptions.Item label="缺失项">{renderList(selectedMatch.missing_points_json)}</Descriptions.Item>
                <Descriptions.Item label="风险点">{renderList(selectedMatch.risk_points_json)}</Descriptions.Item>
              </Descriptions>
            ) : null}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="应聘与面试推进" className="section-panel">
            <Table
              rowKey="id"
              dataSource={candidateApplications}
              pagination={false}
              columns={[
                { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
                { title: '阶段', dataIndex: 'current_stage', render: (value) => <Tag>{value}</Tag> },
                { title: '状态', dataIndex: 'status' }
              ]}
            />
            <div style={{ height: 16 }} />
            <Table
              rowKey="id"
              dataSource={candidateInterviews}
              pagination={false}
              columns={[
                { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
                { title: '轮次', dataIndex: 'round', render: (value) => `第 ${value} 轮` },
                { title: '类型', dataIndex: 'interview_type' },
                { title: '状态', dataIndex: 'status', render: (value) => <Tag>{value}</Tag> }
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Card title="留痕日志" className="section-panel">
        {auditLogs.length ? (
          <Timeline
            items={auditLogs.map((log) => ({
              children: (
                <div>
                  <Typography.Text strong>{log.action}</Typography.Text>
                  <div>{log.detail_json ? JSON.stringify(log.detail_json) : '-'}</div>
                  <Typography.Text type="secondary">{new Date(log.created_at).toLocaleString()}</Typography.Text>
                </div>
              )
            }))}
          />
        ) : (
          <Empty description="暂无留痕" />
        )}
      </Card>
    </Space>
  );
}
