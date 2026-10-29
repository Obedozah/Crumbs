// Split card used by Login + Register: logo on the left, form on the right.
function AuthCard({ title, subtitle, children }) {
    return (
        <div className="frame auth-frame">
            <div className="frame-inner auth-card">
                <div className="auth-brand">
                    <img src="/Crumbs%20Toast%20Data%20Integration%20Logo.png" alt="Crumbs: a Toast API integration to data analysis" />
                </div>
                <div className="auth-body">
                    <h1 className="auth-title">{title}</h1>
                    {subtitle && <p className="auth-subtitle">{subtitle}</p>}
                    {children}
                </div>
            </div>
        </div>
    );
}

export default AuthCard;
