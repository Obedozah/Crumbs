import { Navigate, useNavigate } from 'react-router-dom';
import { SignInAuthScreen, GoogleSignInButton } from '@firebase-oss/ui-react';
import { useAuth } from '../context/AuthContext';
import AuthCard from '../components/ui/AuthCard';

function Login() {
    const { user, loading } = useAuth();
    const navigate = useNavigate();

    if (loading) {
        return null;
    }

    if (user) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <AuthCard>
            <SignInAuthScreen
                onSignIn={() => navigate("/dashboard")}
                onSignUpClick={() => navigate("/register")}
                onForgotPasswordClick={() => navigate("/forgot-password")}
            >
                <GoogleSignInButton themed="neutral" />
            </SignInAuthScreen>
        </AuthCard>
    );
}

export default Login;
