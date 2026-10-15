import { Routes, Route } from 'react-router-dom';
import AppLayout from '../components/layout/AppLayout';
import PublicLayout from '../components/layout/PublicLayout';
import Home from '../pages/Home';
import Register from '../pages/Register';
import Login from '../pages/Login';

function AppRoutes() {
    return (
        <Routes>
            <Route element={<PublicLayout />}>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
            </Route>
            <Route element={<AppLayout />}>
                <Route path="/" element={<Home />} />
            </Route>
        </Routes>
    );
}

export default AppRoutes;