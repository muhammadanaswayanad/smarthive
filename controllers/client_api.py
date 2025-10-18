# -*- coding: utf-8 -*-

import json
import logging
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class ClientAPIController(http.Controller):
    
    def _authenticate_request(self):
        """Authenticate API request using headers"""
        api_key = request.httprequest.headers.get('X-SmartHive-API-Key')
        client_id = request.httprequest.headers.get('X-SmartHive-Client-ID')
        
        if not api_key or not client_id:
            return False, "Missing API key or client ID"
        
        client = request.env['smarthive.client'].sudo().search([
            ('client_id', '=', client_id),
            ('api_key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if not client:
            return False, "Invalid API credentials"
            
        return client, None

    @http.route('/smarthive/api/client/status', type='json', auth='none', methods=['POST'], csrf=False)
    def client_status_update(self):
        """Receive status updates from client instances"""
        try:
            client, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            data = request.jsonrequest
            
            # Update client status
            client.write({
                'last_connection': fields.Datetime.now(),
                'connection_status': 'online',
                'odoo_version': data.get('odoo_version'),
                'client_addon_version': data.get('addon_version'),
            })
            
            # Log status update
            request.env['smarthive.client.status'].sudo().log_status(
                client.id,
                'system',
                'info',
                'Status update received',
                json.dumps(data)
            )
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Client status update error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive/api/client/heartbeat', type='json', auth='none', methods=['POST'], csrf=False)
    def client_heartbeat(self):
        """Heartbeat endpoint for client health checks"""
        try:
            client, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            client.write({
                'last_connection': fields.Datetime.now(),
                'connection_status': 'online',
            })
            
            # Return current status that client should apply
            return {
                'success': True,
                'blocked': client.is_blocked,
                'block_reason': client.block_reason,
                'show_warning': client.show_warning,
                'warning_message': client.warning_message,
                'payment_status': client.payment_status,
            }
            
        except Exception as e:
            _logger.error(f"Client heartbeat error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive/api/dashboard', type='http', auth='user', methods=['GET'])
    def client_dashboard(self):
        """Dashboard endpoint for client management"""
        clients = request.env['smarthive.client'].search([])
        
        dashboard_data = {
            'total_clients': len(clients),
            'online_clients': len(clients.filtered(lambda c: c.connection_status == 'online')),
            'blocked_clients': len(clients.filtered(lambda c: c.is_blocked)),
            'pending_payments': len(clients.filtered(lambda c: c.payment_status in ['pending', 'overdue'])),
        }
        
        return json.dumps(dashboard_data)