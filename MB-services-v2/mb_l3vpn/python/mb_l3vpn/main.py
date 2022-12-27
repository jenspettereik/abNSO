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

        vars.add('vrf_name', service.vrf_name)
        for endpoint in service.endpoint:
            vars.add('as_number', endpoint.as_number)
            vars.add('rd', endpoint.rd)
            vars.add('c_vlan', endpoint.vlan)
            self.log.info('CSR DEVICE: ', endpoint.csr.device)
            vars.add('device', endpoint.csr.device)
            vars.add('interface_name', endpoint.csr.local.interface_name)
            vars.add('interface_number', endpoint.csr.local.interface_number)
            interface = endpoint.csr.local.interface_name + endpoint.csr.local.interface_number
            vars.add('interface', interface)
            interface_description = "VPN: " + service.vrf_name + ", Circuit ID: " + endpoint.id
            vars.add('interface_description', interface_description)
            vars.add('ipv4_address', endpoint.csr.local.ipv4_address)
            vars.add('ipv4_mask', endpoint.csr.local.ipv4_mask)
            vars.add('ul_interface_name', endpoint.csr.link.interface_name)
            vars.add('ul_interface_number', endpoint.csr.link.interface_number)
            ul_interface = endpoint.csr.link.interface_name + endpoint.csr.link.interface_number
            self.log.info('CSR UL INTERFACE: ', ul_interface)
            vars.add('ul_interface', ul_interface)
            # "link to PE / {$PE} - {$PE_INT_NAME}</description>"
            ul_interface_description = endpoint.er.device + " - " + endpoint.er.link.interface_name + endpoint.er.link.interface_number
            vars.add('ul_interface_description', ul_interface_description)
            vars.add('ul_ipv4_address', endpoint.csr.link.ipv4_address)
            vars.add('ul_ipv4_mask', endpoint.csr.link.ipv4_mask)
            template.apply('mb_l3vpn_csr-template', vars)

            self.log.info('ER DEVICE: ', endpoint.er.device)
            vars.add('device', endpoint.er.device)
            vars.add('interface_name', endpoint.er.link.interface_name)
            vars.add('interface_number', endpoint.er.link.interface_number)
            # "link to CSR / {$CSR} - {$CSR_INT_NAME}</description>"
            interface_description = endpoint.csr.device + " - " + ul_interface
            vars.add('interface_description', interface_description)
            vars.add('ipv4_address', endpoint.er.link.ipv4_address)
            vars.add('ipv4_mask', endpoint.er.link.ipv4_mask)
            template.apply('mb_l3vpn_er-template', vars)

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
        self.register_service('mb_l3vpn-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
