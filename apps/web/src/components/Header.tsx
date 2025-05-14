import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <h1>Skin Triage</h1>
        <p>Upload a skin image to determine if it shows acne or another condition</p>
      </div>
    </header>
  );
};

export default Header;
