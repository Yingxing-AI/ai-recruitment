import { ArrowLeftOutlined, ExperimentOutlined, TrophyOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Col, Descriptions, Empty, List, Row, Select, Space, Table, Tag, Timeline, Typography, message } from 'antd';
import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchAnalysesByCandidate, fetchAuditLogs, fetchMatchesByFilters, generateInterviewQuestions, matchCandidate } from '../../api/ai';
import { fetchApplications } from '../../api/applications';
import { fetchCandidates } from '../../api/candidates';
import { fetchInterviews } from '../../api/interviews';
import { fetchJob } from '../../api/jobs';

const statusLabel: Record<string, string> = {
  open: '开放',
  draft: '草稿',
  paused: '暂停',
  closed: '关闭'
};

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

export default function JobDetail() {
  const navigate = useNavigate();
  const params = useParams();
  const queryClient = useQueryClient();
  const [selectedCandidateId, setSelectedCandidateId] = useState<number>();
  const jobId = Number(params.jobId);
  const { data: job, isLoading: jobLoading } = useQuery({ queryKey: ['job', jobId], queryFn: () => fetchJob(jobId), enabled: Number.isFinite(jobId) });
  const { data: matches = [] } = useQuery({
    queryKey: ['ai', 'matches', jobId],
    queryFn: () => fetchMatchesByFilters({ jobId }),
    enabled: Number.isFinite(jobId)
  });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const { data: applications = [] } = useQuery({ queryKey: ['applications'], queryFn: fetchApplications });
  const { data: interviews = [] } = useQuery({ queryKey: ['interviews'], queryFn: fetchInterviews });
  const { data: auditLogs = [] } = useQuery({
    queryKey: ['audit-logs', 'job', jobId],
    queryFn: () => fetchAuditLogs({ targetType: 'job', targetId: jobId, limit: 20 }),
    enabled: Number.isFinite(jobId)
  });
  const { data: selectedCandidateAnalyses = [] } = useQuery({
    queryKey: ['ai', 'analyses', 'job-detail-candidate', selectedCandidateId],
    queryFn: () => fetchAnalysesByCandidate(selectedCandidateId!),
    enabled: Number.isFinite(selectedCandidateId)
  });

  const refreshJobWorkspace = () => {
    queryClient.invalidateQueries({ queryKey: ['ai'] });
    queryClient.invalidateQueries({ queryKey: ['applications'] });
    queryClient.invalidateQueries({ queryKey: ['interviews'] });
  };
  const matchMutation = useMutation({
    mutationFn: matchCandidate,
    onSuccess: () => {
      message.success('匹配评分已生成');
      refreshJobWorkspace();
    }
  });
  const questionMutation = useMutation({
    mutationFn: generateInterviewQuestions,
    onSuccess: () => {
      message.success('面试问题已生成');
      refreshJobWorkspace();
    }
  });

  const jobApplications = useMemo(() => applications.filter((application) => application.job_id === jobId), [applications, jobId]);
  const jobInterviews = useMemo(() => interviews.filter((interview) => interview.job_id === jobId), [interviews, jobId]);
  const candidateMap = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate.name])), [candidates]);
  const candidateOptions = jobApplications.map((application) => ({
    value: application.candidate_id,
    label: candidateMap.get(application.candidate_id) ?? `#${application.candidate_id}`
  }));
  const selectedMatch = matches.find((match) => match.candidate_id === selectedCandidateId) ?? matches[0];
  const latestCandidateAnalysis = selectedCandidateAnalyses[0];

  if (!Number.isFinite(jobId)) {
    return <Empty description="无效的职位编号" />;
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div className="page-header">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/jobs')}>
            返回职位列表
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            职位工作台
          </Typography.Title>
        </Space>
        <Button onClick={() => navigate('/applications')}>查看招聘流程</Button>
      </div>

      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card title="职位信息" className="section-panel" loading={jobLoading}>
            {job ? (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="职位">{job.title}</Descriptions.Item>
                <Descriptions.Item label="地点">{job.location || '-'}</Descriptions.Item>
                <Descriptions.Item label="人数">{job.headcount}</Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag>{statusLabel[job.status] ?? job.status}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="职位描述">{job.jd_text}</Descriptions.Item>
                <Descriptions.Item label="任职要求">{job.requirements_text || '-'}</Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty description="未找到职位" />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="流程概览" className="section-panel">
            <Space wrap>
              <Tag color="blue">候选人 {jobApplications.length}</Tag>
              <Tag color="gold">匹配评分 {matches.length}</Tag>
              <Tag color="green">面试 {jobInterviews.length}</Tag>
            </Space>
            <div style={{ marginTop: 16 }}>
              <Typography.Text type="secondary">
                推荐路径：先选择候选人生成匹配评分，再生成面试问题并推进到面试安排。
              </Typography.Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} lg={11}>
          <Card title="候选人匹配工作台" className="section-panel">
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <Select
                showSearch
                optionFilterProp="label"
                placeholder="选择当前职位下的候选人"
                value={selectedCandidateId}
                onChange={setSelectedCandidateId}
                options={candidateOptions}
              />
              <Space wrap>
                <Button
                  type="primary"
                  icon={<TrophyOutlined />}
                  disabled={!selectedCandidateId}
                  loading={matchMutation.isPending}
                  onClick={() => selectedCandidateId && matchMutation.mutate({ jobId, candidateId: selectedCandidateId })}
                >
                  生成匹配评分
                </Button>
                <Button
                  icon={<ExperimentOutlined />}
                  disabled={!selectedCandidateId}
                  loading={questionMutation.isPending}
                  onClick={() => selectedCandidateId && questionMutation.mutate({ jobId, candidateId: selectedCandidateId })}
                >
                  生成面试问题
                </Button>
                <Button disabled={!selectedCandidateId} onClick={() => selectedCandidateId && navigate(`/candidates/${selectedCandidateId}`)}>
                  查看候选人详情
                </Button>
              </Space>
              {selectedMatch ? (
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="候选人">{candidateMap.get(selectedMatch.candidate_id) ?? `#${selectedMatch.candidate_id}`}</Descriptions.Item>
                  <Descriptions.Item label="推荐结论">{selectedMatch.recommendation || '-'}</Descriptions.Item>
                  <Descriptions.Item label="匹配亮点">{renderList(selectedMatch.matched_points_json)}</Descriptions.Item>
                  <Descriptions.Item label="缺失项">{renderList(selectedMatch.missing_points_json)}</Descriptions.Item>
                  <Descriptions.Item label="风险点">{renderList(selectedMatch.risk_points_json)}</Descriptions.Item>
                </Descriptions>
              ) : (
                <Empty description="暂无匹配结果，请先选择候选人生成评分" />
              )}
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={13}>
          <Card title="候选人 AI 辅助信息" className="section-panel">
            {latestCandidateAnalysis ? (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="候选人">{candidateMap.get(latestCandidateAnalysis.candidate_id) ?? `#${latestCandidateAnalysis.candidate_id}`}</Descriptions.Item>
                <Descriptions.Item label="候选人总结">{latestCandidateAnalysis.summary || '-'}</Descriptions.Item>
                <Descriptions.Item label="优势">{renderList(latestCandidateAnalysis.strengths_json)}</Descriptions.Item>
                <Descriptions.Item label="风险">{renderList(latestCandidateAnalysis.risks_json)}</Descriptions.Item>
                <Descriptions.Item label="面试问题">
                  {latestCandidateAnalysis.interview_questions_json?.length ? (
                    <List
                      size="small"
                      dataSource={latestCandidateAnalysis.interview_questions_json}
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
                    <Typography.Text type="secondary">暂无面试问题，请先生成。</Typography.Text>
                  )}
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <Empty description="请选择候选人查看 AI 总结和面试问题" />
            )}
          </Card>
        </Col>
      </Row>

      <Card title="关联候选人和匹配结果" className="section-panel">
        <Table
          rowKey="id"
          dataSource={matches}
          columns={[
            { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
            { title: '分数', dataIndex: 'total_score' },
            { title: '等级', dataIndex: 'level', render: (value) => <Tag>{value || '-'}</Tag> },
            { title: '推荐', dataIndex: 'recommendation' },
            { title: '说明', dataIndex: 'explanation' }
          ]}
          pagination={false}
        />
      </Card>

      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="应聘记录" className="section-panel">
            <Table
              rowKey="id"
              dataSource={jobApplications}
              pagination={false}
              columns={[
                { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
                { title: '阶段', dataIndex: 'current_stage', render: (value) => <Tag>{value}</Tag> },
                { title: '状态', dataIndex: 'status' }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="面试安排" className="section-panel">
            <Table
              rowKey="id"
              dataSource={jobInterviews}
              pagination={false}
              columns={[
                { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
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
