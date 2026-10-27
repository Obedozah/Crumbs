import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthCard from '../components/ui/AuthCard';
import GoogleButton from '../components/ui/GoogleButton';

function Register() {
    const { user, register, loginWithGoogle } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    if (user) {
        return <Navigate to="/dashboard" replace />;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (await register(email, password)) {
            navigate("/dashboard");
        }
    }

    async function handleGoogle() {
        if (await loginWithGoogle()) {
            navigate("/dashboard");
        }
    }

    return (
        <AuthCard
            title="Create an Account"
            subtitle={<>Already have an account? <Link to="/login">Log in</Link></>}
        >
            <form className="auth-form" onSubmit={handleSubmit}>
                <label className="field">
                    <span>Email</span>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        autoComplete="email"
                        required
                    />
                </label>
                <label className="field">
                    <span>Password</span>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        autoComplete="new-password"
                        required
                    />
                </label>
                <button type="submit" className="btn btn-primary auth-submit">Create Account</button>
            </form>
            <p className="auth-divider">or</p>
            <GoogleButton onClick={handleGoogle} />
        </AuthCard>
    );
}

export default Register;
