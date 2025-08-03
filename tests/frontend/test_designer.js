import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DragDropContext } from 'react-beautiful-dnd';
import axios from 'axios';
import WorkflowDesigner from '../src/components/WorkflowDesigner';

// Mock axios
jest.mock('axios');

// Mock react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children }) => <div>{children}</div>,
  Droppable: ({ children }) => children({ provided: { innerRef: jest.fn(), droppableProps: {} }, snapshot: {} }),
  Draggable: ({ children, draggableId, index }) => children({
    provided: {
      innerRef: jest.fn(),
      draggableProps: { 'data-rbd-draggable-id': draggableId },
      dragHandleProps: {},
    },
    snapshot: {},
  }, index),
}));

// Mock component to avoid Router errors
const MockWorkflowDesigner = () => (
  <DragDropContext>
    <WorkflowDesigner />
  </DragDropContext>
);

describe('WorkflowDesigner', () => {
  beforeEach(() => {
    axios.post.mockClear();
  });

  test('renders WorkflowDesigner component', () => {
    render(<MockWorkflowDesigner />);
    
    expect(screen.getByText('Workflow Designer')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter workflow name')).toBeInTheDocument();
    expect(screen.getByText('Add Classical Task')).toBeInTheDocument();
    expect(screen.getByText('Add Quantum Task')).toBeInTheDocument();
  });

  test('adds a classical task', async () => {
    render(<MockWorkflowDesigner />);
    
    const addClassicalButton = screen.getByText('Add Classical Task');
    fireEvent.click(addClassicalButton);
    
    expect(screen.getAllByText(/Classical Task #/)).toHaveLength(3); // Initial 2 tasks + 1 new
    expect(screen.getAllByPlaceholderText('e.g., preprocess')).toHaveLength(3);
  });

  test('adds a quantum task', async () => {
    render(<MockWorkflowDesigner />);
    
    const addQuantumButton = screen.getByText('Add Quantum Task');
    fireEvent.click(addQuantumButton);
    
    expect(screen.getAllByText(/Quantum Task #/)).toHaveLength(2); // Initial 1 quantum task + 1 new
    expect(screen.getAllByPlaceholderText('e.g., simple_x')).toHaveLength(2);
  });

  test('updates task config', async () => {
    render(<MockWorkflowDesigner />);
    
    const operationInput = screen.getAllByPlaceholderText('e.g., preprocess')[0];
    fireEvent.change(operationInput, { target: { value: 'custom_preprocess' } });
    
    expect(operationInput).toHaveValue('custom_preprocess');
  });

  test('submits workflow successfully', async () => {
    axios.post.mockResolvedValue({ data: { workflow_id: 1 } });
    
    render(<MockWorkflowDesigner />);
    
    const nameInput = screen.getByPlaceholderText('Enter workflow name');
    fireEvent.change(nameInput, { target: { value: 'Test Workflow' } });
    
    const saveButton = screen.getByText('Save Workflow');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/workflows', {
        name: 'Test Workflow',
        tasks: expect.any(Array),
      });
      expect(screen.getByText(/Workflow 'Test Workflow' created with ID: 1/)).toBeInTheDocument();
    });
  });

  test('handles submission error for empty workflow name', async () => {
    render(<MockWorkflowDesigner />);
    
    const saveButton = screen.getByText('Save Workflow');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText('Workflow name is required')).toBeInTheDocument();
    });
    expect(axios.post).not.toHaveBeenCalled();
  });

  test('handles API submission failure', async () => {
    axios.post.mockRejectedValue({ response: { data: { detail: 'API error' } } });
    
    render(<MockWorkflowDesigner />);
    
    const nameInput = screen.getByPlaceholderText('Enter workflow name');
    fireEvent.change(nameInput, { target: { value: 'Test Workflow' } });
    
    const saveButton = screen.getByText('Save Workflow');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to create workflow: API error')).toBeInTheDocument();
    });
  });
});
