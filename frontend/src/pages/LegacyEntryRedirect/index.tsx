import { Result, Spin } from 'antd';
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

type LegacyEntryRedirectProps = {
  mode: 'resume-import' | 'ai-recruitment';
};

export default function LegacyEntryRedirect({ mode }: LegacyEntryRedirectProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const candidateId = searchParams.get('candidateId');
    const jobId = searchParams.get('jobId');

    if (candidateId) {
      navigate(`/candidates/${candidateId}`, { replace: true });
      return;
    }

    if (jobId) {
      navigate(`/jobs/${jobId}`, { replace: true });
      return;
    }

    if (mode === 'resume-import') {
      navigate('/candidates', { replace: true });
      return;
    }

    navigate('/applications', { replace: true });
  }, [mode, navigate, searchParams]);

  return (
    <Result
      title="正在跳转到新的业务流程入口"
      subTitle="简历导入和 AI 招聘已迁入候选人详情、职位详情和招聘流程页面。"
      icon={<Spin size="large" />}
    />
  );
}
