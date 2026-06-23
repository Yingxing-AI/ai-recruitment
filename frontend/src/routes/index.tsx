import { lazy } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { Navigate } from 'react-router-dom';
import { AppLayout } from '../components/Layout/AppLayout';

const Dashboard = lazy(() => import('../pages/Dashboard'));
const Jobs = lazy(() => import('../pages/Jobs'));
const JobDetail = lazy(() => import('../pages/JobDetail'));
const Candidates = lazy(() => import('../pages/Candidates'));
const CandidateDetail = lazy(() => import('../pages/CandidateDetail'));
const Applications = lazy(() => import('../pages/Applications'));
const Interviews = lazy(() => import('../pages/Interviews'));
const InterviewFeedback = lazy(() => import('../pages/InterviewFeedback'));
const TalentPool = lazy(() => import('../pages/TalentPool'));
const Settings = lazy(() => import('../pages/Settings'));
const LegacyEntryRedirect = lazy(() => import('../pages/LegacyEntryRedirect'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'jobs', element: <Jobs /> },
      { path: 'jobs/:jobId', element: <JobDetail /> },
      { path: 'candidates', element: <Candidates /> },
      { path: 'candidates/:candidateId', element: <CandidateDetail /> },
      { path: 'resume-import', element: <LegacyEntryRedirect mode="resume-import" /> },
      { path: 'applications', element: <Applications /> },
      { path: 'interviews', element: <Navigate to="/interviews/schedule" replace /> },
      { path: 'interviews/schedule', element: <Interviews /> },
      { path: 'interviews/feedback', element: <InterviewFeedback /> },
      { path: 'ai-recruitment', element: <LegacyEntryRedirect mode="ai-recruitment" /> },
      { path: 'talent-pool', element: <TalentPool /> },
      { path: 'settings', element: <Settings /> }
    ]
  }
]);
