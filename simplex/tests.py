from django.test import TestCase, Client
import json
from django.urls import reverse

class SimplexTests(TestCase):
    def test_solve_view(self):
        client = Client()
        url = reverse('solve')
        data = {
            "objective_coefficients": [3, 5],
            "constraint_matrix": [[1, 0], [0, 2], [3, 2]],
            "rhs_values": [4, 12, 18],
            "constraint_signs": ["<=", "<=", "<="],
            "maximize": True
        }
        response = client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'optimal')
        self.assertAlmostEqual(json_response['objective_value'], 36.0, places=2)
        # Check variables. x1=2, x2=6
        # Note: variables list order depends on input order
        vars = json_response['variables']
        self.assertAlmostEqual(vars[0], 2.0, places=2)
        self.assertAlmostEqual(vars[1], 6.0, places=2)

    def test_user_problem(self):
        client = Client()
        url = reverse('solve')
        data = {
            "objective_coefficients": [3, 4],
            "constraint_matrix": [[1, 7], [7, 1]],
            "rhs_values": [1200, 1000],
            "constraint_signs": ["<=", "<="],
            "maximize": True
        }
        response = client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'optimal')
        
        # Expected optimal: x1 ≈ 120.83, x2 ≈ 154.17, Z ≈ 979.17
        self.assertAlmostEqual(json_response['objective_value'], 979.1667, places=2)
        vars = json_response['variables']
        self.assertAlmostEqual(vars[0], 120.8333, places=2)
        self.assertAlmostEqual(vars[1], 154.1667, places=2)

    def test_phase1_problem(self):
        client = Client()
        url = reverse('solve')
        data = {
            "objective_coefficients": [2, 3],
            "constraint_matrix": [[1, 1], [1, 2]],
            "rhs_values": [5, 6],
            "constraint_signs": [">=", ">="],
            "maximize": False # Minimize
        }
        response = client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'optimal')
        
        # Expected optimal: x1=4, x2=1, Z=11
        self.assertAlmostEqual(json_response['objective_value'], 11.0, places=2)
        vars = json_response['variables']
        self.assertAlmostEqual(vars[0], 4.0, places=2)
        self.assertAlmostEqual(vars[1], 1.0, places=2)
