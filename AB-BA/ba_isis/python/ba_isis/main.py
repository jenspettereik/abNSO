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

        vars.add('csr_net_id', service.net_id)
        self.log.info('CSR DEVICE: ', service.isis.csr.device)
        vars.add('csr_device', service.isis.csr.device)
        vars.add('csr_interface_name', service.isis.csr.isis_interface.interface_name)
        vars.add('csr_interface_number', service.isis.csr.isis_interface.interface_number)
        interface_description = service.isis.er.device + " - " + str(service.isis.er.isis_interface.interface_name) + str(service.isis.er.isis_interface.interface_number)
        vars.add('csr_interface_description', interface_description)
        vars.add('csr_ipv4_address', service.isis.csr.isis_interface.ipv4_address)
        vars.add('csr_ipv4_mask', service.isis.csr.isis_interface.ipv4_mask)

        self.log.info('ER DEVICE: ', service.isis.er.device)
        vars.add('er_device', service.isis.er.device)
        vars.add('er_interface_name', service.isis.er.isis_interface.interface_name)
        vars.add('er_interface_number', service.isis.er.isis_interface.interface_number)
        # "link to CSR / {$CSR} - {$CSR_INT_NAME}</description>"
        interface_description = service.isis.csr.device + " - " + str(service.isis.csr.isis_interface.interface_name) + str(service.isis.csr.isis_interface.interface_number)
        vars.add('er_interface_description', interface_description)
        vars.add('er_ipv4_address', service.isis.er.isis_interface.ipv4_address)
        vars.add('er_ipv4_mask', service.isis.er.isis_interface.ipv4_mask)

        template.apply('ba_isis_csr-template', vars)
        template.apply('ba_isis_er-template', vars)

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
        self.register_service('ba_isis-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
