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
        vars.add('only_CSR', service.only_CSR)
        for endpoint in service.endpoint:
            # Collecting all the interface data, which are used by several RFS's
            vars.add('endpoint_id', endpoint.id)
            vars.add('as_number', endpoint.as_number)
            vars.add('rd', endpoint.rd)
            vars.add('vlan', endpoint.vlan)
            # self.log.info('CSR DEVICE: ', endpoint.csr.device)
            vars.add('csr_device', endpoint.csr.device)
            vars.add('csr_interface_name', endpoint.csr.local.interface_name)
            vars.add('csr_interface_number', endpoint.csr.local.interface_number)
            interface = str(endpoint.csr.local.interface_name) + str(endpoint.csr.local.interface_number)
            vars.add('csr_interface', interface)
            interface_description = "VPN: " + service.vrf_name + ", Circuit ID: " + endpoint.id
            vars.add('csr_interface_description', interface_description)
            vars.add('csr_ipv4_address', endpoint.csr.local.ipv4_address)
            vars.add('csr_ipv4_mask', endpoint.csr.local.ipv4_mask)
            vars.add('csr_ul_interface_name', endpoint.csr.link.interface_name)
            vars.add('csr_ul_interface_number', endpoint.csr.link.interface_number)
            ul_interface = str(endpoint.csr.link.interface_name) + str(endpoint.csr.link.interface_number)
            # self.log.info('CSR UL INTERFACE: ', ul_interface)
            vars.add('csr_ul_interface', ul_interface)
            vars.add('csr_ul_ipv4_address', endpoint.csr.link.ipv4_address)
            vars.add('csr_ul_ipv4_mask', endpoint.csr.link.ipv4_mask)
            # "link to PE / {$PE} - {$PE_INT_NAME}</description>"
            ul_interface_description = endpoint.er.device + " - " + str(endpoint.er.link.interface_name) + str(endpoint.er.link.interface_number)
            vars.add('csr_ul_interface_description', ul_interface_description)

            # self.log.info('ER DEVICE: ', endpoint.er.device)
            vars.add('er_device', endpoint.er.device)
            vars.add('er_interface_name', endpoint.er.link.interface_name)
            vars.add('er_interface_number', endpoint.er.link.interface_number)
            # "link to CSR / {$CSR} - {$CSR_INT_NAME}</description>"
            interface_description = endpoint.csr.device + " - " + ul_interface
            vars.add('er_interface_description', interface_description)
            vars.add('er_ipv4_address', endpoint.er.link.ipv4_address)
            vars.add('er_ipv4_mask', endpoint.er.link.ipv4_mask)

            ########## BASE CONFIGURATION SECTION ########
            csr_mgmt_ip = endpoint.csr.mgmt_ipv4_address
            vars.add('csr_mgmt_ipv4_address', csr_mgmt_ip)
            name = "Base_Config"+endpoint.csr.device
            vars.add('name', name)
            vars.add('csr_hostname', "mobile-"+service.name+"-csr1") # Probably this needs to be improved?
            self.log.info('Adding Base Configuration: ', name)
            template.apply('ba_base_conf_rfs-template', vars)

            ########## COMMUNITY SET SECTION ########
            name = "Communityset"+endpoint.csr.device
            vars.add('name', name)
            self.log.info('Adding Community Sets: ', name)
            template.apply('ba_rpl_communityset_rfs-template', vars)

            ########## PREFIX SET SECTION ########
            name = "Prefixset"+endpoint.csr.device
            vars.add('name', name)
            self.log.info('Adding Prefix Sets: ', name)
            template.apply('ba_rpl_prefixset_rfs-template', vars)

            ########## RPL SECTION ########
            name = "RPL"+endpoint.csr.device
            vars.add('name', name)
            self.log.info('Adding RPLs: ', name)
            template.apply('ba_rpl_bgp_rfs-template', vars)

            ########## ba-bgp SECTION ########
            vars.add('m3_area', endpoint.csr.m3_area)
            name = "BGP-"+endpoint.csr.m3_area+"-"+endpoint.csr.device
            vars.add('name', name)
            self.log.info('DOING BGP: ', name)
            template.apply('ba_bgp_rfs-template', vars)

            ########## ba-isis SECTION ########
            name = "ISIS-"+endpoint.csr.device+"-"+endpoint.id
            vars.add('name', name)
            result = "49.0002.{}.{}.{}.00".format(*[''.join(map(lambda x: x.zfill(3), csr_mgmt_ip.split('.')))[i:i+4] for i in range(0, 12, 4)])
            vars.add('net_id', result)
            self.log.info('DOING ISIS: ', name)
            template.apply('ba_isis_rfs-template', vars)

            ########## MPLS SECTION ########
            name = "MPLS-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('DOING MPLS: ', name)
            template.apply('ba_mpls_rfs-template', vars)

            ########## QOS SECTION - CLASS MAPS and POLICY MAPS ########
            ########## INTERFACE POLICY SECTION ########
            vars.add('device', endpoint.csr.device)
            vars.add('interface_name', endpoint.csr.local.interface_name)
            vars.add('interface_number', endpoint.csr.local.interface_number)
            vars.add('police_value', endpoint.csr.police_value)
            vars.add('police_unit', endpoint.csr.police_unit)
            # The Policy Maps BA-ACCESS-IN and BA-ACCESS and all the Class Maps they use must be present in the invemtory before this
            # Add BA-ACCESS
            vars.add('policy_map_name', "BA-ACCESS")
            name = "BA-ACCESS-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('DOING Policy Map BA-ACCESS: ', name)
            template.apply('ba_qos_rfs-template', vars)
            # Add BA-ACCESS-IN
            vars.add('policy_map_name', "BA-ACCESS-IN")
            name = "BA-ACCESS-IN-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('DOING Policy Map BA-ACCESS-IN: ', name)
            template.apply('ba_qos_rfs-template', vars)
            # Add BA-ACCESS-IN to the interface
            name = "BA-ACCESS-IN_INTERFACE_POLICY-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Attaching Policy Map BA-ACCESS-IN to csr IF: ', name)
            template.apply('ba_interface_qos_rfs-template', vars)

            vars.add('policy_map_name', "CORE-IN")
            vars.add('interface_name', endpoint.csr.link.interface_name)
            vars.add('interface_number', endpoint.csr.link.interface_number)
            name = "CORE-IN-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            # The Policy Map CORE-IN and all the Class Maps it uses must be present in the invemtory before this
            self.log.info('DOING Policy Map CORE-IN: ', name)
            template.apply('ba_qos_rfs-template', vars)
            name = "CORE-IN_INTERFACE_POLICY-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Attaching Policy Map CORE-IN to csr IF: ', name)
            template.apply('ba_interface_qos_rfs-template', vars)

            if not service.only_CSR:
                vars.add('device', endpoint.er.device)
                vars.add('policy_map_name', "CORE-IN")
                vars.add('interface_name', endpoint.er.link.interface_name)
                vars.add('interface_number', endpoint.er.link.interface_number)
                """ name = "DL_CM_PM-"+endpoint.er.device+"-"+str(endpoint.id)
                vars.add('name', name)
                self.log.info('DOING Policy Map CORE-IN: ', name)
                template.apply('ba_qos_rfs-template', vars) """
                name = "DL_INTERFACE_POLICY-"+endpoint.er.device+"-"+str(endpoint.id)
                vars.add('name', name)
                self.log.info('Attaching Policy Map CORE-IN to csr IF: ', name)
                template.apply('ba_interface_qos_rfs-template', vars)

            ########## L3VPN, ba-vrf SECTION ########
            import_rt_index_1 = 0
            import_rt_index_2 = 0
            import_rt_index_3 = 0
            import_rt_index_4 = 0
            import_rt_index_5 = 0
            export_rt_index_1 = 0
            export_rt_index_2 = 0
            export_rt_index_3 = 0
            export_rt_index_4 = 0
            export_rt_index_5 = 0
            rt_count = 1
            for irti in endpoint.imprti:
                if rt_count == 1:
                    import_rt_index_1 = irti.import_rt_index
                if rt_count == 2:
                    import_rt_index_2 = irti.import_rt_index
                if rt_count == 3:
                    import_rt_index_3 = irti.import_rt_index
                if rt_count == 4:
                    import_rt_index_4 = irti.import_rt_index
                if rt_count == 5:
                    import_rt_index_5 = irti.import_rt_index
                rt_count += 1
            rt_count = 1
            for erti in endpoint.exprti:
                if rt_count == 1:
                    export_rt_index_1 = erti.export_rt_index
                if rt_count == 2:
                    export_rt_index_2 = erti.export_rt_index
                if rt_count == 3:
                    export_rt_index_3 = erti.export_rt_index
                if rt_count == 4:
                    export_rt_index_4 = erti.export_rt_index
                if rt_count == 5:
                    export_rt_index_5 = erti.export_rt_index
                rt_count += 1
            vars.add('import_rt_index_1', import_rt_index_1)
            vars.add('import_rt_index_2', import_rt_index_2)
            vars.add('import_rt_index_3', import_rt_index_3)
            vars.add('import_rt_index_4', import_rt_index_4)
            vars.add('import_rt_index_5', import_rt_index_5)
            vars.add('export_rt_index_1', export_rt_index_1)
            vars.add('export_rt_index_2', export_rt_index_2)
            vars.add('export_rt_index_3', export_rt_index_3)
            vars.add('export_rt_index_4', export_rt_index_4)
            vars.add('export_rt_index_5', export_rt_index_5)
            template.apply('ba_vrf_rfs-template', vars)

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
        self.register_service('ba_l3vpn-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
