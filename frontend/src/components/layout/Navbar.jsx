import AuthenticatedLinks from './AuthenticatedLinks';
import UnauthenticatedLinks from './UnauthenticatedLinks';
import { useAuth } from '../../context/AuthContext';

function Navbar() {
    const { user } = useAuth();

    return (
        <nav className='navbar'>
            <div className='navbar-logo'>
                <img src='/logo.png' alt='Crumbs Logo' />
            </div>
            <div className='navbar-links'>
                {user ? <AuthenticatedLinks /> : <UnauthenticatedLinks />}
            </div>
        </nav>
    )
}

export default Navbar;