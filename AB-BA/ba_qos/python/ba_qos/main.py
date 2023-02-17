# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        vars.add('device', service.device)
        self.log.info('Policy Map: ', service.policy_map_name)
        vars.add('qos_policy_map_name', service.policy_map_name)
        vars.add('policy_map_description', root.inventory.qos_policy_maps.qos_policy_map[service.policy_map_name].description)
        vars.add('qos_group_value', 0)
        vars.add('traffic_class_value', 0)
        vars.add('discard_class_value', 0)
        vars.add('police_value', 0)
        vars.add('police_unit', "percent")
        for p_class in root.inventory.qos_policy_maps.qos_policy_map[service.policy_map_name].policy_classes.policy_class:

            vars.add('qos_class_map_name', p_class.class_name)
            vars.add('class_map_description', root.inventory.qos_class_maps.qos_class_map[p_class.class_name].description)
            vars.add('match_statement', root.inventory.qos_class_maps.qos_class_map[p_class.class_name].match_statement)
            for me in root.inventory.qos_class_maps.qos_class_map[p_class.class_name].match_elements.match_element:
                self.log.info('match_subject: ', me.match_subject)
                if me.match_subject == "cos":
                    for cv in me.cos.cos_values:
                        vars.add('cos_value', cv.cos_value)
                        template.apply('ba_class_map_cos_template', vars)
                elif me.match_subject == "dscp":
                    for dv in me.dscp.dscp_values:
                        vars.add('dscp_value', dv.dscp_value)
                        template.apply('ba_class_map_dscp_template', vars)
                elif me.match_subject == "mpls":
                    vars.add('mpls_subject1', me.mpls.mpls_subject1)
                    vars.add('mpls_subject2', me.mpls.mpls_subject2)
                    for m in me.mpls.mpls_labels:
                        vars.add('mpls_label', m.mpls_label)
                        template.apply('ba_class_map_mpls_template', vars)
            
            vars.add('class_name', p_class.class_name)
            vars.add('class_type', p_class.class_type)
            for co in p_class.class_operation:
                vars.add('class_operation_name', co.class_operation_name)
                if co.class_operation_name == "set":
                    vars.add('set_subject', co.set_subject)
                    if co.set_subject == "qos-group":
                        vars.add('qos_group_value', co.qos_group_value)
                        template.apply('ba_policy_map_template', vars)
                    elif co.set_subject == "traffic-class":
                        vars.add('traffic_class_value', co.traffic_class_value)
                        template.apply('ba_policy_map_template', vars)
                    elif co.set_subject == "discard-class":
                        vars.add('discard_class_value', co.discard_class_value)
                        template.apply('ba_policy_map_template', vars)
                elif co.class_operation_name == "police":
                    vars.add('police_subject', co.police_subject)
                    vars.add('police_value', co.police_value)
                    vars.add('police_unit', co.police_unit)
                    template.apply('ba_policy_map_template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('ba_qos-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
