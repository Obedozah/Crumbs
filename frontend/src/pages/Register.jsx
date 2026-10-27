import { Navigate, useNavigate } from 'react-router-dom';
import { SignUpAuthScreen, GoogleSignInButton } from '@firebase-oss/ui-react';
import { useAuth } from '../context/AuthContext';
import AuthCard from '../components/ui/AuthCard';

function Register() {
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
            <SignUpAuthScreen
                onSignUp={() => navigate("/dashboard")}
                onSignInClick={() => navigate("/login")}
            >
                <GoogleSignInButton themed="neutral" />
            </SignUpAuthScreen>
        </AuthCard>
    );
}

export default Register;
