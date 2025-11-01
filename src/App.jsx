import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { LandingPage } from '@/components/LandingPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';

// Lazy load pages for better performance
const WorkspacePage = React.lazy(() => import('@/pages/WorkspacePageEnhanced.jsx'));
const ProfilePage = React.lazy(() => import('@/pages/ProfilePage'));
const FeaturesPage = React.lazy(() => import('@/pages/FeaturesPage'));
const AboutPage = React.lazy(() => import('@/pages/AboutPage'));
const LoginPage = React.lazy(() => import('@/pages/auth/LoginPage'));
const SignupPage = React.lazy(() => import('@/pages/auth/SignupPage'));
const NotFoundPage = React.lazy(() => import('@/pages/NotFoundPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    },
  },
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <TooltipProvider>
            <BrowserRouter
              future={{
                v7_startTransition: true,
                v7_relativeSplatPath: true
              }}
            >
              <div className="min-h-screen flex flex-col">
                <Toaster />
                <Sonner />
                <Navigation />
                
                <main className="flex-1">
                  <React.Suspense fallback={
                    <div className="flex items-center justify-center h-64">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  }>
                    <Routes>
                      {/* Public Routes */}
                      <Route path="/" element={<LandingPage />} />
                      <Route path="/features" element={<FeaturesPage />} />
                      <Route path="/about" element={<AboutPage />} />
                      <Route path="/auth/login" element={<LoginPage />} />
                      <Route path="/auth/signup" element={<SignupPage />} />
                      
                      {/* Protected Routes */}
                      <Route path="/workspace" element={
                        <ProtectedRoute>
                          <WorkspacePage />
                        </ProtectedRoute>
                      } />
                      <Route path="/workspace/:projectId" element={
                        <ProtectedRoute>
                          <WorkspacePage />
                        </ProtectedRoute>
                      } />
                      <Route path="/profile" element={
                        <ProtectedRoute>
                          <ProfilePage />
                        </ProtectedRoute>
                      } />
                      
                      {/* Catch-all Route */}
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </React.Suspense>
                </main>
                
                {/* Only show footer on non-workspace pages */}
                <Routes>
                  <Route path="/workspace/*" element={null} />
                  <Route path="/profile" element={null} />
                  <Route path="*" element={<Footer />} />
                </Routes>
              </div>
            </BrowserRouter>
          </TooltipProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
