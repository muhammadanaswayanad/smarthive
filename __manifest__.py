{
    'name': 'SmartHive Client Management',
    'version': '18.0.1.0.0',
    'category': 'Administration',
    'summary': 'Manage remote Odoo clients, payment status, and blocking functionality',
    'description': """
SmartHive Client Management
===========================

This addon allows you to manage multiple remote Odoo client instances from a central Odoo 18 EE installation.

Key Features:
* Centralized client management
* Remote payment status monitoring  
* Client blocking/unblocking capabilities
* Warning banner system for pending payments
* Secure API communication with client instances
* Real-time status monitoring

Use Cases:
* SaaS providers managing multiple client installations
* Service companies monitoring client payment status
* Remote administration of distributed Odoo instances
    """,
    'author': 'SmartHive',
    'website': 'https://www.smarthive.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/client_status_views.xml',
        'views/client_management_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smarthive/static/src/js/client_dashboard.js',
            'smarthive/static/src/css/client_management.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}