import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const features = [
    {
        title: "Connect Toast",
        text: "something here",
    },
    {
        title: "See Your Numbers",
        text: "something here",
    },
    {
        title: "Spot Trends",
        text: "something here",
    },
];

const steps = [
    { title: "step 1", text: "somethng somethin" },
    { title: "step 2", text: "something." },
    { title: "step 3", text: "something something" },
];

function Home() {
    const { user } = useAuth();

    return (
        <div className="container">
            <section className="frame">
                <div className="frame-inner hero">
                    <div className="hero-text">
                        <p className="eyebrow">Toast API &times; Data Analysis</p>
                        <h1>business something.</h1>
                        <p className="lead">
                            something something
                        </p>
                        <div className="button-row">
                            {user ? (
                                <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
                            ) : (
                                <Link to="/register" className="btn btn-primary">Get Started</Link>
                            )}
                            <Link to="/about" className="btn btn-secondary">Learn More</Link>
                        </div>
                    </div>
                    <div className="hero-image">
                        <img src="/Crumbs%20Toast%20Data%20Integration%20Logo.png" alt="Crumbs logo" />
                    </div>
                </div>
            </section>

            <section className="section">
                <h2 className="section-title">What Crumbs Does</h2>
                <div className="card-grid">
                    {features.map((feature) => (
                        <div className="card" key={feature.title}>
                            <span className="card-dot" />
                            <h3>{feature.title}</h3>
                            <p>{feature.text}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="section">
                <h2 className="section-title">How It Works</h2>
                <ol className="steps">
                    {steps.map((step, index) => (
                        <li className="step" key={step.title}>
                            <span className="step-number">{index + 1}</span>
                            <div>
                                <h3>{step.title}</h3>
                                <p>{step.text}</p>
                            </div>
                        </li>
                    ))}
                </ol>
            </section>

            {!user && (
                <section className="cta">
                    <h2>Ready to get Started?</h2>
                    <Link to="/register" className="btn btn-primary">Create an Account</Link>
                </section>
            )}
        </div>
    );
}

export default Home;
