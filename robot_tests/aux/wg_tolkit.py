# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   02-06-2022 21:49:18
# @Email:  rdireito@av.it.pt
# @Last Modified by:   Rafael Direito
# @Last Modified time: 02-06-2022 22:56:41
# @Description: 
import wgconfig
import sys

CONFIG_LOCATION = "/etc/wireguard/wg0.conf"
INTERFACE = "wg0.conf"

def add_peer(public_key, endpoint, allowed_networks):
    
    allowed_networks = [
        net.strip() 
        for net in allowed_networks.split(",") 
        if len(net.strip()) != 0
    ]
    
    wireguard_config = wgconfig.WGConfig(CONFIG_LOCATION)
    wireguard_config.read_file()
    
    # if peer already exists, remove it
    wg_existing_peers = wireguard_config.peers
    if public_key in wg_existing_peers:
        wireguard_config.del_peer(public_key)
        
    wireguard_config.add_peer(public_key)
    
    wireguard_config.add_attr(
        public_key,
        'AllowedIPs',
        ", ".join(allowed_networks)
    )
    
    wireguard_config.add_attr(
        public_key,
        'Endpoint',
        endpoint
    )
    
    wireguard_config.write_file()
    
    print("Peer added with success!")
    
    
def delete_peer(public_key):
    
    wireguard_config = wgconfig.WGConfig(CONFIG_LOCATION)
    wireguard_config.read_file()
    
    # if peer already exists, remove it
    wg_existing_peers = wireguard_config.peers
    if public_key in wg_existing_peers:
        wireguard_config.del_peer(public_key)
        
    wireguard_config.write_file()
    print("Peer deleted with success!")
        
        

def main(args):
    
    action = args[0]
    public_key = None
    endpoint = None
    allowed_networks = None
    
    if action == "add_peer":
        public_key = args[1]
        endpoint = args[2]
        allowed_networks = args[3]
        add_peer(
            public_key=public_key,
            endpoint=endpoint,
            allowed_networks=allowed_networks
        )
        
    elif action == "delete_peer":
        public_key = args[1]
        delete_peer(
            public_key=public_key,
        )
    else:
        raise Exception("Invalid action")
        
    pass
    
if __name__ == "__main__":
   main(sys.argv[1:])
