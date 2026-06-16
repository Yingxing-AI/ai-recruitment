import { lazy } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '../components/Layout/AppLayout';

const Dashboard = lazy(() => import('../pages/Dashboard'));
const Jobs = lazy(() => import('../pages/Jobs'));
const Candidates = lazy(() => import('../pages/Candidates'));
const ResumeImport = lazy(() => import('../pages/ResumeImport'));
const Applications = lazy(() => import('../pages/Applications'));
const Interviews = lazy(() => import('../pages/Interviews'));
const TalentPool = lazy(() => import('../pages/TalentPool'));
const Settings = lazy(() => import('../pages/Settings'));
const AiRecruitment = lazy(() => import('../pages/AiRecruitment'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'jobs', element: <Jobs /> },
      { path: 'candidates', element: <Candidates /> },
      { path: 'resume-import', element: <ResumeImport /> },
      { path: 'applications', element: <Applications /> },
      { path: 'interviews', element: <Interviews /> },
      { path: 'ai-recruitment', element: <AiRecruitment /> },
      { path: 'talent-pool', element: <TalentPool /> },
      { path: 'settings', element: <Settings /> }
    ]
  }
]);
