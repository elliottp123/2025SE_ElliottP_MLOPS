import unittest
import pandas as pd
import numpy as np
from api.predict import ModelPredictor
import os
import logging

# filepath: /workspaces/2025SE_ElliottP_MLOPS/api/test_predict.py

logging.getLogger('predict').setLevel(logging.ERROR)

class TestModelPredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create test data matching the expected format"""
        cls.test_data = {
            'school': 0,
            'sex': 1,
            'age': 0.2,
            'address': 0,
            'famsize': 0,
            'Pstatus': 0,
            'Medu': 1.0,
            'Fedu': 0.75,
            'traveltime': 0.0,
            'studytime': 0.5,
            'failures': 0.0,
            'schoolsup': 0,
            'famsup': 1,
            'paid': 1,
            'activities': 1,
            'nursery': 1,
            'higher': 1,
            'internet': 1,
            'romantic': 0,
            'famrel': 1.0,
            'freetime': 0.75,
            'goout': 0.25,
            'Dalc': 0.0,
            'Walc': 0.25,
            'health': 1.0,
            'absences': 0.5,
            'Mjob_at_home': False,
            'Mjob_health': False,
            'Mjob_other': False,
            'Mjob_services': True,
            'Mjob_teacher': False,
            'Fjob_at_home': False,
            'Fjob_health': False,
            'Fjob_other': True,
            'Fjob_services': False,
            'Fjob_teacher': False,
            'reason_course': False,
            'reason_home': False,
            'reason_other': False,
            'reason_reputation': True,
            'guardian_father': False,
            'guardian_mother': True,
            'guardian_other': False,
            'Gvg': 0.73,
            'Avgalc': 0.125,
            'Bum': 0.44,
            # Adding G1 and G2 since they're needed for G3 prediction
            'G1': 15,
            'G2': 15
        }

        cls.predictor = ModelPredictor()

    def test_model_loading(self):
        """Test that models are loaded correctly"""
        self.assertTrue(len(self.predictor.models) > 0)
        expected_models = ['math_male_G3', 'math_female_G3', 
                         'por_male_G3', 'por_female_G3']
        for model_name in expected_models:
            self.assertIn(model_name, self.predictor.models)

    def test_prediction_math_male(self):
        """Test prediction for male math student"""
        request_data = {
            **self.test_data,
            'gender': 'male',
            'subject': 'mathematics'
        }
        try:
            result = self.predictor.predict(request_data)
            self.assertIn('G3', result)
            self.assertTrue(0 <= result['G3'] <= 20)
        except Exception as e:
            self.fail(f"Prediction failed: {str(e)}")

    def test_prediction_por_female(self):
        """Test prediction for female portuguese student"""
        request_data = {
            **self.test_data,
            'gender': 'female',
            'subject': 'portuguese'
        }
        try:
            result = self.predictor.predict(request_data)
            self.assertIn('G3', result)
            self.assertTrue(0 <= result['G3'] <= 20)
        except Exception as e:
            self.fail(f"Prediction failed: {str(e)}")

    def test_missing_data(self):
        """Test handling of missing required fields"""
        incomplete_data = {
            'gender': 'male',
            'subject': 'mathematics'
        }
        with self.assertRaises(Exception):
            self.predictor.predict(incomplete_data)

    def test_invalid_gender(self):
        """Test handling of invalid gender"""
        invalid_data = {
            **self.test_data,
            'gender': 'invalid',
            'subject': 'mathematics'
        }
        with self.assertRaises(Exception):
            self.predictor.predict(invalid_data)

    def test_invalid_subject(self):
        """Test handling of invalid subject"""
        invalid_data = {
            **self.test_data,
            'gender': 'male',
            'subject': 'invalid'
        }
        with self.assertRaises(Exception):
            self.predictor.predict(invalid_data)

    def test_feature_order(self):
        """Test that feature order matches training data"""
        df = pd.DataFrame([self.test_data])
        for feature in self.predictor.feature_order:
            self.assertIn(feature, df.columns)

    def debug_prediction_pipeline(self):
        """Debug helper to print intermediate steps"""
        test_case = {
            **self.test_data,
            'gender': 'male',
            'subject': 'mathematics'
        }
        
        print("\nDEBUG: Prediction Pipeline")
        print("1. Input data shape:", len(test_case))
        
        processed_data = pd.DataFrame([test_case])
        print("2. Processed features shape:", processed_data.shape)
        print("3. Feature order length:", len(self.predictor.feature_order))
        
        model_key = "math_male_G3"
        if model_key in self.predictor.models:
            print("4. Model found:", model_key)
            try:
                prediction = self.predictor.predict(test_case)
                print("5. Prediction successful:", prediction)
            except Exception as e:
                print("5. Prediction failed:", str(e))
        else:
            print("4. Model missing:", model_key)

if __name__ == '__main__':
    # Run debug first
    print("\n=== Running Debug ===")
    test = TestModelPredictor()
    test.setUpClass()
    test.debug_prediction_pipeline()
    
    # Then run tests
    print("\n=== Running Tests ===")
    unittest.main(argv=['first-arg-is-ignored'])