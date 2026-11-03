import { Navigate, useNavigate } from 'react-router-dom';
import { GoogleSignInButton } from '@firebase-oss/ui-react';
import { useAuth } from '../context/AuthContext';
import AuthCard from '../components/ui/AuthCard';
import SignUpScreen from '../components/ui/SignUpScreen';

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
            <SignUpScreen
                onSignUp={() => navigate("/dashboard")}
                onSignInClick={() => navigate("/login")}
            >
                <GoogleSignInButton themed="neutral" />
            </SignUpScreen>
        </AuthCard>
    );
}

export default Register;
