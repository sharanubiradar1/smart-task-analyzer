from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer


class TaskScorerTests(TestCase):
    """Test suite for TaskScorer algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = TaskScorer(strategy='smart_balance')
        self.today = date.today()
    
    def test_urgency_score_overdue_task(self):
        """Test that overdue tasks get very high urgency scores."""
        overdue_date = self.today - timedelta(days=5)
        score = self.scorer.calculate_urgency_score(overdue_date)
        
        self.assertGreater(score, 95, "Overdue tasks should score > 95")
        self.assertLessEqual(score, 100, "Score should not exceed 100")
    
    def test_urgency_score_due_today(self):
        """Test that tasks due today get appropriately high scores."""
        score = self.scorer.calculate_urgency_score(self.today)
        
        self.assertEqual(score, 95, "Tasks due today should score exactly 95")
    
    def test_urgency_score_future_task(self):
        """Test that future tasks get lower urgency scores."""
        future_date = self.today + timedelta(days=30)
        score = self.scorer.calculate_urgency_score(future_date)
        
        self.assertLess(score, 70, "Tasks due in 30 days should score < 70")
        self.assertGreater(score, 0, "Score should be positive")
    
    def test_importance_score_scaling(self):
        """Test that importance scores scale exponentially."""
        low_importance = self.scorer.calculate_importance_score(2)
        mid_importance = self.scorer.calculate_importance_score(5)
        high_importance = self.scorer.calculate_importance_score(10)
        
        self.assertLess(low_importance, 20, "Low importance should score < 20")
        self.assertGreater(high_importance, 90, "Max importance should score > 90")
        self.assertGreater(
            high_importance - mid_importance,
            mid_importance - low_importance,
            "Score difference should increase exponentially"
        )
    
    def test_effort_score_quick_wins(self):
        """Test that quick tasks get higher effort scores."""
        quick_task = self.scorer.calculate_effort_score(0.5)
        long_task = self.scorer.calculate_effort_score(20)
        
        self.assertGreater(quick_task, 90, "Quick tasks should score > 90")
        self.assertLess(long_task, 30, "Long tasks should score < 30")
    
    def test_dependency_score_blocking_tasks(self):
        """Test that tasks blocking others get higher dependency scores."""
        tasks = [
            {'task_id': 1, 'dependencies': []},
            {'task_id': 2, 'dependencies': [1]},
            {'task_id': 3, 'dependencies': [1]},
            {'task_id': 4, 'dependencies': [1]},
        ]
        
        # Task 1 blocks 3 other tasks
        score = self.scorer.calculate_dependency_score(1, tasks)
        self.assertGreater(score, 60, "Task blocking 3 others should score > 60")
        
        # Task 2 blocks no tasks
        score_no_deps = self.scorer.calculate_dependency_score(2, tasks)
        self.assertEqual(score_no_deps, 20, "Task with no dependents should score 20")
    
    def test_circular_dependency_detection_simple(self):
        """Test detection of simple circular dependencies."""
        tasks = [
            {'task_id': 1, 'dependencies': [2]},
            {'task_id': 2, 'dependencies': [1]},
        ]
        
        cycles = self.scorer.detect_circular_dependencies(tasks)
        
        self.assertTrue(len(cycles) > 0, "Should detect circular dependency")
    
    def test_circular_dependency_detection_complex(self):
        """Test detection of complex circular dependencies."""
        tasks = [
            {'task_id': 1, 'dependencies': [2]},
            {'task_id': 2, 'dependencies': [3]},
            {'task_id': 3, 'dependencies': [1]},
        ]
        
        cycles = self.scorer.detect_circular_dependencies(tasks)
        
        self.assertTrue(len(cycles) > 0, "Should detect complex cycle")
    
    def test_no_circular_dependency(self):
        """Test that valid dependency chains don't trigger false positives."""
        tasks = [
            {'task_id': 1, 'dependencies': []},
            {'task_id': 2, 'dependencies': [1]},
            {'task_id': 3, 'dependencies': [2]},
        ]
        
        cycles = self.scorer.detect_circular_dependencies(tasks)
        
        self.assertEqual(len(cycles), 0, "Valid chain should not have cycles")
    
    def test_priority_calculation_complete(self):
        """Test complete priority calculation."""
        task = {
            'task_id': 1,
            'title': 'Fix critical bug',
            'due_date': self.today + timedelta(days=1),
            'estimated_hours': 2,
            'importance': 9,
            'dependencies': []
        }
        
        all_tasks = [task]
        result = self.scorer.calculate_priority(task, all_tasks)
        
        self.assertIn('priority_score', result)
        self.assertIn('priority_level', result)
        self.assertIn('explanation', result)
        self.assertIn('component_scores', result)
        
        self.assertGreaterEqual(result['priority_score'], 0)
        self.assertLessEqual(result['priority_score'], 100)
        self.assertIn(result['priority_level'], ['Low', 'Medium', 'High'])
    
    def test_strategy_fastest_wins(self):
        """Test that 'fastest_wins' strategy prioritizes low-effort tasks."""
        quick_task = {
            'task_id': 1,
            'title': 'Quick task',
            'due_date': self.today + timedelta(days=30),
            'estimated_hours': 0.5,
            'importance': 3,
            'dependencies': []
        }
        
        long_task = {
            'task_id': 2,
            'title': 'Long task',
            'due_date': self.today + timedelta(days=30),
            'estimated_hours': 20,
            'importance': 3,
            'dependencies': []
        }
        
        scorer_fast = TaskScorer(strategy='fastest_wins')
        tasks = [quick_task, long_task]
        
        result_quick = scorer_fast.calculate_priority(quick_task, tasks)
        result_long = scorer_fast.calculate_priority(long_task, tasks)
        
        self.assertGreater(
            result_quick['priority_score'],
            result_long['priority_score'],
            "Fastest wins should prioritize quick tasks"
        )
    
    def test_strategy_high_impact(self):
        """Test that 'high_impact' strategy prioritizes important tasks."""
        important_task = {
            'task_id': 1,
            'title': 'Important task',
            'due_date': self.today + timedelta(days=30),
            'estimated_hours': 10,
            'importance': 10,
            'dependencies': []
        }
        
        unimportant_task = {
            'task_id': 2,
            'title': 'Unimportant task',
            'due_date': self.today + timedelta(days=1),
            'estimated_hours': 1,
            'importance': 2,
            'dependencies': []
        }
        
        scorer_impact = TaskScorer(strategy='high_impact')
        tasks = [important_task, unimportant_task]
        
        result_important = scorer_impact.calculate_priority(important_task, tasks)
        result_unimportant = scorer_impact.calculate_priority(unimportant_task, tasks)
        
        self.assertGreater(
            result_important['priority_score'],
            result_unimportant['priority_score'],
            "High impact should prioritize important tasks"
        )
    
    def test_score_tasks_sorting(self):
        """Test that score_tasks properly sorts tasks."""
        tasks = [
            {
                'task_id': 1,
                'title': 'Low priority',
                'due_date': self.today + timedelta(days=30),
                'estimated_hours': 20,
                'importance': 2,
                'dependencies': []
            },
            {
                'task_id': 2,
                'title': 'High priority',
                'due_date': self.today,
                'estimated_hours': 1,
                'importance': 10,
                'dependencies': []
            },
        ]
        
        sorted_tasks = self.scorer.score_tasks(tasks)
        
        self.assertEqual(sorted_tasks[0]['title'], 'High priority')
        self.assertEqual(sorted_tasks[1]['title'], 'Low priority')
        self.assertGreater(
            sorted_tasks[0]['priority_score'],
            sorted_tasks[1]['priority_score']
        )
    
    def test_get_top_suggestions(self):
        """Test getting top task suggestions."""
        tasks = [
            {
                'task_id': i,
                'title': f'Task {i}',
                'due_date': self.today + timedelta(days=i),
                'estimated_hours': i,
                'importance': 10 - i,
                'dependencies': []
            }
            for i in range(1, 6)
        ]
        
        suggestions = self.scorer.get_top_suggestions(tasks, limit=3)
        
        self.assertEqual(len(suggestions), 3)
        self.assertIn('reason', suggestions[0])
        self.assertIn('action_items', suggestions[0])
        self.assertTrue(len(suggestions[0]['action_items']) > 0)