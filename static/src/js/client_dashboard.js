/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SmartHiveClientDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            dashboardData: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;

            // Load client statistics
            const clients = await this.orm.searchRead(
                "smarthive.client",
                [],
                ["name", "connection_status", "payment_status", "is_blocked", "outstanding_amount"]
            );

            const dashboardData = {
                totalClients: clients.length,
                onlineClients: clients.filter(c => c.connection_status === 'online').length,
                blockedClients: clients.filter(c => c.is_blocked).length,
                pendingPayments: clients.filter(c => ['pending', 'overdue'].includes(c.payment_status)).length,
                totalOutstanding: clients.reduce((sum, c) => sum + (c.outstanding_amount || 0), 0),
            };

            this.state.dashboardData = dashboardData;
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        await this.loadDashboardData();
    }
}

SmartHiveClientDashboard.template = "smarthive.ClientDashboard";

registry.category("actions").add("smarthive.client_dashboard", SmartHiveClientDashboard);