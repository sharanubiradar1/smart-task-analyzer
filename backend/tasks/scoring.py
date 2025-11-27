from datetime import date, timedelta
from typing import List, Dict, Any, Set
import math


class TaskScorer:
    """
    Intelligent task scoring system that calculates priority based on multiple factors.
    
    Design Philosophy:
    - Urgency: Tasks due sooner score higher
    - Importance: User-defined importance (1-10) heavily weighted
    - Effort: Quick wins get a boost, but not at the expense of important work
    - Dependencies: Tasks blocking others get priority boost
    """
    
    # Default weights for balanced algorithm
    DEFAULT_WEIGHTS = {
        'urgency': 0.35,
        'importance': 0.35,
        'effort': 0.15,
        'dependencies': 0.15
    }
    
    # Strategy-specific weight configurations
    STRATEGIES = {
        'smart_balance': DEFAULT_WEIGHTS,
        'fastest_wins': {
            'urgency': 0.20,
            'importance': 0.20,
            'effort': 0.50,
            'dependencies': 0.10
        },
        'high_impact': {
            'urgency': 0.15,
            'importance': 0.60,
            'effort': 0.05,
            'dependencies': 0.20
        },
        'deadline_driven': {
            'urgency': 0.60,
            'importance': 0.20,
            'effort': 0.05,
            'dependencies': 0.15
        }
    }
    
    def __init__(self, strategy: str = 'smart_balance'):
        """
        Initialize scorer with a specific strategy.
        
        Args:
            strategy: One of 'smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Invalid strategy. Choose from: {list(self.STRATEGIES.keys())}")
        self.weights = self.STRATEGIES[strategy]
        self.strategy = strategy
    
    def calculate_urgency_score(self, due_date: date) -> float:
        """
        Calculate urgency score based on due date.
        
        Logic:
        - Overdue tasks: Score increases the more overdue (max 100)
        - Due today: 95
        - Due this week: Decreasing from 90-70
        - Due this month: Decreasing from 65-40
        - Due later: Decreasing from 35-10
        
        Returns:
            Float between 0-100
        """
        today = date.today()
        days_until_due = (due_date - today).days
        
        # Overdue tasks - exponential increase in urgency
        if days_until_due < 0:
            # Cap at 100, but increase rapidly
            overdue_days = abs(days_until_due)
            return min(100, 95 + (overdue_days * 2))
        
        # Due today
        if days_until_due == 0:
            return 95
        
        # Due within a week
        if days_until_due <= 7:
            return 90 - (days_until_due * 3)
        
        # Due within a month
        if days_until_due <= 30:
            return 65 - ((days_until_due - 7) * 1.2)
        
        # Due later - asymptotic decrease
        return max(10, 35 / (1 + (days_until_due - 30) / 30))
    
    def calculate_importance_score(self, importance: int) -> float:
        """
        Convert importance (1-10) to 0-100 scale with exponential weighting.
        
        Higher importance values get exponentially more weight to emphasize
        the difference between 9 and 10 vs 1 and 2.
        
        Returns:
            Float between 0-100
        """
        # Exponential scaling to emphasize high importance
        return (importance ** 1.8) / (10 ** 1.8) * 100
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        """
        Calculate effort score - favors quick wins but not excessively.
        
        Logic:
        - Very quick tasks (< 1 hour): 90-100
        - Quick tasks (1-4 hours): 70-90
        - Medium tasks (4-8 hours): 50-70
        - Large tasks (8-16 hours): 30-50
        - Very large tasks (> 16 hours): 10-30
        
        Returns:
            Float between 0-100
        """
        if estimated_hours <= 1:
            return 100 - (estimated_hours * 10)
        elif estimated_hours <= 4:
            return 90 - ((estimated_hours - 1) * 6.67)
        elif estimated_hours <= 8:
            return 70 - ((estimated_hours - 4) * 5)
        elif estimated_hours <= 16:
            return 50 - ((estimated_hours - 8) * 2.5)
        else:
            # Asymptotic decrease for very large tasks
            return max(10, 30 - math.log(estimated_hours - 15) * 5)
    
    def calculate_dependency_score(
        self, 
        task_id: int, 
        all_tasks: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate score based on how many tasks depend on this one.
        
        Tasks that block other tasks get higher scores.
        
        Returns:
            Float between 0-100
        """
        # Count how many tasks depend on this task
        blocked_count = 0
        for task in all_tasks:
            if task_id in task.get('dependencies', []):
                blocked_count += 1
        
        # Score increases with number of blocked tasks, with diminishing returns
        if blocked_count == 0:
            return 20  # Base score even with no dependencies
        
        # Logarithmic scaling to prevent domination
        return min(100, 20 + (blocked_count * 25) - (blocked_count ** 1.5))
    
    def detect_circular_dependencies(
        self, 
        tasks: List[Dict[str, Any]]
    ) -> List[List[int]]:
        """
        Detect circular dependencies using depth-first search.
        
        Returns:
            List of cycles, where each cycle is a list of task IDs
        """
        # Build adjacency list
        graph = {}
        task_ids = set()
        
        for task in tasks:
            task_id = task.get('task_id')
            if task_id is None:
                continue
            task_ids.add(task_id)
            graph[task_id] = task.get('dependencies', [])
        
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: int, path: List[int]) -> None:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in task_ids:
                    continue
                    
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for task_id in graph:
            if task_id not in visited:
                dfs(task_id, [])
        
        return cycles
    
    def calculate_priority(
        self, 
        task: Dict[str, Any], 
        all_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive priority score for a task.
        
        Args:
            task: Task dictionary with all required fields
            all_tasks: List of all tasks (for dependency calculation)
        
        Returns:
            Dictionary with priority_score, priority_level, and explanation
        """
        # Extract task properties with defaults
        due_date = task['due_date']
        if isinstance(due_date, str):
            from datetime import datetime
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        importance = task['importance']
        estimated_hours = task['estimated_hours']
        task_id = task.get('task_id')
        
        # Calculate individual component scores
        urgency_score = self.calculate_urgency_score(due_date)
        importance_score = self.calculate_importance_score(importance)
        effort_score = self.calculate_effort_score(estimated_hours)
        dependency_score = self.calculate_dependency_score(task_id, all_tasks) if task_id else 20
        
        # Calculate weighted final score
        priority_score = (
            urgency_score * self.weights['urgency'] +
            importance_score * self.weights['importance'] +
            effort_score * self.weights['effort'] +
            dependency_score * self.weights['dependencies']
        )
        
        # Determine priority level
        if priority_score >= 80:
            priority_level = 'High'
        elif priority_score >= 60:
            priority_level = 'Medium'
        else:
            priority_level = 'Low'
        
        # Generate explanation
        explanation = self._generate_explanation(
            urgency_score, importance_score, effort_score, 
            dependency_score, due_date, estimated_hours
        )
        
        return {
            'priority_score': round(priority_score, 2),
            'priority_level': priority_level,
            'explanation': explanation,
            'component_scores': {
                'urgency': round(urgency_score, 2),
                'importance': round(importance_score, 2),
                'effort': round(effort_score, 2),
                'dependencies': round(dependency_score, 2)
            }
        }
    
    def _generate_explanation(
        self, 
        urgency: float, 
        importance: float, 
        effort: float,
        dependencies: float,
        due_date: date,
        estimated_hours: float
    ) -> str:
        """
        Generate human-readable explanation for the priority score.
        """
        explanations = []
        today = date.today()
        days_until_due = (due_date - today).days
        
        # Urgency explanation
        if days_until_due < 0:
            explanations.append(f"⚠️ OVERDUE by {abs(days_until_due)} days")
        elif days_until_due == 0:
            explanations.append("⚠️ Due TODAY")
        elif days_until_due <= 3:
            explanations.append(f"Due in {days_until_due} days")
        elif days_until_due <= 7:
            explanations.append(f"Due this week")
        
        # Importance explanation
        if importance >= 80:
            explanations.append("High importance")
        elif importance >= 60:
            explanations.append("Medium importance")
        
        # Effort explanation
        if estimated_hours <= 1:
            explanations.append("Quick win (< 1 hour)")
        elif estimated_hours <= 4:
            explanations.append(f"Short task ({estimated_hours}h)")
        
        # Dependency explanation
        if dependencies >= 70:
            explanations.append("Blocks multiple tasks")
        elif dependencies >= 45:
            explanations.append("Blocks other tasks")
        
        return " | ".join(explanations) if explanations else "Standard priority task"
    
    def score_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score and sort all tasks by priority.
        
        Args:
            tasks: List of task dictionaries
        
        Returns:
            Sorted list of tasks with priority scores
        """
        scored_tasks = []
        
        for task in tasks:
            score_data = self.calculate_priority(task, tasks)
            
            # Merge task data with score data
            scored_task = {
                **task,
                **score_data
            }
            scored_tasks.append(scored_task)
        
        # Sort by priority score (descending)
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return scored_tasks
    
    def get_top_suggestions(
        self, 
        tasks: List[Dict[str, Any]], 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get top task suggestions with detailed reasoning.
        
        Args:
            tasks: List of task dictionaries
            limit: Number of suggestions to return
        
        Returns:
            List of top suggested tasks with action items
        """
        scored_tasks = self.score_tasks(tasks)
        top_tasks = scored_tasks[:limit]
        
        suggestions = []
        for i, task in enumerate(top_tasks, 1):
            action_items = self._generate_action_items(task, i)
            
            suggestions.append({
                'task_id': task.get('task_id'),
                'title': task['title'],
                'due_date': task['due_date'],
                'estimated_hours': task['estimated_hours'],
                'importance': task['importance'],
                'priority_score': task['priority_score'],
                'reason': task['explanation'],
                'action_items': action_items
            })
        
        return suggestions
    
    def _generate_action_items(self, task: Dict[str, Any], rank: int) -> List[str]:
        """Generate actionable items for a suggested task."""
        items = []
        
        if rank == 1:
            items.append("🎯 Start this task immediately")
        else:
            items.append(f"📋 Schedule this as task #{rank} today")
        
        if task['estimated_hours'] <= 1:
            items.append("⚡ Quick win - can complete in one sitting")
        elif task['estimated_hours'] <= 4:
            items.append("🕐 Block time in your calendar")
        else:
            items.append("📅 Break down into smaller subtasks")
        
        days_until_due = (task['due_date'] - date.today()).days
        if days_until_due < 0:
            items.append("🚨 Communicate delay or adjust scope")
        elif days_until_due <= 1:
            items.append("⏰ Must complete today")
        
        if task.get('component_scores', {}).get('dependencies', 0) >= 70:
            items.append("🔓 Completing this will unblock other tasks")
        
        return items