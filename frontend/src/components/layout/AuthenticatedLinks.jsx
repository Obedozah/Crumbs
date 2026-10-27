import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function AuthenticatedLinks() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate('/');
    }

    return (
        <>
            <ul className='navbar-links'>
                <li><NavLink to="/" end>Home</NavLink></li>
                <li><NavLink to="/contact">Contact</NavLink></li>
                <li><NavLink to="/about">About</NavLink></li>
                <li><NavLink to="/dashboard">Dashboard</NavLink></li>
            </ul>
            <div className='navbar-actions'>
                <button type="button" className='btn btn-secondary btn-sm' onClick={handleLogout}>
                    Log out
                </button>
            </div>
        </>
    );
}

export default AuthenticatedLinks;
