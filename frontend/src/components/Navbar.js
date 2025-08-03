import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-xl font-bold">
          QuantumFlow Toolkit
        </Link>
        <div className="space-x-4">
          <Link
            to="/"
            className="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium transition duration-300"
          >
            Dashboard
          </Link>
          <Link
            to="/designer"
            className="text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium transition duration-300"
          >
            Workflow Designer
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
