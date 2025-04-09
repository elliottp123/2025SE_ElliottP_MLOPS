from flask import jsonify, request
from . import api
import joblib
import pandas as pd
import os
import logging
from .data_manager import DataManager 

logger = logging.getLogger(__name__)

class ModelPredictor:
    def __init__(self):
        self.models = {}
        self.load_models()
        
        # Define base features (excluding G1 and G2)
        self.base_features = [
            'school', 'sex', 'age', 'address', 'famsize', 'Pstatus',
            'Medu', 'Fedu', 'traveltime', 'studytime', 'failures',
            'schoolsup', 'famsup', 'paid', 'activities', 'nursery',
            'higher', 'internet', 'romantic', 'famrel', 'freetime',
            'goout', 'Dalc', 'Walc', 'health', 'absences',
            'Mjob_at_home', 'Mjob_health', 'Mjob_other', 'Mjob_services',
            'Mjob_teacher', 'Fjob_at_home', 'Fjob_health', 'Fjob_other',
            'Fjob_services', 'Fjob_teacher', 'reason_course', 'reason_home',
            'reason_other', 'reason_reputation', 'guardian_father',
            'guardian_mother', 'guardian_other', 'Gvg', 'Avgalc', 'Bum'
        ]
        
        # Define the exact feature order for G3 model (base + G1 + G2)
        self.g3_features = self.base_features + ['G1', 'G2']

    def load_models(self):
        """Load all models at initialization"""
        base_path = 'models'
        for subject in ['math', 'por']:
            for gender in ['male', 'female']:
                for period in ['G1', 'G2', 'G3']:
                    model_path = f"{base_path}/{subject}_{gender}_{period}_model.joblib"
                    if os.path.exists(model_path):
                        key = f"{subject}_{gender}_{period}"
                        self.models[key] = joblib.load(model_path)
                        logger.info(f"Loaded model: {key}")

    def predict(self, data):
        """Make G3 prediction using provided G1 and G2 values"""
        try:
            # Process input data
            processed_data = DataManager.process_prediction_data(data)
            
            # Get model parameters
            gender = data['gender']
            subject_key = 'math' if data['subject'] == 'mathematics' else 'por'
            
            # Extract G1 and G2 from input data (guaranteed to be present)
            g1_value = float(data['G1'])
            g2_value = float(data['G2'])
            logger.info(f"Using provided G1={g1_value} and G2={g2_value}")
            
            # Update processed data with G1 and G2 values
            processed_data['G1'] = g1_value
            processed_data['G2'] = g2_value
            
            # Update Gvg based on actual G1 and G2 values
            processed_data['Gvg'] = (g1_value + g2_value) / 2.0
            
            # Create DataFrame with exact feature order for G3 model
            g3_input = pd.DataFrame([processed_data])[self.g3_features]
            
            # Get G3 model based on subject and gender
            g3_model_key = f"{subject_key}_{gender}_G3"
            if g3_model_key not in self.models:
                raise ValueError(f"Model not found: {g3_model_key}")
                
            g3_model = self.models[g3_model_key]
            
            # Make G3 prediction
            g3_prediction = float(g3_model.predict(g3_input)[0])
            
            # Return only G3 prediction
            predictions = {
                'G3': g3_prediction
            }
            
            logger.info(f"Final G3 prediction: {g3_prediction:.2f}")
            return predictions

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Prediction error: {str(e)}")

# Initialize predictor
predictor = ModelPredictor()

@api.route('/predict', methods=['POST'])
def predict():
    """Endpoint for grade prediction"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    try:
        data = request.get_json()
        logger.info(f"Prediction request data: {data}")
        
        # Check for G1 and G2, set default values if not provided
        if 'G1' not in data or data['G1'] == '':
            data['G1'] = 0.0
            logger.info("G1 not provided, using default value")
        
        if 'G2' not in data or data['G2'] == '':
            data['G2'] = 0.0
            logger.info("G2 not provided, using default value")
        
        # Ensure G1 and G2 are float values
        try:
            data['G1'] = float(data['G1'])
            data['G2'] = float(data['G2'])
        except (ValueError, TypeError):
            return jsonify({'error': 'G1 and G2 must be valid numbers'}), 400
            
        predictions = predictor.predict(data)
        return jsonify({'predictions': predictions})
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({'error': str(e)}), 400