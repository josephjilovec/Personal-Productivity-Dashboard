import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import Dashboard from '../src/components/Dashboard';
import { Chart as ChartJS } from 'chart.js';

// Mock axios
jest.mock('axios');

// Mock Chart.js to avoid rendering issues
jest.mock('chart.js', () => ({
  Chart: jest.fn(),
  register: jest.fn(),
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  PointElement: jest.fn(),
  LineElement: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn(),
}));

describe('Dashboard', () => {
  beforeEach(() => {
    axios.get.mockClear();
    ChartJS.register.mockClear();
  });

  test('renders Dashboard component', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('QuantumFlow Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('displays workflows and metrics on successful API calls', async () => {
    axios.get
      .mockResolvedValueOnce({
        data: [
          { workflow_id: 1, name: 'Test Workflow', status: 'completed' },
          { workflow_id: 2, name: 'Another Workflow', status: 'pending' },
        ],
      })
      .mockResolvedValueOnce({
        data: [
          { workflow_id: 1, task_id: 0, runtime: 2.5, circuit_depth: 5, shots: 100, timestamp: '2025-08-03T16:33:00' },
          { workflow_id: 1, task_id: 1, runtime: 3.2, circuit_depth: null, shots: null, timestamp: '2025-08-03T16:34:00' },
        ],
      });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Test Workflow (ID: 1)')).toBeInTheDocument();
      expect(screen.getByText('Status: completed')).toBeInTheDocument();
      expect(screen.getByText('Another Workflow (ID: 2)')).toBeInTheDocument();
      expect(screen.getByText('Status: pending')).toBeInTheDocument();
      expect(screen.getByText('Workflow Performance Metrics')).toBeInTheDocument();
      expect(screen.getByText(/Runtime: 2.50s/)).toBeInTheDocument();
      expect(screen.getByText(/Circuit Depth: 5/)).toBeInTheDocument();
      expect(screen.getByText(/Shots: 100/)).toBeInTheDocument();
    });

    expect(axios.get).toHaveBeenCalledWith('/api/workflows');
    expect(axios.get).toHaveBeenCalledWith('/api/performance');
  });

  test('displays no workflows message when API returns empty', async () => {
    axios.get
      .mockResolvedValueOnce({ data: [] })
      .mockResolvedValueOnce({ data: [] });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('No workflows found.')).toBeInTheDocument();
      expect(screen.getByText('No metrics available.')).toBeInTheDocument();
    });
  });

  test('handles API call failure', async () => {
    axios.get.mockRejectedValue({ response: { data: { detail: 'API error' } } });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch data: API error')).toBeInTheDocument();
    });
  });

  test('renders Chart.js visualization with correct data', async () => {
    axios.get
      .mockResolvedValueOnce({ data: [{ workflow_id: 1, name: 'Test Workflow', status: 'completed' }] })
      .mockResolvedValueOnce({
        data: [
          { workflow_id: 1, task_id: 0, runtime: 2.5, circuit_depth: 5, shots: 100, timestamp: '2025-08-03T16:33:00' },
          { workflow_id: 1, task_id: 1, runtime: 3.2, circuit_depth: null, shots: null, timestamp: '2025-08-03T16:34:00' },
        ],
      });

    render(<Dashboard />);

    await waitFor(() => {
      expect(ChartJS.register).toHaveBeenCalled();
      expect(screen.getByText('Workflow Performance Metrics')).toBeInTheDocument();
    });
  });
});
