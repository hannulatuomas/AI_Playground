import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { UserProvider } from './contexts/UserContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { Navigation } from './components/layout/Navigation';
import { Footer } from './components/layout/Footer';
import { AssetFormWrapper } from './components/wrappers/AssetFormWrapper';
import { AssetTypeListWrapper } from './components/wrappers/AssetTypeListWrapper';
import { AssetTypeFormWrapper } from './components/wrappers/AssetTypeFormWrapper';

// Lazy load components
const LandingPage = lazy(() => import('./components/layout/LandingPage'));
const ContainerList = lazy(() => import('./components/containers/ContainerList'));
const CreateContainer = lazy(() => import('./components/containers/CreateContainer'));
const ContainerDetails = lazy(() => import('./components/containers/ContainerDetails'));
const NotFound = lazy(() => import('./components/common/NotFound'));

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <UserProvider>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <ErrorBoundary>
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/containers" element={<ContainerList />} />
                <Route path="/containers/new" element={<CreateContainer />} />
                <Route path="/containers/:containerId" element={<ContainerDetails />} />
                <Route path="/containers/:containerId/assets/new" element={<AssetFormWrapper />} />
                <Route path="/containers/:containerId/assets/:assetId" element={<AssetFormWrapper />} />
                <Route path="/containers/:containerId/asset-types" element={<AssetTypeListWrapper />} />
                <Route path="/containers/:containerId/asset-types/new" element={<AssetTypeFormWrapper />} />
                <Route path="/containers/:containerId/asset-types/:assetTypeId" element={<AssetTypeFormWrapper />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
          <Footer />
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={true}
            closeOnClick={true}
            rtl={false}
            pauseOnFocusLoss={true}
            draggable={true}
            pauseOnHover={true}
            aria-label="Notifications"
          />
        </div>
      </UserProvider>
    </Router>
  );
}

export default App; 