import { ArrowLeftOutlined, RobotOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Card, Col, Descriptions, Empty, Row, Space, Table, Tag, Timeline, Typography } from 'antd';
import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchAnalysesByCandidate, fetchAuditLogs, fetchMatchesByFilters } from '../../api/ai';
import { fetchApplications } from '../../api/applications';
import { fetchCandidate } from '../../api/candidates';
import { fetchInterviews } from '../../api/interviews';
import { fetchJobs } from '../../api/jobs';
import { fetchResumes } from '../../api/resumes';

export default function CandidateDetail() {
  const navigate = useNavigate();
  const params = useParams();
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

  const candidateApplications = useMemo(() => applications.filter((application) => application.candidate_id === candidateId), [applications, candidateId]);
  const candidateInterviews = useMemo(() => interviews.filter((interview) => interview.candidate_id === candidateId), [interviews, candidateId]);
  const candidateResumes = useMemo(() => resumes.filter((resume) => resume.candidate_id === candidateId), [resumes, candidateId]);
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const latestAnalysis = analyses[0];

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
            候选人详情
          </Typography.Title>
        </Space>
        <Button icon={<RobotOutlined />} type="primary" onClick={() => navigate('/ai-recruitment')}>
          去 AI 招聘
        </Button>
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
          <Card title="AI 摘要" className="section-panel">
            {latestAnalysis ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Typography.Paragraph>{latestAnalysis.summary}</Typography.Paragraph>
                <Typography.Text type="secondary">优势：{(latestAnalysis.strengths_json ?? []).map(String).join(' / ') || '-'}</Typography.Text>
                <Typography.Text type="secondary">风险：{(latestAnalysis.risks_json ?? []).map(String).join(' / ') || '-'}</Typography.Text>
              </Space>
            ) : (
              <Empty description="暂无候选人分析" />
            )}
          </Card>
        </Col>
      </Row>

      <Card title="简历与解析" className="section-panel">
        <Table
          rowKey="id"
          dataSource={candidateResumes}
          columns={[
            { title: '文件名', dataIndex: 'file_name' },
            { title: '状态', dataIndex: 'parse_status', render: (value) => <Tag>{value}</Tag> },
            { title: '姓名', render: (_, record) => record.parsed_json?.name || '-' },
            { title: '电话', render: (_, record) => record.parsed_json?.phone || '-' },
            { title: '邮箱', render: (_, record) => record.parsed_json?.email || '-' }
          ]}
        />
      </Card>

      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="岗位匹配" className="section-panel">
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
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="应聘与面试" className="section-panel">
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
