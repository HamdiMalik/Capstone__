import base64
import io
import numpy as np
from PIL import Image, ImageOps
import os
import random

def analyze_skin_image(image_data):
    """
    Analyze skin image using AI model
    For now, this returns mock data. Replace with actual AI model integration.
    """
    try:
        # For production, implement actual AI model loading and prediction
        # from tensorflow.keras.models import load_model
        # model = load_model('path/to/your/model.h5')
        
        # Mock analysis result
        conditions = [
            'Benign Mole',
            'Normal Skin',
            'Freckle', 
            'Age Spot',
            'Seborrheic Keratosis',
            'Actinic Keratosis',
            'Dermatofibroma'
        ]
        
        recommendations_map = {
            'Benign Mole': [
                'Monitor for changes in size, shape, or color',
                'Annual dermatologist check-up recommended',
                'Protect from sun exposure'
            ],
            'Normal Skin': [
                'Continue regular self-examinations',
                'Use sunscreen daily',
                'Maintain healthy skincare routine'
            ],
            'Freckle': [
                'Protect from sun exposure',
                'Monthly self-check recommended',
                'No immediate action needed'
            ],
            'Age Spot': [
                'No immediate action needed',
                'Regular dermatologist visits recommended',
                'Use sunscreen to prevent new spots'
            ],
            'Seborrheic Keratosis': [
                'Schedule dermatologist appointment for confirmation',
                'Monitor for growth or changes',
                'Usually benign but should be examined'
            ],
            'Actinic Keratosis': [
                'Schedule dermatologist appointment immediately',
                'Avoid sun exposure',
                'May require treatment to prevent progression'
            ],
            'Dermatofibroma': [
                'Generally benign, monitor for changes',
                'Consult dermatologist if concerned',
                'No urgent treatment typically needed'
            ]
        }
        
        # Random selection for demo (replace with actual AI prediction)
        condition = random.choice(conditions)
        confidence = random.uniform(0.75, 0.95)
        recommendations = recommendations_map.get(condition, ['Consult a dermatologist'])
        
        return {
            'condition': condition,
            'confidence': confidence,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        # Fallback result
        return {
            'condition': 'Analysis Unavailable',
            'confidence': 0.0,
            'recommendations': ['Please consult a dermatologist for proper diagnosis']
        }

def preprocess_base64_image(base64_string):
    """
    Preprocess base64 image for AI model input
    """
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to image
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Resize to model input size (typically 224x224 for most models)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        
        # Add batch dimension
        return np.expand_dims(normalized_image_array, axis=0)
        
    except Exception as e:
        raise Exception(f"Image preprocessing failed: {e}")

def load_ai_model():
    """
    Load the AI model (implement this when you have the actual model)
    """
    try:
        # Uncomment and modify when you have the actual model
        # from tensorflow.keras.models import load_model
        # model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'keras_Model.h5')
        # model = load_model(model_path, compile=False)
        # return model
        
        return None  # Return None for now (using mock data)
        
    except Exception as e:
        print(f"Model loading failed: {e}")
        return None

def get_class_labels():
    """
    Load class labels from labels.txt file
    """
    try:
        labels_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'labels.txt')
        if os.path.exists(labels_path):
            with open(labels_path, 'r') as f:
                class_names = [line.strip() for line in f.readlines()]
            return class_names
        else:
            # Default labels
            return ['Benign', 'Malignant', 'Normal']
            
    except Exception as e:
        print(f"Labels loading failed: {e}")
        return ['Unknown']