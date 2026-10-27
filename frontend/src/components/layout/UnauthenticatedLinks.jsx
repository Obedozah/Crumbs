import { Link, NavLink } from 'react-router-dom';

function UnauthenticatedLinks() {
    return (
        <>
            <ul className='navbar-links'>
                <li><NavLink to="/" end>Home</NavLink></li>
                <li><NavLink to="/contact">Contact</NavLink></li>
                <li><NavLink to="/about">About</NavLink></li>
            </ul>
            <div className='navbar-actions'>
                <Link to="/login" className='btn btn-primary btn-sm'>Log in</Link>
            </div>
        </>
    )
}

export default UnauthenticatedLinks;
