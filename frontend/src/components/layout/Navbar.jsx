import { Link } from 'react-router-dom';
import AuthenticatedLinks from './AuthenticatedLinks';
import UnauthenticatedLinks from './UnauthenticatedLinks';
import { useAuth } from '../../context/AuthContext';

function Navbar() {
    const { user } = useAuth();

    return (
        <header className='navbar'>
            <nav className='navbar-inner'>
                <Link to='/' className='navbar-logo'>
                    <img src='/favicon.png' alt='' />
                    <span>crumbs</span>
                </Link>
                {user ? <AuthenticatedLinks /> : <UnauthenticatedLinks />}
            </nav>
        </header>
    )
}

export default Navbar;
