function AuthCard({ children }) {
    return (
        <div className="frame auth-frame">
            <div className="frame-inner auth-card">
                <div className="auth-brand">
                    <img src="/Crumbs%20Toast%20Data%20Integration%20Logo.png" alt="Crumbs: a Toast API integration to data analysis" />
                </div>
                <div className="auth-body">
                    {children}
                </div>
            </div>
        </div>
    );
}

export default AuthCard;
