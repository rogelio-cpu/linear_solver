def validate_problem_input(data):
    """
    Validates the problem input data.
    
    Args:
        data: Dictionary containing problem definition
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['objective_coefficients', 'constraint_matrix', 'rhs_values', 'constraint_signs']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
            
    try:
        c = data['objective_coefficients']
        A = data['constraint_matrix']
        b = data['rhs_values']
        signs = data['constraint_signs']
        
        if not isinstance(c, list) or not isinstance(A, list) or not isinstance(b, list) or not isinstance(signs, list):
             return False, "Fields must be lists"

        if len(A) != len(b) or len(A) != len(signs):
            return False, "Constraint dimensions mismatch"
            
        if len(A) > 0 and len(A[0]) != len(c):
             return False, "Constraint matrix columns must match objective coefficients length"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

    return True, None
