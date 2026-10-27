import { Link } from 'react-router-dom';

function Footer() {
    return (
        <footer className="footer">
            <div className="footer-inner">
                <p>&copy; 2026 Crumbs &middot; A Toast API integration to data analysis</p>
                <ul className="footer-links">
                    <li><Link to="/about">About</Link></li>
                    <li><Link to="/contact">Contact</Link></li>
                </ul>
            </div>
        </footer>
    );
}

export default Footer;
