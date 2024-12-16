import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Home } from '@/pages/Home';

export const router = createBrowserRouter([
  {
    element: <ErrorBoundary />,
    children: [
      {
        path: '/',
        element: <Home />,
      },

      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
