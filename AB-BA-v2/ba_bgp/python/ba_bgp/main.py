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
        vars.add('csr_neighbor_group_name', "T-RR-NC")
        vars.add('rr1_ipv4_address', service.bgp.csr.rr1_ipv4_address)
        vars.add('rr1_neighbor_description', "RR1 is device "+service.bgp.csr.rr1_device_name)
        vars.add('rr2_ipv4_address', service.bgp.csr.rr2_ipv4_address)
        vars.add('rr2_neighbor_description', "RR2 is device "+service.bgp.csr.rr2_device_name)
        template.apply('ba_bgp_csr-template', vars)

        vars.add('agg_neighbor_ipv4_address', service.bgp.csr.mgmt_ipv4_address)
        vars.add('agg_neighbor_group_name', "T-RR-NC")
        vars.add('agg_device', service.bgp.csr.rr1_device_name)
        vars.add('agg_neighbor_description', "I am RR1 for CSR " + service.bgp.csr.device)
        template.apply('ba_bgp_agg-template', vars)
        vars.add('agg_device', service.bgp.csr.rr2_device_name)
        vars.add('agg_neighbor_description', "I am RR2 for CSR " + service.bgp.csr.device)
        template.apply('ba_bgp_agg-template', vars)

        # 1: i steden for å lage inventory på METRO ring, så vil det i API kallet komme:
        # hostanvn/device navn på RR1 og RR2 (AGG1 og AGG2)
        # peer ip adresse på RR1 og RR2 (RR1 på AGG1 og AGG2)

        """ for rr in root.inventory.METRO3Areas.METRO3Area[service.m3_area].RR:
            self.log.info('RR address: ', rr.RR_ipv4_addr)
            vars.add('csr_neighbor_ipv4_address', rr.RR_ipv4_addr)
            vars.add('csr_neighbor_group_name', rr.neighbor_group_name)
            vars.add('csr_neighbor_description', rr.neighbor_description)
            template.apply('ba_bgp_csr-template', vars)
            if not service.only_CSR:
                vars.add('agg_device', rr.agg_device)
                self.log.info('AGG DEVICE: ', rr.agg_device)
                vars.add('agg_neighbor_ipv4_address', service.bgp.csr.mgmt_ipv4_address)
                vars.add('agg_neighbor_group_name', rr.neighbor_group_name)
                vars.add('agg_neighbor_description', rr.neighbor_description)
                template.apply('ba_bgp_agg-template', vars) """

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
