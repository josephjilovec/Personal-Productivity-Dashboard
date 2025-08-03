#[cfg(test)]
mod tests {
    use super::super::scheduler::{Scheduler, TaskConfig};
    use tokio;

    // Helper function to create sample tasks
    fn create_sample_tasks() -> Vec<TaskConfig> {
        vec![
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
            TaskConfig {
                id: 2,
                r#type: "quantum".to_string(),
                backend: "qiskit".to_string(),
                estimated_cost: 0.4,
            },
        ]
    }

    #[tokio::test]
    async fn test_schedule_tasks_ordered_by_cost() {
        let scheduler = Scheduler::new();
        let tasks = create_sample_tasks();
        let max_latency = 100.0;
        let max_budget = 2.0;

        let result = scheduler.schedule_tasks(tasks, max_latency, max_budget).await;

        assert!(result.is_ok());
        let prioritized = result.unwrap();
        assert_eq!(prioritized.len(), 3);
        // Check if tasks are ordered by cost (lowest first: 0.3, 0.4, 0.5)
        assert_eq!(prioritized[0].id, 1); // Cost 0.3
        assert_eq!(prioritized[1].id, 2); // Cost 0.4
        assert_eq!(prioritized[2].id, 0); // Cost 0.5
    }

    #[tokio::test]
    async fn test_schedule_tasks_exceeds_latency() {
        let scheduler = Scheduler::new();
        let tasks = vec![TaskConfig {
            id: 0,
            r#type: "quantum".to_string(),
            backend: "cirq".to_string(),
            estimated_cost: 20.0, // Latency = 20 * 10 = 200s
        }];
        let max_latency = 100.0;
        let max_budget = 100.0;

        let result = scheduler.schedule_tasks(tasks, max_latency, max_budget).await;

        assert!(result.is_err());
        let error = result.unwrap_err();
        assert!(error.contains("exceeds max latency"));
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
            TaskConfig {
                id: 1,
                r#type: "classical".to_string(),
                backend: "local".to_string(),
                estimated_cost: 0.6,
            },
        ];
        let max_latency = 100.0;
        let max_budget = 1.0;

        let result = scheduler.schedule_tasks(tasks, max_latency, max_budget).await;

        assert!(result.is_err());
        let error = result.unwrap_err();
        assert!(error.contains("exceeds budget"));
    }

    #[tokio::test]
    async fn test_execute_tasks_concurrently() {
        let scheduler = Scheduler::new();
        let tasks = create_sample_tasks();

        let results = scheduler.execute_tasks(tasks).await;

        assert_eq!(results.len(), 3);
        // Verify all task IDs are present
        let ids: Vec<usize> = results.iter().map(|(id, _)| *id).collect();
        assert!(ids.contains(&0));
        assert!(ids.contains(&1));
        assert!(ids.contains(&2));
        // Verify execution messages
        for (id, message) in results {
            assert!(message.contains(&format!("Executed task {}", id)));
        }
    }

    #[tokio::test]
    async fn test_execute_empty_tasks() {
        let scheduler = Scheduler::new();
        let tasks = vec![];

        let results = scheduler.execute_tasks(tasks).await;

        assert_eq!(results.len(), 0);
    }
}
