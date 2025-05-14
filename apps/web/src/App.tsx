import React from 'react';
import './App.css';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <ImageUploader />
      </main>
      <Footer />
    </div>
  );
}

export default App;
