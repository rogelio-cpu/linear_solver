"""
Django views for the linear programming solver.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np

from .solvers.two_phase_solver import TwoPhaseSolver
from .utils.validators import validate_problem_input
from .utils.formatters import format_solution_response

@csrf_exempt
def solve_problem(request):
    """API endpoint to solve linear programming problem."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate input
            is_valid, error = validate_problem_input(data)
            if not is_valid:
                return JsonResponse({'error': error}, status=400)
            
            # Extract problem parameters
            c = np.array(data['objective_coefficients'])
            A = np.array(data['constraint_matrix'])
            b = np.array(data['rhs_values'])
            signs = data['constraint_signs']
            maximize = data.get('maximize', True)
            
            # Solve using Two-Phase Simplex
            solver = TwoPhaseSolver(maximize=maximize)
            result = solver.solve(c, A, b, signs)
            
            # Format response
            response = format_solution_response(result)
            
            return JsonResponse(response)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def index(request):
    """Render the main interface."""
    return render(request, 'simplex/index.html')