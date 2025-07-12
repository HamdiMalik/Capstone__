from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import os
import uuid
from datetime import datetime
import json

from models import db, User, Scan
from services.ai_service import analyze_skin_image

scans_bp = Blueprint('scans', __name__)

@scans_bp.route('', methods=['GET'])
@jwt_required()
def get_scans():
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        scans_query = Scan.query.filter_by(user_id=current_user_id).order_by(Scan.timestamp.desc())
        
        paginated_scans = scans_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        scans = [scan.to_dict() for scan in paginated_scans.items]
        
        return jsonify({
            'scans': scans,
            'total': paginated_scans.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated_scans.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scans_bp.route('', methods=['POST'])
@jwt_required()
def create_scan():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        image_path = data.get('imagePath', '')
        timestamp_str = data.get('timestamp')
        
        if not image_path:
            return jsonify({'error': 'Image path is required'}), 400
        
        # Parse timestamp if provided
        scan_timestamp = datetime.utcnow()
        if timestamp_str:
            try:
                scan_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                pass
        
        # Create scan record
        scan = Scan(
            user_id=current_user_id,
            image_path=image_path,
            timestamp=scan_timestamp
        )
        
        # Analyze image if it's base64 encoded
        if image_path.startswith('data:image'):
            try:
                result = analyze_skin_image(image_path)
                scan.set_result(
                    result['condition'],
                    result['confidence'],
                    result['recommendations']
                )
            except Exception as e:
                print(f"AI analysis failed: {e}")
                # Set default result if AI fails
                scan.set_result(
                    "Analysis Pending",
                    0.0,
                    ["Please consult a dermatologist for proper diagnosis"]
                )
        
        db.session.add(scan)
        db.session.commit()
        
        return jsonify({'scan': scan.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@scans_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_scans():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        scans_data = data.get('scans', [])
        
        synced_scans = []
        
        for scan_data in scans_data:
            # Create new scan record
            scan = Scan(
                user_id=current_user_id,
                image_path=scan_data.get('image_path', ''),
                timestamp=datetime.fromisoformat(scan_data.get('timestamp', datetime.utcnow().isoformat()))
            )
            
            # Set result if provided
            result = scan_data.get('result')
            if result:
                scan.set_result(
                    result.get('condition', ''),
                    result.get('confidence', 0.0),
                    result.get('recommendations', [])
                )
            
            db.session.add(scan)
            synced_scans.append(scan)
        
        db.session.commit()
        
        return jsonify({
            'synced_count': len(synced_scans),
            'scans': [scan.to_dict() for scan in synced_scans]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@scans_bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    try:
        current_user_id = get_jwt_identity()
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
        
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify({'scan': scan.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scans_bp.route('/<int:scan_id>', methods=['DELETE'])
@jwt_required()
def delete_scan(scan_id):
    try:
        current_user_id = get_jwt_identity()
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
        
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        db.session.delete(scan)
        db.session.commit()
        
        return jsonify({'message': 'Scan deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500