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
        vars.add('as_number', service.endpoint.as_number)
        vars.add('rd', service.endpoint.rd)
        vars.add('vlan', service.endpoint.vlan)
        self.log.info('CSR DEVICE: ', service.endpoint.csr.device)
        vars.add('csr_device', service.endpoint.csr.device)
        vars.add('csr_interface_name', service.endpoint.csr.local.interface_name)
        vars.add('csr_interface_number', service.endpoint.csr.local.interface_number)
        interface = str(service.endpoint.csr.local.interface_name) + str(service.endpoint.csr.local.interface_number)
        vars.add('csr_interface', interface)
        interface_description = "VPN: " + service.vrf_name + ", Circuit ID: " + service.endpoint.id
        vars.add('csr_interface_description', interface_description)
        vars.add('csr_ipv4_address', service.endpoint.csr.local.ipv4_address)
        vars.add('csr_ipv4_mask', service.endpoint.csr.local.ipv4_mask)
        template.apply('ba_vrf_csr-template', vars)
        if service.endpoint.import_rt_index_1 != 0:
            vars.add('import_rt_index', service.endpoint.import_rt_index_1)
            template.apply('ba_vrf_csr_irt-template', vars)
        if service.endpoint.import_rt_index_2 != 0:
            vars.add('import_rt_index', service.endpoint.import_rt_index_2)
            template.apply('ba_vrf_csr_irt-template', vars)
        if service.endpoint.import_rt_index_3 != 0:
            vars.add('import_rt_index', service.endpoint.import_rt_index_3)
            template.apply('ba_vrf_csr_irt-template', vars)
        if service.endpoint.import_rt_index_4 != 0:
            vars.add('import_rt_index', service.endpoint.import_rt_index_4)
            template.apply('ba_vrf_csr_irt-template', vars)
        if service.endpoint.import_rt_index_5 != 0:
            vars.add('import_rt_index', service.endpoint.import_rt_index_5)
            template.apply('ba_vrf_csr_irt-template', vars)
        if service.endpoint.export_rt_index_1 != 0:
            vars.add('export_rt_index', service.endpoint.export_rt_index_1)
            template.apply('ba_vrf_csr_ert-template', vars)
        if service.endpoint.export_rt_index_2 != 0:
            vars.add('export_rt_index', service.endpoint.export_rt_index_2)
            template.apply('ba_vrf_csr_ert-template', vars)
        if service.endpoint.export_rt_index_3 != 0:
            vars.add('export_rt_index', service.endpoint.export_rt_index_3)
            template.apply('ba_vrf_csr_ert-template', vars)
        if service.endpoint.export_rt_index_4 != 0:
            vars.add('export_rt_index', service.endpoint.export_rt_index_4)
            template.apply('ba_vrf_csr_ert-template', vars)
        if service.endpoint.export_rt_index_5 != 0:
            vars.add('export_rt_index', service.endpoint.export_rt_index_5)
            template.apply('ba_vrf_csr_ert-template', vars)

        # Uplink interfaces are handled by the ISIS RFS:
        """ vars.add('csr_ul_interface_name', service.endpoint.csr.link.interface_name)
        vars.add('csr_ul_interface_number', service.endpoint.csr.link.interface_number)
        ul_interface = str(service.endpoint.csr.link.interface_name) + str(service.endpoint.csr.link.interface_number)
        self.log.info('CSR UL INTERFACE: ', ul_interface)
        vars.add('csr_ul_interface', ul_interface) """
        # "link to PE / {$PE} - {$PE_INT_NAME}</description>"
        """ ul_interface_description = service.endpoint.er.device + " - " + str(service.endpoint.er.link.interface_name) + str(service.endpoint.er.link.interface_number)
        vars.add('csr_ul_interface_description', ul_interface_description)
        vars.add('csr_ul_ipv4_address', service.endpoint.csr.link.ipv4_address)
        vars.add('csr_ul_ipv4_mask', service.endpoint.csr.link.ipv4_mask) """

        """ self.log.info('ER DEVICE: ', service.endpoint.er.device)
        vars.add('er_device', service.endpoint.er.device)
        vars.add('er_interface_name', service.endpoint.er.link.interface_name)
        vars.add('er_interface_number', service.endpoint.er.link.interface_number) """
        # "link to CSR / {$CSR} - {$CSR_INT_NAME}</description>"
        """ interface_description = service.endpoint.csr.device + " - " + ul_interface
        vars.add('er_interface_description', interface_description)
        vars.add('er_ipv4_address', service.endpoint.er.link.ipv4_address)
        vars.add('er_ipv4_mask', service.endpoint.er.link.ipv4_mask) """

        template.apply('ba_vrf_csr-template', vars)
        # template.apply('ba_vrf_er-template', vars)

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
        self.register_service('ba_vrf-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
