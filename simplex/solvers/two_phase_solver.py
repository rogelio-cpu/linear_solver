import numpy as np

class TwoPhaseSolver:
    def __init__(self, maximize=True):
        self.maximize = maximize
        self.iterations = []

    def solve(self, c, A, b, signs):
        """
        Solves the linear programming problem using the Two-Phase Simplex method.
        """
        try:
            self.iterations = []
            
            # 1. Standardize the problem
            # Convert Max Z to Min -Z if necessary
            # We will solve for Min Z' internally. If original was Max Z, Z = -Z'
            
            c = np.array(c, dtype=float)
            A = np.array(A, dtype=float)
            b = np.array(b, dtype=float)
            
            if self.maximize:
                c = -c  # Minimize -Z
            
            num_vars_original = len(c)
            num_constraints = len(b)
            
            # Add Slack, Surplus, and Artificial variables
            # We need to construct the initial tableau for Phase 1 (or direct Phase 2 if possible)
            
            # Identify types of constraints
            # <= : Add slack (+s)
            # >= : Substract surplus (-e), Add artificial (+a)
            # =  : Add artificial (+a)
            
            A_aug = A.copy()
            c_phase1 = np.zeros(num_vars_original) # Phase 1 objective: Minimize sum(artificials)
            
            # Track variable indices
            # 0..n-1: Original
            # n.. : Slack/Surplus/Artificial
            
            slack_surplus_indices = []
            artificial_indices = []
            basis_indices = [] # Indices of variables in the basis for each row
            
            current_col_idx = num_vars_original
            
            for i in range(num_constraints):
                sign = signs[i]
                
                if sign == '<=':
                    # Add slack +s
                    col = np.zeros((num_constraints, 1))
                    col[i] = 1
                    A_aug = np.hstack((A_aug, col))
                    c_phase1 = np.append(c_phase1, 0)
                    basis_indices.append(current_col_idx)
                    slack_surplus_indices.append(current_col_idx)
                    current_col_idx += 1
                    
                elif sign == '>=':
                    # Subtract surplus -e
                    col_s = np.zeros((num_constraints, 1))
                    col_s[i] = -1
                    A_aug = np.hstack((A_aug, col_s))
                    c_phase1 = np.append(c_phase1, 0)
                    slack_surplus_indices.append(current_col_idx)
                    current_col_idx += 1
                    
                    # Add artificial +a
                    col_a = np.zeros((num_constraints, 1))
                    col_a[i] = 1
                    A_aug = np.hstack((A_aug, col_a))
                    c_phase1 = np.append(c_phase1, 1) # Cost of 1 in Phase 1
                    basis_indices.append(current_col_idx)
                    artificial_indices.append(current_col_idx)
                    current_col_idx += 1
                    
                elif sign == '=':
                    # Add artificial +a
                    col_a = np.zeros((num_constraints, 1))
                    col_a[i] = 1
                    A_aug = np.hstack((A_aug, col_a))
                    c_phase1 = np.append(c_phase1, 1) # Cost of 1 in Phase 1
                    basis_indices.append(current_col_idx)
                    artificial_indices.append(current_col_idx)
                    current_col_idx += 1

            # Check if Phase 1 is needed
            if not artificial_indices:
                # Direct Phase 2
                # Augment c with 0s for slacks
                c_aug = np.concatenate((c, np.zeros(len(slack_surplus_indices))))
                status, tableau, basis, obj_val = self._simplex_algorithm(A_aug, b, c_aug, basis_indices, phase=2)
            else:
                # ** Phase 1 **
                # Objective: Minimize sum(Artificials) -> Min W = 1*a1 + 1*a2 ...
                # We need to express W in terms of non-basic variables using the initial basis equations.
                
                # In the initial tableau for Phase 1, the costs are 1 for artificials, 0 for others.
                # However, basic variables must have 0 coefficient in the objective row of the tableau.
                # Currently, artificials are basic but have cost 1.
                # We must subtract rows corresponding to artificial variables from the objective row
                # to make their reduced costs 0.
                
                # Construct Initial Tableau for Phase 1
                # Dimensions: (num_constraints + 1) x (num_total_vars + 1)
                # Last column is RHS
                # Last row is Reduced Costs (Z_j - C_j)
                
                # For Phase 1 calculation specifically:
                # Z_phase1 = sum(artificials)
                # We want Minimize Z_phase1.
                # Reduced cost row initially: c_phase1 (1 for art, 0 else)
                # Corrected reduced cost = c_phase1 - sum(rows where basis is artificial)
                
                status, tableau, basis, obj_val = self._simplex_algorithm(A_aug, b, c_phase1, basis_indices, phase=1)
                
                if status != 'optimal':
                    return self._format_result(status, 0, [], "Phase 1 failed")
                
                if obj_val > 1e-9: # If Min W > 0
                    return self._format_result('infeasible', 0, [], "Problem is infeasible (Phase 1 objective > 0)")
                
                # Prepare for Phase 2
                # Remove artificial columns from A_aug and tableau?
                # Usually we just ignore them or drop them. 
                # If an artificial variable is still in basis at level 0, it's a degenerate case, 
                # but we can technically keep it or pivot it out. For simplicity, we drop artificial columns.
                
                # Drop artificial columns
                non_artificial_mask = np.ones(A_aug.shape[1], dtype=bool)
                non_artificial_mask[artificial_indices] = False
                
                A_phase2 = tableau[:-1, :-1][:, non_artificial_mask] # Take from current tableau
                b_phase2 = tableau[:-1, -1] # Current RHS
                
                # Original C augmented with 0s for slacks/surplus
                c_aug = np.concatenate((c, np.zeros(len(slack_surplus_indices))))
                
                # We need to map the old basis indices to new indices (shifting left if we removed cols)
                # This is tricky. Easiest might be to keep artificials but force their cost to 0 (or huge M) 
                # and ensure they don't re-enter. 
                # Let's just create c_phase2 identifying the correct columns.
                
                c_phase2 = np.zeros(A_aug.shape[1])
                c_phase2[:num_vars_original] = c
                # Slacks/surplus are 0
                # Artificials - don't care, but set to 0 to be safe or High if we kept them
                
                # Recalculate reduced costs for Phase 2 based on current basis
                status, tableau, basis, obj_val = self._simplex_algorithm(A_aug, b_phase2, c_phase2, basis, phase=2, initial_tableau=tableau[:-1, :])

            # Extract solution
            if status == 'optimal':
                solution = np.zeros(A_aug.shape[1])
                for r, var_idx in enumerate(basis):
                    solution[var_idx] = tableau[r, -1]
                
                final_vars = solution[:num_vars_original]
                
                final_obj = obj_val
                if self.maximize:
                    final_obj = -final_obj # Revert sign
                    
                return self._format_result('optimal', final_obj, final_vars.tolist(), "Optimal solution found")
            
            return self._format_result(status, 0, [], f"Solver finished with status: {status}")

        except Exception as e:
            return self._format_result('error', 0, [], str(e))

    def _simplex_algorithm(self, A, b, c, basis_indices, phase, initial_tableau=None):
        """
        Runs the Simplex iterations.
        Minimizes z = c^T x
        """
        
        m, n = A.shape
        
        # Build Tableau
        # Row 0..m-1: [ A  | b ]
        # Row m     : [ rc | -obj ] (Reduced costs)
        
        tableau = np.zeros((m + 1, n + 1))
        
        if initial_tableau is not None:
            tableau[:m, :] = list(initial_tableau) # Copy A and b part
            tableau[:m, -1] = b # Ensure b is update-to-date
        else:
            tableau[:m, :n] = A
            tableau[:m, n] = b
        
        # Calculate initial reduced costs: rc = c - cb * B^-1 * A
        # Since we have the tableau (which is B^-1 A), rc = c - cb * Tableau_rows
        # cb is vector of costs of basic variables
        
        cb = np.array([c[i] for i in basis_indices])
        
        # specific calculation for reduced costs row
        # z_j - c_j in some conventions, here we want to Minimize, so we look for C_j - Z_j < 0 ??
        
        # Let's stick to: Minimize Z.
        # Reduced cost r_j = c_j - z_j = c_j - cb * col_j
        # If any r_j < 0, we can improve (descend).
        
        for j in range(n):
            z_j = np.dot(cb, tableau[:m, j])
            tableau[m, j] = c[j] - z_j
            
        # Objective value z = cb * b
        tableau[m, n] = -np.dot(cb, tableau[:m, n])
        
        self.iterations.append({
            'phase': phase,
            'tableau': tableau.tolist(),
            'basis': list(basis_indices),
            'obj': -tableau[m, n]
        })

        # Iterations
        MAX_ITER = 100
        for it in range(MAX_ITER):
            # Check for optimality
            # For Minimization: All reduced costs (row m) must be >= 0 (allow small tolerance)
            if np.all(tableau[m, :n] >= -1e-9):
                return 'optimal', tableau, basis_indices, -tableau[m, n]
            
            # Select entering variable (most negative reduced cost)
            entering_col = np.argmin(tableau[m, :n])
            
            # Check for unboundedness
            # If entering column <= 0 (all entries), then unbounded
            col_vals = tableau[:m, entering_col]
            if np.all(col_vals <= 1e-9):
                return 'unbounded', tableau, basis_indices, -tableau[m, n]
            
            # Ratio test
            ratios = []
            for i in range(m):
                if col_vals[i] > 1e-9:
                    ratios.append(tableau[i, n] / col_vals[i])
                else:
                    ratios.append(np.inf)
            
            if np.all(np.array(ratios) == np.inf):
                 return 'unbounded', tableau, basis_indices, -tableau[m, n]

            leaving_row = np.argmin(ratios)
            
            # Pivot
            pivot_val = tableau[leaving_row, entering_col]
            tableau[leaving_row, :] /= pivot_val
            
            for i in range(m + 1):
                if i != leaving_row:
                    factor = tableau[i, entering_col]
                    tableau[i, :] -= factor * tableau[leaving_row, :]
            
            # Update Basis
            basis_indices[leaving_row] = entering_col
            
            self.iterations.append({
                'phase': phase,
                'iter': it + 1,
                'entering': int(entering_col),
                'leaving_row': int(leaving_row),
                'tableau': tableau.tolist(),
                'obj': -tableau[m, n]
            })
            
        return 'max_iter_reached', tableau, basis_indices, -tableau[m, n]

    def _format_result(self, status, obj_value, variables, message):
        return {
            'status': status,
            'objective_value': round(obj_value, 4),
            'variables': [round(v, 4) for v in variables],
            'message': message,
            'iterations': self.iterations
        }
