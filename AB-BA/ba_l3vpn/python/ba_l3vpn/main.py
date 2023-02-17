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

        # BA VRF Section
        vars.add('vrf_name', service.vrf_name)
        for endpoint in service.endpoint:
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
            # "link to PE / {$PE} - {$PE_INT_NAME}</description>"
            ul_interface_description = endpoint.er.device + " - " + str(endpoint.er.link.interface_name) + str(endpoint.er.link.interface_number)
            vars.add('csr_ul_interface_description', ul_interface_description)
            vars.add('csr_ul_ipv4_address', endpoint.csr.link.ipv4_address)
            vars.add('csr_ul_ipv4_mask', endpoint.csr.link.ipv4_mask)

            # self.log.info('ER DEVICE: ', endpoint.er.device)
            vars.add('er_device', endpoint.er.device)
            vars.add('er_interface_name', endpoint.er.link.interface_name)
            vars.add('er_interface_number', endpoint.er.link.interface_number)
            # "link to CSR / {$CSR} - {$CSR_INT_NAME}</description>"
            interface_description = endpoint.csr.device + " - " + ul_interface
            vars.add('er_interface_description', interface_description)
            vars.add('er_ipv4_address', endpoint.er.link.ipv4_address)
            vars.add('er_ipv4_mask', endpoint.er.link.ipv4_mask)

            ########## COMMUNITY SET SECTION ########
            vars.add('community_set_umpls', endpoint.csr.community_set_umpls)
            for cs in root.inventory.community_sets.community_set[endpoint.csr.community_set_umpls].rpl_community_set:
                vars.add('as_number', cs.part1)
                vars.add('set_number', cs.part2)
                name = "Communityset"+endpoint.csr.device+"-"+endpoint.csr.community_set_umpls+"-"+str(cs.part2)
                vars.add('name', name)
                template.apply('ba_rpl_communityset_rfs-template', vars)

            ########## PREFIX SET SECTION ########
            vars.add('prefix_set_umpls', endpoint.csr.prefix_set_umpls)
            for ps in root.inventory.prefix_sets.prefix_set[endpoint.csr.prefix_set_umpls].rpl_prefix_set:
                vars.add('prefix_set_ip', ps.prefix_set_ip)
                vars.add('prefix_set_mask1', ps.prefix_set_mask1)
                vars.add('prefix_set_operator', ps.prefix_set_operator)
                vars.add('prefix_set_mask2', ps.prefix_set_mask2)
                name = "Prefixset"+endpoint.csr.device+"-"+endpoint.csr.prefix_set_umpls+"-"+str(ps.prefix_set_ip)
                vars.add('name', name)
                template.apply('ba_rpl_prefixset_rfs-template', vars)

            template.apply('ba_rpl_bgp_rfs-template', vars)

            ########## ba-bgp SECTION ########
            csr_mgmt_ip = endpoint.csr.mgmt_ipv4_address
            vars.add('csr_mgmt_ipv4_address', csr_mgmt_ip)
            vars.add('paths_route_policy', endpoint.csr.paths_route_policy)
            vars.add('networks_route_policy', endpoint.csr.networks_route_policy)
            vars.add('ng_route_policy_in', endpoint.csr.ng_route_policy_in)
            vars.add('ng_route_policy_out', endpoint.csr.ng_route_policy_out)
            count = 0
            for rr in root.inventory.METRO3Areas.METRO3Area[endpoint.csr.m3_area].RR:
                count = count +1
                name = "BGP-"+endpoint.csr.m3_area+"-"+endpoint.csr.device+"-Neighbor"+str(count)
                vars.add('name', name)
                self.log.info('Service Name: ', name)
                self.log.info('RR address: ', rr.RR_ipv4_addr)
                vars.add('csr_neighbor_ipv4_address', rr.RR_ipv4_addr)
                vars.add('csr_neighbor_group_name', rr.neighbor_group_name)
                vars.add('csr_neighbor_description', rr.neighbor_description)
                vars.add('agg_device', rr.agg_device)
                vars.add('agg_neighbor_ipv4_address', endpoint.csr.mgmt_ipv4_address)
                vars.add('agg_neighbor_group_name', rr.neighbor_group_name)
                vars.add('agg_neighbor_description', rr.neighbor_description)
                template.apply('ba_bgp_rfs-template', vars)

            ########## ba-isis SECTION ########
            name = "ISIS-"+endpoint.csr.device+"-"+endpoint.id
            vars.add('name', name)
            result = "49.0002.{}.{}.{}.00".format(*[''.join(map(lambda x: x.zfill(3), csr_mgmt_ip.split('.')))[i:i+4] for i in range(0, 12, 4)])
            vars.add('net_id', result)
            template.apply('ba_isis_rfs-template', vars)

            ########## MPLS SECTION ########
            name = "MPLS-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_mpls_rfs-template', vars)

            ########## QOS SECTION - CLASS MAPS and POLICY MAPS ########
            ########## INTERFACE POLICY SECTION ########
            vars.add('device', endpoint.csr.device)
            vars.add('policy_map_name', endpoint.csr.vrf_policy_map)
            vars.add('interface_name', endpoint.csr.local.interface_name)
            vars.add('interface_number', endpoint.csr.local.interface_number)
            # self.log.info('POLICY MAP: ', endpoint.csr.vrf_policy_map)
            # self.log.info('INTERFACE NAME: ', endpoint.csr.local.interface_name)
            # self.log.info('INTERFACE NUMBER: ', endpoint.csr.local.interface_number)
            name = "VRF_CM_PM-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_qos_rfs-template', vars)
            name = "VRF_INTERFACE_POLICY-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_interface_qos_rfs-template', vars)

            vars.add('policy_map_name', endpoint.csr.uplink_policy_map)
            vars.add('interface_name', endpoint.csr.link.interface_name)
            vars.add('interface_number', endpoint.csr.link.interface_number)
            name = "UL_CM_PM-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_qos_rfs-template', vars)
            name = "UL_INTERFACE_POLICY-"+endpoint.csr.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_interface_qos_rfs-template', vars)

            vars.add('device', endpoint.er.device)
            vars.add('policy_map_name', endpoint.er.downlink_policy_map)
            vars.add('interface_name', endpoint.er.link.interface_name)
            vars.add('interface_number', endpoint.er.link.interface_number)
            name = "DL_CM_PM-"+endpoint.er.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_qos_rfs-template', vars)
            name = "DL_INTERFACE_POLICY-"+endpoint.er.device+"-"+str(endpoint.id)
            vars.add('name', name)
            template.apply('ba_interface_qos_rfs-template', vars)

            ########## L3VPN SECTION ########
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
