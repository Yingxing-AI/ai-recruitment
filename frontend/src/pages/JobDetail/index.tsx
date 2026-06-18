import { ArrowLeftOutlined, RobotOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Card, Col, Descriptions, Empty, Row, Space, Table, Tag, Timeline, Typography } from 'antd';
import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchAuditLogs, fetchMatchesByFilters } from '../../api/ai';
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

export default function JobDetail() {
  const navigate = useNavigate();
  const params = useParams();
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

  const jobApplications = useMemo(() => applications.filter((application) => application.job_id === jobId), [applications, jobId]);
  const jobInterviews = useMemo(() => interviews.filter((interview) => interview.job_id === jobId), [interviews, jobId]);
  const candidateMap = useMemo(
    () => new Map(candidates.map((candidate) => [candidate.id, candidate.name])),
    [candidates]
  );

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
            职位详情
          </Typography.Title>
        </Space>
        <Button icon={<RobotOutlined />} type="primary" onClick={() => navigate('/ai-recruitment')}>
          去 AI 招聘
        </Button>
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
              <Tag color="blue">应聘 {jobApplications.length}</Tag>
              <Tag color="green">面试 {jobInterviews.length}</Tag>
              <Tag color="gold">匹配评分 {matches.length}</Tag>
            </Space>
            <div style={{ marginTop: 16 }}>
              <Typography.Text type="secondary">建议动作：先看最新匹配，再安排面试。</Typography.Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Card title="岗位匹配" className="section-panel">
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
