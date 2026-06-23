import { MessageOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Empty, Table, Tag, Typography } from 'antd';
import { useMemo } from 'react';
import { fetchCandidates } from '../../api/candidates';
import { fetchInterviews } from '../../api/interviews';
import { fetchJobs } from '../../api/jobs';

const statusLabel: Record<string, string> = {
  scheduled: '待面试',
  completed: '已完成',
  cancelled: '已取消',
  no_show: '未到场'
};

export default function InterviewFeedback() {
  const { data: interviews = [], isLoading } = useQuery({ queryKey: ['interviews'], queryFn: fetchInterviews });
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs });
  const { data: candidates = [] } = useQuery({ queryKey: ['candidates'], queryFn: fetchCandidates });
  const jobMap = useMemo(() => new Map(jobs.map((job) => [job.id, job.title])), [jobs]);
  const candidateMap = useMemo(() => new Map(candidates.map((candidate) => [candidate.id, candidate.name])), [candidates]);
  const feedbackRows = useMemo(
    () =>
      [...interviews].sort((a, b) => {
        const left = a.scheduled_start_at ? new Date(a.scheduled_start_at).getTime() : 0;
        const right = b.scheduled_start_at ? new Date(b.scheduled_start_at).getTime() : 0;
        return right - left;
      }),
    [interviews]
  );

  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>面试反馈</Typography.Title>
      </div>
      <div className="panel">
        {feedbackRows.length === 0 && !isLoading ? (
          <Empty image={<MessageOutlined style={{ fontSize: 48 }} />} description="暂无面试反馈记录" />
        ) : (
          <Table
            rowKey="id"
            loading={isLoading}
            dataSource={feedbackRows}
            columns={[
              { title: '候选人', dataIndex: 'candidate_id', render: (value) => candidateMap.get(value) ?? `#${value}` },
              { title: '职位', dataIndex: 'job_id', render: (value) => jobMap.get(value) ?? `#${value}` },
              { title: '轮次', dataIndex: 'round', width: 90, render: (value) => `第 ${value} 轮` },
              { title: '面试时间', dataIndex: 'scheduled_start_at', render: (value) => (value ? new Date(value).toLocaleString() : '-') },
              { title: '反馈状态', dataIndex: 'status', render: (value) => <Tag>{statusLabel[value] ?? value}</Tag> },
              { title: '面试方式', dataIndex: 'interview_type' },
              { title: '地点/链接', render: (_, record) => record.meeting_link || record.location || '-' },
              {
                title: '反馈说明',
                render: (_, record) => {
                  if (record.status === 'completed') return '已完成面试，可在招聘流程中继续推进。';
                  if (record.status === 'cancelled') return '面试已取消，建议回到招聘流程调整安排。';
                  if (record.status === 'no_show') return '候选人未到场，建议记录原因并重新安排。';
                  return '等待面试完成后回写结论。';
                }
              }
            ]}
          />
        )}
      </div>
    </>
  );
}
