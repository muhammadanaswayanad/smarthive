# SmartHive Client Management

## Overview

SmartHive is an Odoo addon that enables centralized management of multiple remote Odoo client instances. It allows you to monitor client status, manage payments, and control access remotely.

## Features

### Server Side (Odoo 18 EE)
- Centralized client management dashboard
- Real-time connection monitoring
- Payment status tracking and alerts
- Remote client blocking/unblocking
- Warning banner management
- Automated payment monitoring
- Secure API communication

### Client Side (Odoo 17 CE)
- Automatic status reporting to server
- Warning banner display system
- Access control enforcement
- Heartbeat monitoring
- Secure API authentication

## Installation

### Server Installation (Odoo 18 EE)

1. Copy the `smarthive` folder to your Odoo 18 custom addons directory
2. Update your addons list: `./odoo-bin -u all -d your_database`
3. Install the addon from Apps menu
4. Configure API settings in Settings > SmartHive

### Client Installation (Odoo 17 CE)

1. Copy the `smarthive_client` folder to your Odoo 17 custom addons directory
2. Update your addons list and install the addon
3. Configure the server connection details

## Configuration

### Server Configuration

1. Go to SmartHive > Configuration > Settings
2. Set API timeout and check intervals
3. Configure default grace periods

### Client Registration

1. Navigate to SmartHive > Clients > Client Management
2. Click "Create" to add a new client
3. Fill in client details:
   - Client Name
   - Client ID (unique identifier)
   - Domain (client Odoo URL)
   - API Key (for secure communication)
   - Database name

### Client Configuration

1. In the client instance, go to Settings > SmartHive Client
2. Enter server details:
   - Server URL (your Odoo 18 instance)
   - Client ID (matching server configuration)
   - API Key (matching server configuration)

## Usage

### Managing Clients

- **View Clients**: Access client list via SmartHive > Clients
- **Check Connection**: Use "Check Connection" button to test connectivity
- **Block/Unblock**: Use respective buttons to control client access
- **Send Warnings**: Configure and send warning banners to clients
- **Monitor Payments**: Track payment status and set up automated blocking

### Payment Management

1. Set payment status (Paid, Pending, Overdue, Blocked)
2. Configure outstanding amounts and due dates
3. Enable auto-blocking for overdue payments
4. Set grace periods before automatic blocking

### Warning System

1. Enable "Show Warning Banner" for a client
2. Customize warning message
3. Click "Send Warning" to display on client instance

## API Endpoints

### Server Endpoints

- `POST /smarthive/api/client/status` - Receive client status updates
- `POST /smarthive/api/client/heartbeat` - Client heartbeat check
- `GET /smarthive/api/dashboard` - Dashboard data

### Client Endpoints

- `GET /smarthive_client/ping` - Health check
- `POST /smarthive_client/block` - Block client access
- `POST /smarthive_client/unblock` - Unblock client access
- `POST /smarthive_client/warning` - Send warning banner

## Security

- API key authentication for all communications
- Client ID verification
- Encrypted communication recommended (HTTPS)
- Role-based access control with user groups

## Troubleshooting

### Connection Issues

1. Verify client domain is accessible
2. Check API key matches on both sides
3. Ensure firewall allows communication
4. Verify SSL certificates if using HTTPS

### Payment Blocking Not Working

1. Check client addon is installed and configured
2. Verify API communication is working
3. Check cron jobs are running on server
4. Review status logs for error messages

## Support

For support and documentation, visit: https://www.smarthive.com