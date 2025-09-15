import requests
import os
from flask import current_app

def sync_user_to_projects_crm(user):
    """Sync a user from my-agency-crm to projects-crm"""
    try:
        projects_crm_url = current_app.config.get('PROJECTS_CRM_URL', 'http://localhost:5001')
        projects_crm_api_key = current_app.config.get('PROJECTS_CRM_API_KEY')

        if not projects_crm_api_key:
            current_app.logger.error('PROJECTS_CRM_API_KEY not configured')
            return False

        user_data = {
            'agency_crm_id': user.id,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}",
            'password_hash': user.password_hash  # Send the hash directly
        }

        headers = {
            'X-API-Key': projects_crm_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'{projects_crm_url}/api/sync-user',
            json=user_data,
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            current_app.logger.info(f'Successfully synced user {user.email} to projects-crm')
            return True
        else:
            current_app.logger.error(f'Failed to sync user {user.email}: {response.text}')
            return False

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Error syncing user to projects-crm: {str(e)}')
        return False
    except Exception as e:
        current_app.logger.error(f'Unexpected error syncing user: {str(e)}')
        return False