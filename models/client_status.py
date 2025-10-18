# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ClientStatus(models.Model):
    _name = 'smarthive.client.status'
    _description = 'Client Status Log'
    _order = 'create_date desc'

    client_id = fields.Many2one(
        'smarthive.client',
        string='Client',
        required=True,
        ondelete='cascade'
    )
    
    status_type = fields.Selection([
        ('connection', 'Connection'),
        ('payment', 'Payment'),
        ('block', 'Block/Unblock'),
        ('warning', 'Warning'),
        ('system', 'System')
    ], string='Status Type', required=True)
    
    status = fields.Selection([
        ('success', 'Success'),
        ('warning', 'Warning'), 
        ('error', 'Error'),
        ('info', 'Information')
    ], string='Status', required=True)
    
    message = fields.Text(
        string='Message',
        required=True
    )
    
    details = fields.Text(
        string='Details'
    )
    
    create_date = fields.Datetime(
        string='Date',
        readonly=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.model
    def log_status(self, client_id, status_type, status, message, details=None):
        """Helper method to log client status"""
        return self.create({
            'client_id': client_id,
            'status_type': status_type,
            'status': status,
            'message': message,
            'details': details,
        })