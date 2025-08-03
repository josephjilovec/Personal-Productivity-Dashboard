import React, { useState } from 'react';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

const initialTasks = [
  { id: 'task-1', type: 'classical', config: { operation: 'preprocess', data: [] } },
  { id: 'task-2', type: 'quantum', config: { circuit: 'simple_x', shots: 100, backend: 'cirq' } },
];

function WorkflowDesigner() {
  const [workflowName, setWorkflowName] = useState('');
  const [tasks, setTasks] = useState(initialTasks);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const reorderedTasks = Array.from(tasks);
    const [movedTask] = reorderedTasks.splice(result.source.index, 1);
    reorderedTasks.splice(result.destination.index, 0, movedTask);
    setTasks(reorderedTasks);
  };

  const addTask = (type) => {
    const newTask = {
      id: `task-${tasks.length + 1}`,
      type,
      config: type === 'classical' 
        ? { operation: 'preprocess', data: [] }
        : { circuit: 'simple_x', shots: 100, backend: 'cirq' },
    };
    setTasks([...tasks, newTask]);
  };

  const updateTaskConfig = (id, field, value) => {
    setTasks(tasks.map(task => 
      task.id === id ? { ...task, config: { ...task.config, [field]: value } } : task
    ));
  };

  const submitWorkflow = async () => {
    if (!workflowName) {
      setError('Workflow name is required');
      return;
    }
    try {
      const response = await axios.post('/api/workflows', {
        name: workflowName,
        tasks,
      });
      setSuccess(`Workflow '${workflowName}' created with ID: ${response.data.workflow_id}`);
      setError(null);
      setWorkflowName('');
      setTasks(initialTasks);
    } catch (err) {
      setError(`Failed to create workflow: ${err.response?.data?.detail || err.message}`);
      setSuccess(null);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Workflow Designer</h2>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Workflow Name</label>
        <input
          type="text"
          value={workflowName}
          onChange={(e) => setWorkflowName(e.target.value)}
          className="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter workflow name"
        />
      </div>

      <div className="mb-4 flex space-x-4">
        <button
          onClick={() => addTask('classical')}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300"
        >
          Add Classical Task
        </button>
        <button
          onClick={() => addTask('quantum')}
          className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition duration-300"
        >
          Add Quantum Task
        </button>
      </div>

      {error && <div className="mb-4 text-red-600">{error}</div>}
      {success && <div className="mb-4 text-green-600">{success}</div>}

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="tasks">
          {(provided) => (
            <div
              {...provided.droppableProps}
              ref={provided.innerRef}
              className="space-y-4"
            >
              {tasks.map((task, index) => (
                <Draggable key={task.id} draggableId={task.id} index={index}>
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className="p-4 bg-gray-50 rounded-md shadow-sm border border-gray-200"
                    >
                      <h3 className="text-lg font-semibold text-gray-800">
                        {task.type === 'classical' ? 'Classical Task' : 'Quantum Task'} #{index + 1}
                      </h3>
                      {task.type === 'classical' ? (
                        <div className="mt-2">
                          <label className="block text-sm text-gray-600">Operation</label>
                          <input
                            type="text"
                            value={task.config.operation}
                            onChange={(e) => updateTaskConfig(task.id, 'operation', e.target.value)}
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                            placeholder="e.g., preprocess"
                          />
                        </div>
                      ) : (
                        <div className="mt-2 space-y-2">
                          <div>
                            <label className="block text-sm text-gray-600">Circuit</label>
                            <input
                              type="text"
                              value={task.config.circuit}
                              onChange={(e) => updateTaskConfig(task.id, 'circuit', e.target.value)}
                              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                              placeholder="e.g., simple_x"
                            />
                          </div>
                          <div>
                            <label className="block text-sm text-gray-600">Shots</label>
                            <input
                              type="number"
                              value={task.config.shots}
                              onChange={(e) => updateTaskConfig(task.id, 'shots', parseInt(e.target.value))}
                              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                              placeholder="e.g., 100"
                            />
                          </div>
                          <div>
                            <label className="block text-sm text-gray-600">Backend</label>
                            <select
                              value={task.config.backend}
                              onChange={(e) => updateTaskConfig(task.id, 'backend', e.target.value)}
                              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                            >
                              <option value="cirq">Cirq</option>
                              <option value="qiskit">Qiskit</option>
                              <option value="pennylane">PennyLane</option>
                            </select>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <button
        onClick={submitWorkflow}
        className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-300"
      >
        Save Workflow
      </button>
    </div>
  );
}

export default WorkflowDesigner;
