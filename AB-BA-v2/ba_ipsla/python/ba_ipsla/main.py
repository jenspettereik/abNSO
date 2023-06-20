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
        vars.add('tos', 0)
        vars.add('device', service.device)
        vars.add('count', 1)
        vars.add('interval', 1)
        vars.add('buckets', 1)
        vars.add('interval_time', 1)
        vars.add('source_port', 65000)
        vars.add('destination_port', 65000)
        hostname = service.hostname
        ipsla_mgmt_address = service.ipsla_mgmt_address
        for ipsla_op in root.inventory.ipsla_operations.ipsla_operation:
            vars.add('operation_number', ipsla_op.operation_number)
            vars.add('operation_type', ipsla_op.operation_type)
            vars.add('udp_operation_type', ipsla_op.udp_operation_type)
            vars.add('operation_tag', hostname + "-" + ipsla_op.operation_tag)
            vars.add('vrf', ipsla_op.vrf)
            vars.add('source_address', ipsla_mgmt_address)
            vars.add('set_source_port', ipsla_op.set_source_port)
            if ipsla_op.set_source_port:
                vars.add('source_port', ipsla_op.source_port)
            vars.add('destination_address', ipsla_op.destination_address)
            vars.add('set_destination_port', ipsla_op.set_destination_port)
            if ipsla_op.set_destination_port:
                vars.add('destination_port', ipsla_op.destination_port)
            vars.add('frequency', ipsla_op.frequency)
            if ipsla_op.tos_or_not.set_tos:
                vars.add('set_tos', True)
                vars.add('tos', ipsla_op.tos_or_not.tos)
            else:
                vars.add('set_tos', False)
            if ipsla_op.jitter_options.packet.set_packet:
                vars.add('set_packet', True)
                vars.add('count', ipsla_op.jitter_options.packet.count)
                vars.add('interval', ipsla_op.jitter_options.packet.interval)
            else:
                vars.add('set_packet', False)
            if ipsla_op.jitter_options.statistics.set_stats:
                vars.add('set_stats', True)
                vars.add('buckets', ipsla_op.jitter_options.statistics.buckets)
                vars.add('interval_time', ipsla_op.jitter_options.statistics.interval_time)
            else:
                vars.add('set_stats', False)
            template.apply('ba_ipsla-template', vars)

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
        self.register_service('ba_ipsla-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
