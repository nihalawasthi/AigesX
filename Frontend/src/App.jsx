import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LanguageProvider } from "./context/LanguageContext";
import { ScanProvider } from "./context/ScanContext";
import Login from "./pages/Login";
import Landing from "./pages/Landing";
import About from "./pages/About";
import UserDashboard from "./pages/UserDashboard";
import TargetIntake from "./pages/TargetIntake";
import Settings from "./pages/Settings";
import ReportPage from "./pages/ReportPage";

const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
};

const App = () => {
  return (
    <AuthProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <LanguageProvider>
          <ScanProvider>
            <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/about" element={<About />} />
            <Route path="/login" element={<Login />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <UserDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/intake"
              element={
                <ProtectedRoute>
                  <TargetIntake />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <ReportPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </ScanProvider>
        </LanguageProvider>
      </Router>
    </AuthProvider>
  );
};

export default App;
