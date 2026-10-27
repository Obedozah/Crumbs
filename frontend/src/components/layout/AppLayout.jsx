import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Navbar from './Navbar';
import Footer from './Footer';

function AppLayout() {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="app-shell">
            <Navbar />
            <main className="page-main">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}

export default AppLayout;
