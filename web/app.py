#!/usr/bin/env python3
"""
Flask Web UI for Telegram Job Scraper

This provides a web interface to manage the job scraper, view results,
and configure settings.
"""

import sys
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import json
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
from output import DatabaseManager

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get statistics
        stats = db_manager.get_statistics()
        
        # Get recent jobs
        recent_jobs = db_manager.get_jobs(limit=10)
        
        return render_template('index.html', stats=stats, recent_jobs=recent_jobs)
    except Exception as e:
        logger.error(f'Error loading dashboard: {e}')
        return render_template('error.html', error=str(e))

@app.route('/jobs')
def jobs():
    """Jobs listing page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        # Get jobs with pagination
        all_jobs = db_manager.get_jobs(limit=1000)  # Get all for pagination
        total_jobs = len(all_jobs)
        jobs_page = all_jobs[offset:offset + per_page]
        
        total_pages = (total_jobs + per_page - 1) // per_page
        
        return render_template('jobs.html', 
                             jobs=jobs_page, 
                             page=page, 
                             total_pages=total_pages,
                             total_jobs=total_jobs)
    except Exception as e:
        logger.error(f'Error loading jobs: {e}')
        return render_template('error.html', error=str(e))

@app.route('/favorites')
def favorites():
    """Favorites page"""
    try:
        favorite_jobs = db_manager.get_jobs(limit=100, favorite_only=True)
        return render_template('favorites.html', jobs=favorite_jobs)
    except Exception as e:
        logger.error(f'Error loading favorites: {e}')
        return render_template('error.html', error=str(e))

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for jobs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        favorite_only = request.args.get('favorite_only', 'false').lower() == 'true'
        
        offset = (page - 1) * per_page
        
        # Get jobs
        all_jobs = db_manager.get_jobs(limit=1000, favorite_only=favorite_only)
        total_jobs = len(all_jobs)
        jobs_page = all_jobs[offset:offset + per_page]
        
        return jsonify({
            'jobs': jobs_page,
            'total': total_jobs,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_jobs + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f'API error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>/toggle_favorite', methods=['POST'])
def api_toggle_favorite(job_id):
    """API endpoint to toggle favorite status"""
    try:
        success = db_manager.toggle_favorite(job_id)
        if success:
            return jsonify({'success': True, 'message': 'Favorite status updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update favorite status'}), 400
    except Exception as e:
        logger.error(f'Error toggling favorite: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = db_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f'Error getting stats: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings():
    """Settings page"""
    try:
        # Get current configuration
        current_config = {
            'target_channels': config.target_channels,
            'filter_keywords': config.filter_keywords,
            'date_filter_hours': config.date_filter_hours,
            'output_method': config.output_method
        }
        
        return render_template('settings.html', config=current_config)
    except Exception as e:
        logger.error(f'Error loading settings: {e}')
        return render_template('error.html', error=str(e))

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API endpoint to update settings"""
    try:
        data = request.get_json()
        
        # Update configuration (this would need to be implemented)
        # For now, just return success
        logger.info(f'Settings update requested: {data}')
        
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        logger.error(f'Error updating settings: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export():
    """Export jobs page"""
    try:
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            jobs = db_manager.get_jobs(limit=1000)
            return jsonify(jobs), 200, {'Content-Type': 'application/json'}
        elif format_type == 'csv':
            # CSV export would need to be implemented
            return jsonify({'error': 'CSV export not implemented yet'}), 501
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f'Error exporting data: {e}')
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(
        host=config.web_host,
        port=config.web_port,
        debug=True
    )