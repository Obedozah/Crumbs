import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/AuthContext';
import Navbar from './Navbar';
import Footer from './Footer';

function AppLayout() {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to-="/login" />;
    }

    return (
        <div>
            <Navbar />
            <Outlet />
            <Footer />
        </div>
    );
}

export default AppLayout;