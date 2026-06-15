import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '../components/Layout/AppLayout';
import Dashboard from '../pages/Dashboard';
import Jobs from '../pages/Jobs';
import Candidates from '../pages/Candidates';
import ResumeImport from '../pages/ResumeImport';
import Applications from '../pages/Applications';
import Interviews from '../pages/Interviews';
import TalentPool from '../pages/TalentPool';
import Settings from '../pages/Settings';

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
      { path: 'talent-pool', element: <TalentPool /> },
      { path: 'settings', element: <Settings /> }
    ]
  }
]);
