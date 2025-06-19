import React from 'react';
import './App.css';
import InstituicoesList from './components/InstituicoesList';
import Mapa from './components/Mapa';

function App() {
  return (
    <div className="App">
      <h1>Censo Escolar - Mapa de Instituições</h1>
      <div className="container">
        <div className="list-container">
          <h2>Lista de Instituições</h2>
          <InstituicoesList />
        </div>
        <div className="map-container">
          <h2>Mapa</h2>
          <Mapa />
        </div>
      </div>
    </div>
  );
}

export default App;