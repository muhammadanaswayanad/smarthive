# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Constants
IR_ACTIONS_CLIENT = 'ir.actions.client'
NOTIFICATION_SUCCESS = 'success'


class ClientManagement(models.Model):
    _name = 'smarthive.client'
    _description = 'SmartHive Client Management'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Client Name',
        required=True,
        tracking=True,
        help='Name of the client organization'
    )
    
    client_id = fields.Char(
        string='Client ID',
        required=True,
        unique=True,
        tracking=True,
        help='Unique identifier for the client'
    )
    
    domain = fields.Char(
        string='Client Domain',
        required=True,
        tracking=True,
        help='Domain or URL of the client Odoo instance'
    )
    
    api_key = fields.Char(
        string='API Key',
        required=True,
        help='API key for secure communication with client instance'
    )
    
    database_name = fields.Char(
        string='Database Name',
        help='Name of the client database'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )
    
    is_blocked = fields.Boolean(
        string='Blocked',
        default=False,
        tracking=True,
        help='Block client access to their system'
    )
    
    block_reason = fields.Text(
        string='Block Reason',
        help='Reason for blocking the client'
    )
    
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending Payment'),
        ('overdue', 'Overdue'),
        ('blocked', 'Payment Blocked')
    ], string='Payment Status', default='paid', tracking=True)
    
    last_payment_date = fields.Date(
        string='Last Payment Date',
        tracking=True
    )
    
    next_payment_due = fields.Date(
        string='Next Payment Due',
        tracking=True
    )
    
    outstanding_amount = fields.Float(
        string='Outstanding Amount',
        digits='Product Price',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    last_connection = fields.Datetime(
        string='Last Connection',
        help='Last time we successfully connected to the client'
    )
    
    connection_status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Connection Error')
    ], string='Connection Status', default='offline')
    
    odoo_version = fields.Char(
        string='Odoo Version',
        help='Client Odoo version'
    )
    
    client_addon_version = fields.Char(
        string='Client Addon Version',
        help='Version of the SmartHive client addon installed'
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    # Status tracking fields
    show_warning = fields.Boolean(
        string='Show Warning Banner',
        default=False,
        help='Show warning banner on client instance'
    )
    
    warning_message = fields.Text(
        string='Warning Message',
        help='Custom warning message to display'
    )
    
    auto_block_overdue = fields.Boolean(
        string='Auto Block on Overdue',
        default=True,
        help='Automatically block client when payment is overdue'
    )
    
    overdue_grace_days = fields.Integer(
        string='Grace Days for Overdue',
        default=7,
        help='Number of days after due date before auto-blocking'
    )

    @api.constrains('domain')
    def _check_domain_format(self):
        """Validate domain format"""
        for record in self:
            if record.domain:
                if not (record.domain.startswith('http://') or record.domain.startswith('https://')):
                    raise ValidationError(_('Domain must start with http:// or https://'))

    @api.model
    def create(self, vals):
        """Override create to set up initial connection"""
        client = super(ClientManagement, self).create(vals)
        client._check_client_connection()
        return client

    def _get_api_headers(self):
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'X-SmartHive-API-Key': self.api_key,
            'X-SmartHive-Client-ID': self.client_id,
        }

    def _make_api_request(self, endpoint, method='GET', data=None):
        """Make API request to client instance"""
        try:
            url = f"{self.domain.rstrip('/')}/smarthive_client/{endpoint}"
            headers = self._get_api_headers()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data or {}, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data or {}, timeout=30)
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"API request failed for client {self.name}: {str(e)}")
            self.connection_status = 'error'
            raise UserError(_("Failed to connect to client %s: %s") % (self.name, str(e)))

    def _check_client_connection(self):
        """Check connection status with client"""
        try:
            result = self._make_api_request('ping')
            self.write({
                'connection_status': 'online',
                'last_connection': fields.Datetime.now(),
                'odoo_version': result.get('odoo_version'),
                'client_addon_version': result.get('addon_version'),
            })
            return True
        except Exception as e:
            self.write({
                'connection_status': 'error',
            })
            _logger.warning(f"Connection check failed for client {self.name}: {str(e)}")
            return False

    def action_check_connection(self):
        """Manual connection check action"""
        self.ensure_one()
        if self._check_client_connection():
            return {
                'type': IR_ACTIONS_CLIENT,
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Successfully connected to client %s') % self.name,
                    'type': NOTIFICATION_SUCCESS,
                }
            }

    def action_block_client(self):
        """Block client access"""
        self.ensure_one()
        try:
            data = {
                'blocked': True,
                'block_reason': self.block_reason or 'Blocked by administrator',
            }
            self._make_api_request('block', method='POST', data=data)
            self.is_blocked = True
            self.message_post(body=_("Client has been blocked"))
            
            return {
                'type': IR_ACTIONS_CLIENT,
                'tag': 'display_notification',
                'params': {
                    'title': _('Client Blocked'),
                    'message': _('Client %s has been successfully blocked') % self.name,
                    'type': NOTIFICATION_SUCCESS,
                }
            }
        except Exception as e:
            raise UserError(_("Failed to block client: %s") % str(e))

    def action_unblock_client(self):
        """Unblock client access"""
        self.ensure_one()
        try:
            data = {'blocked': False}
            self._make_api_request('unblock', method='POST', data=data)
            self.is_blocked = False
            self.message_post(body=_("Client has been unblocked"))
            
            return {
                'type': IR_ACTIONS_CLIENT,
                'tag': 'display_notification',
                'params': {
                    'title': _('Client Unblocked'),
                    'message': _('Client %s has been successfully unblocked') % self.name,
                    'type': NOTIFICATION_SUCCESS,
                }
            }
        except Exception as e:
            raise UserError(_("Failed to unblock client: %s") % str(e))

    def action_send_warning(self):
        """Send warning banner to client"""
        self.ensure_one()
        try:
            data = {
                'show_warning': self.show_warning,
                'warning_message': self.warning_message or 'Payment reminder: Please check your payment status.',
                'payment_status': self.payment_status,
                'outstanding_amount': self.outstanding_amount,
            }
            self._make_api_request('warning', method='POST', data=data)
            self.message_post(body=_("Warning banner sent to client"))
            
            return {
                'type': IR_ACTIONS_CLIENT,
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning Sent'),
                    'message': _('Warning banner sent to client %s') % self.name,
                    'type': NOTIFICATION_SUCCESS,
                }
            }
        except Exception as e:
            raise UserError(_("Failed to send warning: %s") % str(e))

    def action_update_payment_status(self):
        """Update payment status and sync with client"""
        self.ensure_one()
        
        # Check if payment is overdue and should be auto-blocked
        if (self.payment_status == 'overdue' and 
            self.auto_block_overdue and 
            self.next_payment_due and 
            (fields.Date.today() - self.next_payment_due).days > self.overdue_grace_days):
            
            self.show_warning = True
            self.warning_message = f"Payment overdue by {(fields.Date.today() - self.next_payment_due).days} days. Please settle immediately."
            
            if not self.is_blocked:
                self.block_reason = "Auto-blocked due to overdue payment"
                self.action_block_client()
        
        # Send updated status to client
        self.action_send_warning()

    @api.model
    def cron_check_payments(self):
        """Cron job to check payment status and auto-block if needed"""
        clients = self.search([
            ('active', '=', True),
            ('payment_status', 'in', ['pending', 'overdue']),
        ])
        
        for client in clients:
            try:
                client.action_update_payment_status()
            except Exception as e:
                _logger.error(f"Failed to update payment status for client {client.name}: {str(e)}")

    @api.model
    def cron_check_connections(self):
        """Cron job to check client connections"""
        clients = self.search([('active', '=', True)])
        
        for client in clients:
            try:
                client._check_client_connection()
            except Exception as e:
                _logger.error(f"Connection check failed for client {client.name}: {str(e)}")