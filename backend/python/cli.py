import click
import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from backend.python.workflow.engine import WorkflowEngine

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """QuantumFlow Toolkit CLI: Manage hybrid quantum-classical workflows."""
    pass

@cli.command()
@click.option('--name', required=True, help='Name of the workflow')
@click.option('--tasks-file', type=click.Path(exists=True), required=True, help='JSON file containing tasks')
def create_workflow(name: str, tasks_file: str):
    """Define a new hybrid workflow and save it to the database."""
    try:
        # Load tasks from JSON file
        tasks_path = Path(tasks_file)
        with tasks_path.open('r') as f:
            tasks = json.load(f)
        
        # Validate tasks
        if not isinstance(tasks, list) or not all(isinstance(t, dict) and 'type' in t and 'config' in t for t in tasks):
            raise ValueError("Tasks must be a list of dictionaries with 'type' and 'config' keys")

        # Initialize workflow engine
        engine = WorkflowEngine()
        
        # Define workflow
        workflow_id = engine.define_workflow(name, tasks)
        if workflow_id == -1:
            raise ValueError("Failed to define workflow")

        click.echo(f"Workflow '{name}' created successfully with ID: {workflow_id}")
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
    finally:
        if 'engine' in locals():
            engine.close()

@cli.command()
@click.option('--id', type=int, required=True, help='Workflow ID to run')
def run_workflow(id: int):
    """Execute a workflow by ID."""
    try:
        engine = WorkflowEngine()
        result = engine.execute_workflow(id)
        if result is None:
            raise ValueError(f"Failed to execute workflow ID {id}")

        click.echo(f"Workflow {id} executed successfully:")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        logger.error(f"Error running workflow {id}: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
    finally:
        if 'engine' in locals():
            engine.close()

@cli.command()
@click.option('--id', type=int, required=True, help='Workflow ID to monitor')
def monitor_workflow(id: int):
    """Monitor the status of a workflow by ID."""
    try:
        engine = WorkflowEngine()
        status = engine.get_workflow_status(id)
        if status is None:
            raise ValueError(f"Workflow ID {id} not found")

        click.echo(f"Workflow Status for ID {id}:")
        click.echo(json.dumps(status, indent=2))
    except Exception as e:
        logger.error(f"Error monitoring workflow {id}: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
    finally:
        if 'engine' in locals():
            engine.close()

if __name__ == '__main__':
    cli()
