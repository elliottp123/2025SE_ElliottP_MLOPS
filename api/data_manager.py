import re
import logging
from datetime import datetime
import bcrypt
import pandas as pd
import os
from flask import request, jsonify
import logging
from . import api  # Import the api Blueprint

logger = logging.getLogger(__name__)

class DataManager:
    # Define constants for data validation and normalization
    NUMERIC_RANGES = {
        'age': (15, 22),
        'Medu': (0, 4),
        'Fedu': (0, 4),
        'traveltime': (1, 4),
        'studytime': (1, 4),
        'failures': (0, 4),
        'famrel': (1, 5),
        'freetime': (1, 5),
        'goout': (1, 5),
        'Dalc': (1, 5),
        'Walc': (1, 5),
        'health': (1, 5),
        'absences': (0, 93)
    }

    BINARY_FIELDS = [
        'schoolsup', 'famsup', 'paid', 'activities', 'nursery',
        'higher', 'internet', 'romantic'
    ]

    ONE_HOT_FIELDS = {
        'Mjob': ['at_home', 'health', 'other', 'services', 'teacher'],
        'Fjob': ['at_home', 'health', 'other', 'services', 'teacher'],
        'reason': ['course', 'home', 'other', 'reputation'],
        'guardian': ['father', 'mother', 'other']
    }

    EXPECTED_COLUMNS = [
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

    @staticmethod
    def normalize_value(value, min_val, max_val):
        """Normalize a value to range [0,1]"""
        return (float(value) - min_val) / (max_val - min_val)

    @staticmethod
    def process_prediction_data(data):
        """Process and validate all prediction data"""
        processed = {}
        
        # Handle basic fields
        processed['school'] = int(data.get('school', 0))
        processed['sex'] = int(data.get('gender') == 'male')
        processed['address'] = int(data.get('address', 0))
        processed['famsize'] = int(data.get('famsize', 0))
        processed['Pstatus'] = int(data.get('Pstatus', 0))
        
        # Normalize numeric fields
        for field, (min_val, max_val) in DataManager.NUMERIC_RANGES.items():
            value = float(data.get(field, min_val))
            processed[field] = DataManager.normalize_value(value, min_val, max_val)
        
        # Process binary fields
        for field in DataManager.BINARY_FIELDS:
            processed[field] = int(data.get(field) in ['yes', '1', True])
        
        # Process one-hot encoded fields
        for field, options in DataManager.ONE_HOT_FIELDS.items():
            selected = data.get(field)
            for option in options:
                processed[f'{field}_{option}'] = int(selected == option)
        
        # Calculate engineered features
        processed['Avgalc'] = (processed['Dalc'] + processed['Walc']) / 2.0
        processed['Bum'] = (
            2.0 * processed['failures'] +
            1.5 * processed['absences'] +
            processed['Dalc'] +
            processed['Walc'] +
            (1.0 - processed['studytime']) +
            0.5 * processed['freetime']
        ) / 6.0
        
        # Initialize grades and averages
        processed['G1'] = float(data.get('G1', 0))
        processed['G2'] = float(data.get('G2', 0))
        processed['Gvg'] = (processed['G1'] + processed['G2']) / 2.0 if 'G1' in data and 'G2' in data else 0.0
        
        return processed

    @staticmethod
    def sanitize_repository_url(url):
        if not url:
            return None
        url = url.strip()
        url_pattern = r'^https?:\/\/(github\.com|gitlab\.com|bitbucket\.org)\/[\w\-\.\/]+'
        if not re.match(url_pattern, url):
            raise ValueError("URL must be a valid repository URL")
        return url

    @staticmethod
    def validate_timestamps(start_time, end_time):
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            if end <= start:
                raise ValueError("end time must be after start time")
            return start, end
        except ValueError as e:
            raise ValueError(f"invalid timestamp format: {str(e)}")

    @staticmethod
    def calculate_time_worked(start_time, end_time):
        diff_minutes = (end_time - start_time).total_seconds() / 60
        return round(diff_minutes / 15) * 15

    @staticmethod
    def sanitize_email(email):
        if not email or not isinstance(email, str):
            raise ValueError("Invalid email format")
        email = email.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        return email

    @staticmethod
    def sanitize_developer_tag(developer_tag):
        return developer_tag.strip().lower()

    @staticmethod
    def sanitize_project(project):
        if not project or not isinstance(project, str):
            raise ValueError("Invalid project name")
        project = project.strip()
        if len(project) > 100:
            raise ValueError("Project name must be less than 100 characters")
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\s_-]*$', project):
            raise ValueError("Project name must start with alphanumeric and contain only letters, numbers, spaces, underscores, or hyphens")
        return project[:100]

    @staticmethod
    def sanitize_content(content):
        if not content or not isinstance(content, str):
            raise ValueError("Content cannot be empty")
        content = content.strip()
        if len(content) > 10000:
            raise ValueError("Content exceeds maximum length of 10000 characters")
        return content

    @staticmethod
    def sanitize_search_params(params):
        clean_params = {}
        if 'project' in params:
            clean_params['project'] = DataManager.sanitize_project(params['project'])
        if 'developer_tag' in params:
            clean_params['developer_tag'] = DataManager.sanitize_developer_tag(params['developer_tag'])
        if 'date' in params:
            try:
                datetime.strptime(params['date'], '%Y-%m-%d')
                clean_params['date'] = params['date']
            except ValueError:
                raise ValueError("Invalid date format")
        return clean_params

    @staticmethod
    def validate_password(password):
        if len(password) < 7:
            raise ValueError("Password must be at least 7 characters long")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() or not c.isalnum() for c in password):
            raise ValueError("Password must contain at least one number or special character")
        return password.encode('utf-8')

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(DataManager.validate_password(password), salt)

    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.checkpw(DataManager.validate_password(password), hashed)

    @staticmethod
    def save_feedback_data(data):
        """Save new training data to feedback CSV"""
        try:
            # Ensure all required columns are present
            required_columns = DataManager.EXPECTED_COLUMNS + ['G1', 'G2', 'G3']
            
            # Process the input data
            processed_data = DataManager.process_prediction_data(data)
            
            # Add G1, G2, G3 values
            processed_data['G1'] = float(data.get('G1', 0))
            processed_data['G2'] = float(data.get('G2', 0))
            processed_data['G3'] = float(data.get('G3', 0))
            
            # Create DataFrame with single row
            df_new = pd.DataFrame([processed_data])
            
            # Ensure all columns match training data format
            for col in required_columns:
                if col not in df_new.columns:
                    df_new[col] = 0
            
            # Reorder columns to match training data
            df_new = df_new[required_columns]
            
            # Create feedback_data directory if it doesn't exist
            os.makedirs('feedback_data', exist_ok=True)
            
            # Append to existing file or create new one
            feedback_file = 'feedback_data/feedback_data.csv'
            if os.path.exists(feedback_file):
                df_new.to_csv(feedback_file, mode='a', header=False, index=False)
            else:
                df_new.to_csv(feedback_file, index=False)
                
            return True
        except Exception as e:
            logging.error(f"Error saving feedback data: {str(e)}")
            raise ValueError(f"Failed to save feedback data: {str(e)}")
    
    @staticmethod
    @api.route('/new-data', methods=['POST'])
    def handle_new_data():
        """Handle new training data submission endpoint"""
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json()
            logger.info(f"New data submission: {data}")
            
            # Validate required fields
            required_fields = ['G1', 'G2', 'G3']
            for field in required_fields:
                if field not in data or not isinstance(data.get(field), (int, float)):
                    return jsonify({'error': f'Missing or invalid {field} value'}), 400
            
            # Save the data using existing method
            success = DataManager.save_feedback_data(data)
            
            if success:
                return jsonify({'message': 'Data saved successfully'})
            else:
                raise ValueError('Failed to save data')
                
        except Exception as e:
            logger.error(f"New data submission failed: {str(e)}")
            return jsonify({'error': str(e)}), 400
