/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

class AboutUs extends Component {

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.root = useRef("aboutUsRoot");

        this.state = useState({
            instructors: [],
        });

        onWillStart(async () => {
            this.state.instructors = await this.rpc("/online_courses/instructors");
        });
    }

    exploreCourses() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "online.course",
            name: "Our Courses",
            views: [[false, "kanban"], [false, "tree"], [false, "form"]],
            target: "current",
        });
    }

    showOurInstructors() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "online.instructor",
            name: "Our Instructors",
            views: [[false, "kanban"], [false, "tree"], [false, "form"]],
            target: "current",
        });
    }

}

AboutUs.template = 'online_courses.AboutUs';
registry.category("actions").add("about.us.client.action", AboutUs);
