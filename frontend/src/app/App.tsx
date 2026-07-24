import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router';
import { ErrorBoundary } from '@/app/ErrorBoundary';
import { LoadingSkeleton } from '@/components/feedback/States';
import { AuthProvider } from '@/contexts/AuthContext';
import { LoginPage } from '@/features/auth/LoginPage';
import { AppLayout } from '@/layouts/AppLayout';
import { ForbiddenPage, NotFoundPage, ServerErrorPage } from '@/pages/ErrorPages';
import { QueryProvider } from '@/providers/QueryProvider';import { ToastProvider } from '@/components/feedback/Toast';
import { ProtectedRoute } from '@/routes/ProtectedRoute';
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage })));
const AIChatPage = lazy(() => import('@/features/ai-chat/AIChatPage').then((m) => ({ default: m.AIChatPage })));
const VisitsPage = lazy(() => import('@/features/visits/VisitsPage').then((m) => ({ default: m.VisitsPage })));
const RoutesPage = lazy(() => import('@/features/routes/RoutesPage').then((m) => ({ default: m.RoutesPage })));
const CalendarPage = lazy(() => import('@/features/calendar/CalendarPage').then((m) => ({ default: m.CalendarPage })));
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const DoctorListPage = lazy(() => import('@/features/doctors/DoctorListPage').then((m) => ({ default: m.DoctorListPage })));
const DoctorDetailPage = lazy(() => import('@/features/doctors/DoctorDetailPage').then((m) => ({ default: m.DoctorDetailPage })));
const DoctorFormPage = lazy(() => import('@/features/doctors/DoctorFormPage').then((m) => ({ default: m.DoctorFormPage })));
const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { element: <ProtectedRoute />, children: [{ element: <AppLayout />, errorElement: <ServerErrorPage />, children: [{ index: true, element: <DashboardPage /> }, { path: 'ai', element: <AIChatPage /> }, { path: 'visits', element: <VisitsPage /> }, { path: 'routes', element: <RoutesPage /> }, { path: 'calendar', element: <CalendarPage /> }, { path: 'settings', element: <SettingsPage /> }, { path: 'doctors', element: <DoctorListPage /> }, { path: 'doctors/new', element: <DoctorFormPage /> }, { path: 'doctors/:id', element: <DoctorDetailPage /> }, { path: 'doctors/:id/edit', element: <DoctorFormPage /> }] }] },
  { path: '/403', element: <ForbiddenPage /> },
  { path: '*', element: <NotFoundPage /> }
]);
export function App() { return <ErrorBoundary><QueryProvider><ToastProvider><AuthProvider><Suspense fallback={<LoadingSkeleton />}><RouterProvider router={router} /></Suspense></AuthProvider></ToastProvider></QueryProvider></ErrorBoundary>; }
