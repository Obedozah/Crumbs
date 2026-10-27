import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthCard from '../components/ui/AuthCard';
import GoogleButton from '../components/ui/GoogleButton';

function Login() {
    const { user, login, loginWithGoogle } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    if (user) {
        return <Navigate to="/dashboard" replace />;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (await login(email, password)) {
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
            title="Welcome Back"
            subtitle={<>Don't have an account? <Link to="/register">Sign up</Link></>}
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
                        autoComplete="current-password"
                        required
                    />
                </label>
                <button type="submit" className="btn btn-primary auth-submit">Log In</button>
            </form>
            <p className="auth-divider">or</p>
            <GoogleButton onClick={handleGoogle} />
        </AuthCard>
    );
}

export default Login;
