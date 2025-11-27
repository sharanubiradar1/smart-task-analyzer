from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    TaskInputSerializer, 
    TaskOutputSerializer, 
    SuggestedTaskSerializer
)
from .scoring import TaskScorer
from datetime import datetime


@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and sort tasks by priority score.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance" // optional
    }
    
    Returns:
        Sorted list of tasks with priority scores
    """
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart_balance')
    
    if not tasks_data:
        return Response(
            {'error': 'No tasks provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate input tasks
    validated_tasks = []
    errors = []
    
    for i, task_data in enumerate(tasks_data):
        serializer = TaskInputSerializer(data=task_data)
        if serializer.is_valid():
            validated_tasks.append(serializer.validated_data)
        else:
            errors.append({
                'task_index': i,
                'errors': serializer.errors
            })
    
    if errors:
        return Response(
            {
                'error': 'Invalid task data',
                'details': errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for circular dependencies
    try:
        scorer = TaskScorer(strategy=strategy)
        
        # Detect circular dependencies
        cycles = scorer.detect_circular_dependencies(validated_tasks)
        if cycles:
            return Response(
                {
                    'error': 'Circular dependencies detected',
                    'cycles': cycles,
                    'message': 'Please remove circular dependencies before analyzing tasks'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Score and sort tasks
        scored_tasks = scorer.score_tasks(validated_tasks)
        
        # Serialize output
        output_serializer = TaskOutputSerializer(scored_tasks, many=True)
        
        return Response({
            'tasks': output_serializer.data,
            'strategy': strategy,
            'total_tasks': len(scored_tasks)
        })
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def suggest_tasks(request):
    """
    Get top 3 suggested tasks to work on today.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance", // optional
        "limit": 3 // optional
    }
    
    Returns:
        Top suggested tasks with detailed explanations
    """
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart_balance')
    limit = request.data.get('limit', 3)
    
    if not tasks_data:
        return Response(
            {'error': 'No tasks provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate input tasks
    validated_tasks = []
    for task_data in tasks_data:
        serializer = TaskInputSerializer(data=task_data)
        if serializer.is_valid():
            validated_tasks.append(serializer.validated_data)
        else:
            return Response(
                {'error': 'Invalid task data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        scorer = TaskScorer(strategy=strategy)
        
        # Check for circular dependencies
        cycles = scorer.detect_circular_dependencies(validated_tasks)
        if cycles:
            return Response(
                {
                    'error': 'Circular dependencies detected',
                    'cycles': cycles
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get suggestions
        suggestions = scorer.get_top_suggestions(validated_tasks, limit=limit)
        
        # Serialize output
        output_serializer = SuggestedTaskSerializer(suggestions, many=True)
        
        return Response({
            'suggestions': output_serializer.data,
            'strategy': strategy,
            'generated_at': datetime.now().isoformat()
        })
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )