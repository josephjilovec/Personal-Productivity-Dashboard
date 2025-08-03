import sqlite3
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app for performance metrics API
app = FastAPI()

# Pydantic model for API response
class MetricsResponse(BaseModel):
    workflow_id: int
    task_id: int
    runtime: float
    circuit_depth: Optional[int] = None
    shots: Optional[int] = None

class PerformanceMonitor:
    """Tracks and stores performance metrics for hybrid workflows."""
    
    def __init__(self, db_path: str = 'workflows.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize SQLite table for performance metrics."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    workflow_id INTEGER,
                    task_id INTEGER,
                    runtime REAL,
                    circuit_depth INTEGER,
                    shots INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (workflow_id, task_id)
                )
            ''')
            self.conn.commit()
            logger.info(f"Initialized performance_metrics table in {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def track_metrics(self, workflow_id: int, task_id: int, task_config: Dict[str, Any]) -> None:
        """Track performance metrics for a task and store in SQLite."""
        try:
            start_time = time.time()
            task_type = task_config.get('type')
            config = task_config.get('config', {})
            
            # Simulate task execution (replace with actual execution in engine.py)
            circuit_depth = config.get('depth', 0) if task_type == 'quantum' else None
            shots = config.get('shots', 0) if task_type == 'quantum' else None
            runtime = time.time() - start_time

            # Store metrics
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO performance_metrics (workflow_id, task_id, runtime, circuit_depth, shots)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, task_id, runtime, circuit_depth, shots))
            self.conn.commit()
            logger.info(f"Tracked metrics for workflow {workflow_id}, task {task_id}: runtime={runtime:.2f}s")
        except sqlite3.Error as e:
            logger.error(f"Error tracking metrics for workflow {workflow_id}, task {task_id}: {str(e)}")
            raise
    
    def get_metrics(self, workflow_id: int, task_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Retrieve performance metrics for a workflow or specific task."""
        try:
            cursor = self.conn.cursor()
            if task_id is not None:
                cursor.execute('''
                    SELECT workflow_id, task_id, runtime, circuit_depth, shots, timestamp
                    FROM performance_metrics
                    WHERE workflow_id = ? AND task_id = ?
                ''', (workflow_id, task_id))
            else:
                cursor.execute('''
                    SELECT workflow_id, task_id, runtime, circuit_depth, shots, timestamp
                    FROM performance_metrics
                    WHERE workflow_id = ?
                ''', (workflow_id,))

            results = [
                {
                    'workflow_id': row[0],
                    'task_id': row[1],
                    'runtime': row[2],
                    'circuit_depth': row[3],
                    'shots': row[4],
                    'timestamp': row[5]
                }
                for row in cursor.fetchall()
            ]
            if not results:
                raise ValueError(f"No metrics found for workflow {workflow_id}")
            logger.info(f"Retrieved metrics for workflow {workflow_id}")
            return results
        except (sqlite3.Error, ValueError) as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            return None
    
    def close(self) -> None:
        """Close the database connection."""
        try:
            if self.conn:
                self.conn.close()
                logger.info("Closed database connection")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {str(e)}")

# FastAPI endpoints
@app.get("/api/performance/{workflow_id}", response_model=List[MetricsResponse])
async def get_workflow_metrics(workflow_id: int):
    """API endpoint to retrieve metrics for a workflow."""
    monitor = PerformanceMonitor()
    try:
        metrics = monitor.get_metrics(workflow_id)
        if metrics is None:
            raise HTTPException(status_code=404, detail=f"No metrics found for workflow {workflow_id}")
        return metrics
    finally:
        monitor.close()

@app.get("/api/performance/{workflow_id}/{task_id}", response_model=MetricsResponse)
async def get_task_metrics(workflow_id: int, task_id: int):
    """API endpoint to retrieve metrics for a specific task."""
    monitor = PerformanceMonitor()
    try:
        metrics = monitor.get_metrics(workflow_id, task_id)
        if metrics is None or not metrics:
            raise HTTPException(status_code=404, detail=f"No metrics found for workflow {workflow_id}, task {task_id}")
        return metrics[0]
    finally:
        monitor.close()

if __name__ == "__main__":
    # Example usage
    monitor = PerformanceMonitor()
    task_config = {
        'type': 'quantum',
        'config': {'circuit': 'simple_x', 'shots': 100, 'depth': 5}
    }
    monitor.track_metrics(workflow_id=1, task_id=0, task_config=task_config)
    metrics = monitor.get_metrics(workflow_id=1)
    print(metrics)
    monitor.close()
