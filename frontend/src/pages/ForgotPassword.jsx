import { useNavigate } from 'react-router-dom';
import { ForgotPasswordAuthScreen } from '@firebase-oss/ui-react';
import AuthCard from '../components/ui/AuthCard';

function ForgotPassword() {
    const navigate = useNavigate();

    return (
        <AuthCard>
            <ForgotPasswordAuthScreen onBackToSignInClick={() => navigate("/login")} />
        </AuthCard>
    );
}

export default ForgotPassword;
