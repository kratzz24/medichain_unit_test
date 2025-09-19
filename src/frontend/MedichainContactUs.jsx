import React, { useState } from 'react';
import '../frontend/MedichainContactUs.css';

const MedichainContactUs = () => {
  const [form, setForm] = useState({ name: '', email: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    // Here you would typically send the form data to your backend or email service
  };

  return (
    <div className="contactus-container">
      <div className="contactus-card">
        <h2 className="contactus-title">Contact Us</h2>
        <p className="contactus-subtitle">
          Have questions or feedback? Fill out the form below and we'll get back to you!
        </p>
        {submitted ? (
          <div className="contactus-success">Thank you for contacting us!</div>
        ) : (
          <form className="contactus-form" onSubmit={handleSubmit}>
            <input
              className="contactus-input"
              type="text"
              name="name"
              placeholder="Your Name"
              value={form.name}
              onChange={handleChange}
              required
            />
            <input
              className="contactus-input"
              type="email"
              name="email"
              placeholder="Your Email"
              value={form.email}
              onChange={handleChange}
              required
            />
            <textarea
              className="contactus-textarea"
              name="message"
              placeholder="Your Message"
              value={form.message}
              onChange={handleChange}
              required
            />
            <button className="btn btn-primary contactus-btn" type="submit">
              Send Message
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default MedichainContactUs;
