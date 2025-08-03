import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import WorkflowDesigner from './components/WorkflowDesigner';
import Dashboard from './components/Dashboard';
import './styles/tailwind.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/designer" element={<WorkflowDesigner />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
