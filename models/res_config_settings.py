# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smarthive_api_timeout = fields.Integer(
        string='API Timeout (seconds)',
        default=30,
        config_parameter='smarthive.api_timeout',
        help='Timeout for API requests to client instances'
    )
    
    smarthive_auto_check_interval = fields.Integer(
        string='Auto Check Interval (minutes)',
        default=60,
        config_parameter='smarthive.auto_check_interval',
        help='Interval for automatic connection checks'
    )
    
    smarthive_payment_check_interval = fields.Integer(
        string='Payment Check Interval (hours)',
        default=24,
        config_parameter='smarthive.payment_check_interval',
        help='Interval for automatic payment status checks'
    )
    
    smarthive_default_grace_days = fields.Integer(
        string='Default Grace Days',
        default=7,
        config_parameter='smarthive.default_grace_days',
        help='Default number of grace days for overdue payments'
    )