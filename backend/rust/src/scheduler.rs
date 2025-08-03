use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::collections::BinaryHeap;
use tokio::sync::Mutex;
use std::sync::Arc;

// Task configuration structure
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TaskConfig {
    pub id: usize,
    pub r#type: String,
    pub backend: String,
    pub estimated_cost: f64,
}

// Priority queue item for task scheduling
#[derive(Clone, Debug)]
struct TaskPriority {
    task: TaskConfig,
    priority: f64, // Lower priority value means higher priority
}

impl PartialEq for TaskPriority {
    fn eq(&self, other: &Self) -> bool {
        self.priority == other.priority
    }
}

impl Eq for TaskPriority {}

impl PartialOrd for TaskPriority {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.priority.partial_cmp(&self.priority) // Reverse for min-heap
    }
}

impl Ord for TaskPriority {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

// Scheduler struct for concurrent task execution
#[derive(Clone)]
pub struct Scheduler {
    tasks: Arc<Mutex<BinaryHeap<TaskPriority>>>,
}

impl Scheduler {
    pub fn new() -> Self {
        Scheduler {
            tasks: Arc::new(Mutex::new(BinaryHeap::new())),
        }
    }

    /// Schedule tasks based on cost and latency constraints
    pub async fn schedule_tasks(
        &self,
        task_configs: Vec<TaskConfig>,
        max_latency: f64,
        max_budget: f64,
    ) -> Result<Vec<TaskConfig>, String> {
        let mut heap = BinaryHeap::new();
        let mut total_cost = 0.0;

        // Validate and prioritize tasks
        for task in task_configs {
            // Estimate latency (simplified: cost-based)
            let latency = task.estimated_cost * 10.0; // Arbitrary scaling
            if latency > max_latency {
                return Err(format!(
                    "Task {} exceeds max latency: {}s > {}s",
                    task.id, latency, max_latency
                ));
            }
            total_cost += task.estimated_cost;
            if total_cost > max_budget {
                return Err(format!(
                    "Total cost exceeds budget: ${} > ${}",
                    total_cost, max_budget
                ));
            }
            heap.push(TaskPriority {
                task: task.clone(),
                priority: task.estimated_cost, // Lower cost = higher priority
            });
        }

        // Collect prioritized tasks
        let mut prioritized_tasks = Vec::new();
        while let Some(task_priority) = heap.pop() {
            prioritized_tasks.push(task_priority.task);
        }

        Ok(prioritized_tasks)
    }

    /// Execute tasks concurrently (placeholder for async execution)
    pub async fn execute_tasks(&self, task_configs: Vec<TaskConfig>) -> Vec<(usize, String)> {
        let mut results = Vec::new();
        let tasks: Vec<_> = task_configs
            .into_iter()
            .map(|task| {
                tokio::spawn(async move {
                    // Simulate task execution (replace with actual backend calls)
                    (task.id, format!("Executed task {} on {}", task.id, task.backend))
                })
            })
            .collect();

        for task in tasks {
            if let Ok(result) = task.await {
                results.push(result);
            }
        }

        results
    }
}

// Unit tests
#[cfg(test)]
mod tests {
    use super::*;
    use tokio;

    #[tokio::test]
    async fn test_schedule_tasks_success() {
        let scheduler = Scheduler::new();
        let tasks = vec![
            TaskConfig {
                id: 0,
                r#type: "quantum".to_string(),
                backend: "cirq".to_string(),
                estimated_cost: 0.5,
            },
            TaskConfig {
                id: 1,
                r#type: "classical".to_string(),
                backend: "local".to_string(),
                estimated_cost: 0.3,
            },
        ];

        let result = scheduler.schedule_tasks(tasks.clone(), 100.0, 1.0).await;
        assert!(result.is_ok());
        let prioritized = result.unwrap();
        assert_eq!(prioritized.len(), 2);
        assert_eq!(prioritized[0].id, 1); // Lower cost (0.3) prioritized first
        assert_eq!(prioritized[1].id, 0);
    }

    #[tokio::test]
    async fn test_schedule_tasks_exceeds_latency() {
        let scheduler = Scheduler::new();
        let tasks = vec![
            TaskConfig {
                id: 0,
                r#type: "quantum".to_string(),
                backend: "cirq".to_string(),
                estimated_cost: 20.0, // Latency = 20 * 10 = 200s
            },
        ];

        let result = scheduler.schedule_tasks(tasks, 100.0, 100.0).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exceeds max latency"));
    }

    #[tokio::test]
    async fn test_schedule_tasks_exceeds_budget() {
        let scheduler = Scheduler::new();
        let tasks = vec![
            TaskConfig {
                id: 0,
                r#type: "quantum".to_string(),
                backend: "cirq".to_string(),
                estimated_cost: 1.5,
            },
        ];

        let result = scheduler.schedule_tasks(tasks, 100.0, 1.0).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exceeds budget"));
    }

    #[tokio::test]
    async fn test_execute_tasks() {
        let scheduler = Scheduler::new();
        let tasks = vec![
            TaskConfig {
                id: 0,
                r#type: "quantum".to_string(),
                backend: "cirq".to_string(),
                estimated_cost: 0.5,
            },
            TaskConfig {
                id: 1,
                r#type: "classical".to_string(),
                backend: "local".to_string(),
                estimated_cost: 0.3,
            },
        ];

        let results = scheduler.execute_tasks(tasks).await;
        assert_eq!(results.len(), 2);
        assert!(results.iter().any(|(id, _)| *id == 0));
        assert!(results.iter().any(|(id, _)| *id == 1));
    }
}
