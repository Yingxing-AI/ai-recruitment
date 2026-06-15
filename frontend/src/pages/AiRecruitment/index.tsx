import { ExperimentOutlined, FileSearchOutlined, QuestionCircleOutlined, TrophyOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Col, Descriptions, Form, List, Row, Select, Space, Table, Tabs, Tag, Typography, message } from 'antd';
import { useMemo, useState } from 'react';
import {
  fetchAnalyses,
  fetchMatches,
  generateInterviewQuestions,
  matchCandidate,
  parseResume,
  summarizeResume
} from '../../api/ai';
import { fetchCandidates } from '../../api/candidates';
import { fetchJobs } from '../../api/jobs';
import { fetchResumes } from '../../api/resumes';

const questionTypeLabel: Record<string, string> = {
  technical: '技术',
  project: '项目',
  behavior: '行为'
};

export default function AiRecruitment() {
  const queryClient = useQueryClient();
  const [selectedResumeId, setSelectedResumeId] = useState<number>();
  const [selectedJobId, setSelectedJobId] = useState<number>();
  const [selectedCandidateId, setSelectedCandidateId] = useState<number>();
  const { data: resumes = [] } = useQuery({ queryKey: ['resumes'], queryFn: fetchResumes });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: analyses = [] } = useQuery({ queryKey: ['ai', 'analyses'], queryFn: fetchAnalyses });
  const { data: matches = [] } = useQuery({ queryKey: ['ai', 'matches'], queryFn: fetchMatches });
  const candidateMap = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate.name])), [candidates]);
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const latestAnalysis = analyses[0];
  const latestMatch = matches[0];

  const refreshAi = () => {
    queryClient.invalidateQueries({ queryKey: ['ai'] });
    queryClient.invalidateQueries({ queryKey: ['resumes'] });
  };
  const parseMutation = useMutation({
    mutationFn: parseResume,
    onSuccess: () => {
      message.success('简历解析完成');
      refreshAi();
    }
  });
  const summaryMutation = useMutation({
    mutationFn: summarizeResume,
    onSuccess: () => {
      message.success('候选人总结已生成');
      refreshAi();
    }
  });
  const matchMutation = useMutation({
    mutationFn: matchCandidate,
    onSuccess: () => {
      message.success('匹配评分已生成');
      refreshAi();
    }
  });
  const questionMutation = useMutation({
    mutationFn: generateInterviewQuestions,
    onSuccess: () => {
      message.success('面试问题已生成');
      refreshAi();
    }
  });

  const resumeOptions = resumes.map((resume) => ({
    value: resume.id,
    label: `${candidateMap.get(resume.candidate_id) ?? `#${resume.candidate_id}`} - ${resume.file_name}`
  }));
  const candidateOptions = candidates.map((candidate) => ({
    value: candidate.id,
    label: `${candidate.name}${candidate.current_title ? ` - ${candidate.current_title}` : ''}`
  }));
  const jobOptions = jobs.map((job) => ({ value: job.id, label: job.title }));

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>AI 招聘</Typography.Title>
        <Tag color="blue">规则版</Tag>
      </div>
      <Tabs
        items={[
          {
            key: 'resume',
            label: '简历解析与总结',
            children: (
              <Row gutter={16}>
                <Col xs={24} lg={10}>
                  <div className="panel">
                    <Typography.Title level={4}>选择简历</Typography.Title>
                    <Form layout="vertical">
                      <Form.Item label="简历">
                        <Select
                          showSearch
                          optionFilterProp="label"
                          options={resumeOptions}
                          value={selectedResumeId}
                          onChange={setSelectedResumeId}
                          placeholder="选择已上传简历"
                        />
                      </Form.Item>
                    </Form>
                    <Space>
                      <Button
                        icon={<FileSearchOutlined />}
                        onClick={() => selectedResumeId && parseMutation.mutate(selectedResumeId)}
                        loading={parseMutation.isPending}
                        disabled={!selectedResumeId}
                      >
                        解析简历
                      </Button>
                      <Button
                        type="primary"
                        icon={<ExperimentOutlined />}
                        onClick={() => selectedResumeId && summaryMutation.mutate(selectedResumeId)}
                        loading={summaryMutation.isPending}
                        disabled={!selectedResumeId}
                      >
                        生成总结
                      </Button>
                    </Space>
                  </div>
                </Col>
                <Col xs={24} lg={14}>
                  <div className="panel">
                    <Typography.Title level={4}>最新候选人总结</Typography.Title>
                    {latestAnalysis ? (
                      <Descriptions column={1} bordered size="small">
                        <Descriptions.Item label="候选人">{candidateMap.get(latestAnalysis.candidate_id) ?? `#${latestAnalysis.candidate_id}`}</Descriptions.Item>
                        <Descriptions.Item label="摘要">{latestAnalysis.summary}</Descriptions.Item>
                        <Descriptions.Item label="技能">{renderTags(latestAnalysis.skills_json)}</Descriptions.Item>
                        <Descriptions.Item label="优势">{renderList(latestAnalysis.strengths_json)}</Descriptions.Item>
                        <Descriptions.Item label="不足">{renderList(latestAnalysis.risks_json)}</Descriptions.Item>
                      </Descriptions>
                    ) : (
                      <Typography.Text type="secondary">暂无分析结果</Typography.Text>
                    )}
                  </div>
                </Col>
              </Row>
            )
          },
          {
            key: 'match',
            label: '岗位匹配评分',
            children: (
              <Row gutter={16}>
                <Col xs={24} lg={10}>
                  <div className="panel">
                    <Typography.Title level={4}>选择职位与候选人</Typography.Title>
                    <Form layout="vertical">
                      <Form.Item label="职位">
                        <Select showSearch optionFilterProp="label" options={jobOptions} value={selectedJobId} onChange={setSelectedJobId} />
                      </Form.Item>
                      <Form.Item label="候选人">
                        <Select showSearch optionFilterProp="label" options={candidateOptions} value={selectedCandidateId} onChange={setSelectedCandidateId} />
                      </Form.Item>
                    </Form>
                    <Space>
                      <Button
                        type="primary"
                        icon={<TrophyOutlined />}
                        loading={matchMutation.isPending}
                        disabled={!selectedJobId || !selectedCandidateId}
                        onClick={() => selectedJobId && selectedCandidateId && matchMutation.mutate({ jobId: selectedJobId, candidateId: selectedCandidateId })}
                      >
                        生成评分
                      </Button>
                      <Button
                        icon={<QuestionCircleOutlined />}
                        loading={questionMutation.isPending}
                        disabled={!selectedJobId || !selectedCandidateId}
                        onClick={() => selectedJobId && selectedCandidateId && questionMutation.mutate({ jobId: selectedJobId, candidateId: selectedCandidateId })}
                      >
                        生成面试题
                      </Button>
                    </Space>
                  </div>
                </Col>
                <Col xs={24} lg={14}>
                  <div className="panel">
                    <Typography.Title level={4}>最新匹配结果</Typography.Title>
                    {latestMatch ? (
                      <Card size="small">
                        <Descriptions column={1} bordered size="small">
                          <Descriptions.Item label="职位">{jobMap.get(latestMatch.job_id) ?? `#${latestMatch.job_id}`}</Descriptions.Item>
                          <Descriptions.Item label="候选人">{candidateMap.get(latestMatch.candidate_id) ?? `#${latestMatch.candidate_id}`}</Descriptions.Item>
                          <Descriptions.Item label="分数"><Typography.Text strong>{latestMatch.total_score}</Typography.Text> / {latestMatch.level}</Descriptions.Item>
                          <Descriptions.Item label="推荐结论">{latestMatch.recommendation}</Descriptions.Item>
                          <Descriptions.Item label="匹配理由">{latestMatch.explanation}</Descriptions.Item>
                          <Descriptions.Item label="匹配点">{renderTags(latestMatch.matched_points_json)}</Descriptions.Item>
                          <Descriptions.Item label="风险点">{renderList(latestMatch.risk_points_json)}</Descriptions.Item>
                        </Descriptions>
                      </Card>
                    ) : (
                      <Typography.Text type="secondary">暂无匹配结果</Typography.Text>
                    )}
                  </div>
                </Col>
              </Row>
            )
          },
          {
            key: 'questions',
            label: '面试问题',
            children: (
              <div className="panel">
                <Table
                  rowKey="id"
                  dataSource={analyses}
                  columns={[
                    { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
                    { title: '状态', dataIndex: 'status', render: (value) => <Tag>{value}</Tag> },
                    {
                      title: '问题',
                      render: (_, record) => (
                        <List
                          size="small"
                          dataSource={record.interview_questions_json ?? []}
                          renderItem={(item) => (
                            <List.Item>
                              <Tag>{questionTypeLabel[item.type] ?? item.type}</Tag>
                              {item.question}
                            </List.Item>
                          )}
                        />
                      )
                    }
                  ]}
                />
              </div>
            )
          }
        ]}
      />
    </>
  );
}

function renderTags(values?: unknown[]) {
  if (!values?.length) return '-';
  return values.map((value) => <Tag key={String(value)}>{String(value)}</Tag>);
}

function renderList(values?: unknown[]) {
  if (!values?.length) return '-';
  return (
    <ul className="compact-list">
      {values.map((value) => <li key={String(value)}>{String(value)}</li>)}
    </ul>
  );
}
