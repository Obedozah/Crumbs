import { useState } from 'react';

function Contact() {
    const [sent, setSent] = useState(false);

    function handleSubmit(event) {
        event.preventDefault();
        // TODO: send to backend
        setSent(true);
    }

    return (
        <div className="container">
            <header className="page-header">
                <p className="eyebrow">Contact</p>
                <h1>Get in Touch</h1>
                <p className="lead">something</p>
            </header>

            <section className="frame">
                <div className="frame-inner contact-card">
                    <div className="contact-info">
                        <h2>Reach Us</h2>
                        <p><strong>Email</strong><br />asdlk@gmail.com</p>
                        <p><strong>Project</strong><br />COMP 490 &middot; Fall 2026</p>
                    </div>
                    <div className="contact-form-wrap">
                        {sent ? (
                            <div className="contact-sent">
                                <h2>Thanks!</h2>
                                <p>Your message has been sent. We'll get back to you soon.</p>
                                <button type="button" className="btn btn-secondary" onClick={() => setSent(false)}>
                                    Send another
                                </button>
                            </div>
                        ) : (
                            <form className="contact-form" onSubmit={handleSubmit}>
                                <label className="field">
                                    <span>Name</span>
                                    <input type="text" autoComplete="name" required />
                                </label>
                                <label className="field">
                                    <span>Email</span>
                                    <input type="email" autoComplete="email" required />
                                </label>
                                <label className="field">
                                    <span>Message</span>
                                    <textarea rows="5" required />
                                </label>
                                <button type="submit" className="btn btn-primary">Send Message</button>
                            </form>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Contact;
