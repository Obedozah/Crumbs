import { useAuth } from '../context/AuthContext';

// TODO: replace with Toast data
const stats = [
    { label: "Total Sales", value: "—" },
    { label: "Orders", value: "—" },
    { label: "Average Ticket", value: "—" },
    { label: "Top Item", value: "—" },
];

()=>{
    
}

function Dashboard() {
    const { user } = useAuth();

    return (
        <div className="container">
            <header className="dashboard-header">
                <div>
                    <p className="eyebrow">Dashboard</p>
                    <h1>Welcome back{user.displayName ? `, ${user.displayName}` : ""}</h1>
                    <p className="muted">Signed in as {user.email}</p>
                </div>
                <button type="button" className="btn btn-primary">Connect Toast</button>
            </header>

            <div className="stat-grid">
                {stats.map((stat) => (
                    <div className="card stat-card" key={stat.label}>
                        <p className="stat-label">{stat.label}</p>
                        <p className="stat-value">{stat.value}</p>
                    </div>
                ))}
            </div>

            <div className="panel-grid">
                <section className="card panel">
                    <h3>Sales Over Time</h3>
                    <div className="empty-state">Connect your Toast account to see sales data.</div>
                </section>
                <section className="card panel">
                    <h3>Top Menu Items</h3>
                    <div className="empty-state">No menu data yet.</div>
                </section>
            </div>
        </div>
    );
}

export default Dashboard;
