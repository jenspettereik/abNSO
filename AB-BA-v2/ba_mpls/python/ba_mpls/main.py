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

        # Start by adding the MPLS_LOOPBACKS ACL on csr and er
        vars.add('acl_name', service.acl_name)
        for seq in root.inventory.access_lists.access_list[service.acl_name].sequence:
            vars.add('sequence_number', seq.sequence_number)
            vars.add('protocol', seq.protocol)
            vars.add('ipv4_addr', seq.ipv4_addr)
            vars.add('prefix_length', seq.prefix_length)
            vars.add('device', service.mpls.csr.device)
            template.apply('ba_mpls_acl-template', vars)
            if not service.only_CSR:
                vars.add('device', service.mpls.er.device)
                template.apply('ba_mpls_acl-template', vars)

        # Add MPLS configuration to the csr
        vars.add('device', service.mpls.csr.device)
        vars.add('mgmt_ipv4_address', service.mpls.csr.mgmt_ipv4_address)
        vars.add('interface_name', service.mpls.csr.interface_name)
        vars.add('interface_number', service.mpls.csr.interface_number)
        template.apply('ba_mpls_ldp_csr-template', vars)

        # Add MPLS configuration to the er
        if not service.only_CSR:
            vars.add('device', service.mpls.er.device)
            vars.add('interface_name', service.mpls.er.interface_name)
            vars.add('interface_number', service.mpls.er.interface_number)
            template.apply('ba_mpls_ldp_er-template', vars)

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
        self.register_service('ba_mpls-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
