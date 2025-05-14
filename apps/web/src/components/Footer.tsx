import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>&copy; {new Date().getFullYear()} Skin Triage - Powered by EfficientNet</p>
        <div className="disclaimer">
          <p>
            <strong>Disclaimer:</strong> This application is for informational purposes only and
            is not a substitute for professional medical advice, diagnosis, or treatment.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
