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

        vars.add('as_number', service.as_number)
        self.log.info('CSR DEVICE: ', service.bgp.csr.device)
        vars.add('csr_device', service.bgp.csr.device)
        vars.add('csr_mgmt_ipv4_address', service.bgp.csr.mgmt_ipv4_address)
        vars.add('csr_paths_route_policy', service.bgp.csr.paths_route_policy)
        vars.add('csr_networks_route_policy', service.bgp.csr.networks_route_policy)
        vars.add('csr_ng_route_policy_in', service.bgp.csr.ng_route_policy_in)
        vars.add('csr_ng_route_policy_out', service.bgp.csr.ng_route_policy_out)
        vars.add('csr_neighbor_ipv4_address', service.bgp.csr.neighbor_ipv4_address)
        vars.add('csr_neighbor_group_name', service.bgp.csr.neighbor_group_name)
        vars.add('csr_neighbor_description', service.bgp.csr.neighbor_description)

        self.log.info('AGG DEVICE: ', service.bgp.agg.device)
        vars.add('agg_device', service.bgp.agg.device)
        vars.add('agg_neighbor_ipv4_address', service.bgp.agg.neighbor_ipv4_address)
        vars.add('agg_neighbor_group_name', service.bgp.agg.neighbor_group_name)
        vars.add('agg_neighbor_description', service.bgp.agg.neighbor_description)

        template.apply('ba_bgp_csr-template', vars)
        template.apply('ba_bgp_agg-template', vars)

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
        self.register_service('ba_bgp-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
