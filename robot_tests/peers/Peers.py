# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   02-06-2022 21:48:42
# @Email:  rdireito@av.it.pt
# @Last Modified by:   Rafael Direito
# @Last Modified time: 10-06-2022 10:02:51
# @Description: 


import paramiko
import statistics
import os
import ipaddress
from aux.nods_information_parser import NetworkInformationParser 


network_info = os.getenv('peers_network_info')
host1 = "ns_index=1,vnf_index=2,vdu_index=1,interface_index=1,field=ip-address"
username1 = "ubuntu"
password1 = "ubuntu"
host2 = "ns_index=1,vnf_index=3,vdu_index=1,interface_index=1,field=ip-address"
username2 = "ubuntu"
password2 = "ubuntu"

net_information_parser = NetworkInformationParser(network_info)

host1_ip = net_information_parser.get_field_info(host1)
host2_ip = net_information_parser.get_field_info(host2)


def install_peer_dependencies(peer_client):
    stdin, stdout, stderr = peer_client.exec_command(
        "sudo apt install python3-pip -y &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()

    # control
    if status_code != "0": return False
    
    stdin, stdout, stderr = peer_client.exec_command(
        f"sudo python3 -m pip install wgconfig==0.2.2 &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()

    # control
    if status_code != "0": return False

    print("Installed all dependencies") 
    return True

def get_toolkit(peer_client):
    url = "https://raw.githubusercontent.com/rafael-direito/netsoft2-demo/main"\
        "/aux/wg_tolkit.py"
        
    stdin, stdout, stderr = peer_client.exec_command(
        f"cd ~/ && wget {url} ; echo $?"
    )
    status_code = stdout.read().decode().strip()

    # control
    if status_code != "0":
        return False
    
    print("Got Toolkit")
    return True


def remove_toolkit(peer_client):
    stdin, stdout, stderr = peer_client.exec_command(
        f"cd ~/ && rm -rf wg_tolkit.py.* ; echo $?"
    )
    status_code = stdout.read().decode().strip()
    # control
    if status_code != "0":
        return False

    print("Removed Toolkit")
    return True


def get_wg_address(peer_client):
    stdin, stdout, stderr = peer_client.exec_command(
        f"sudo cat /etc/wireguard/wg0.conf | grep Address | awk '{{print $3}}'"
    )
    address = stdout.read().decode().strip()
    return address


def get_wg_public_key(peer_client):
    stdin, stdout, stderr = peer_client.exec_command(
        f"sudo cat /etc/wireguard/publickey"
    )
    public_key = stdout.read().decode().strip()
    return public_key

    
def create_peer_connection(peer1_client, peer2_client):
    
    # Get peer1 Data
    peer1_enpoint = peer1_client.get_transport().getpeername()[0] + ":51820"
    peer1_public_key = get_wg_public_key(peer1_client)
    peer1_address = get_wg_address(peer1_client)
    peer1_wg_network = ipaddress.IPv4Interface(peer1_address).network
    peer1_wg_ip = ipaddress.IPv4Interface(peer1_address).ip
    
    #Get peer2 Data
    peer2_enpoint = peer2_client.get_transport().getpeername()[0] + ":51820"
    peer2_public_key = get_wg_public_key(peer2_client)
    peer2_address = get_wg_address(peer2_client)
    peer2_wg_network = ipaddress.IPv4Interface(peer2_address).network
    peer2_wg_ip = ipaddress.IPv4Interface(peer2_address).ip
    
    # Add peer2 to peer1
    stdin, stdout, stderr = peer1_client.exec_command(
        f"sudo wg-quick down wg0 ; sudo python3 ~/wg_tolkit.py add_peer " \
        f"{peer2_public_key} {peer2_enpoint} {peer2_wg_network} ; sudo "\
        "wg-quick up wg0"
    )
    stdout = stdout.read().decode().strip()
    print(f"Result of listing peer2 as peer of peer1: {stdout}")
    
    # control
    if "success" not in stdout:
        return False
    
    # Add peer1 to peer2
    stdin, stdout, stderr = peer2_client.exec_command(
        f"sudo wg-quick down wg0 ; sudo python3 ~/wg_tolkit.py add_peer "\
        f"{peer1_public_key} {peer1_enpoint} {peer1_wg_network} ; sudo "\
        "wg-quick up wg0"
    )
    stdout = stdout.read().decode().strip()
    print(f"Result of listing peer1 as peer of peer2: {stdout}")
    
    # control
    if "success" not in stdout:
        return False
    
    # Test connection from peer1 to peer2 
    stdin, stdout, stderr = peer1_client.exec_command(
        f"ping -c 5 {peer2_wg_ip} -W 1 -c 5  &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()
   
    # control
    if status_code != "0":
        return False
    
    # Test connection from peer2 to peer1
    stdin, stdout, stderr = peer2_client.exec_command(
        f"ping -c 5 {peer1_wg_ip} -W 1 -c 5  &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()
    
    print(f"Connectivity status: {'ok' if status_code=='0' else 'fail'}")

    # control
    if status_code != "0":
        return False
    
    return True
     
     
        
def delete_peer_connection(peer1_client, peer2_client):
    
    # Get peer1 Data
    peer1_public_key = get_wg_public_key(peer1_client)
    peer1_address = get_wg_address(peer1_client)
    peer1_wg_ip = ipaddress.IPv4Interface(peer1_address).ip

    #Get peer2 Data
    peer2_public_key = get_wg_public_key(peer2_client)
    peer2_address = get_wg_address(peer2_client)
    peer2_wg_ip = ipaddress.IPv4Interface(peer2_address).ip

    # Remove peer2 from peer1
    stdin, stdout, stderr = peer1_client.exec_command(
        f"sudo wg-quick down wg0 ; sudo python3 ~/wg_tolkit.py delete_peer " \
        f"{peer2_public_key} ; sudo wg-quick up wg0"
    )
    stdout = stdout.read().decode().strip()
    print(f"Result of removing peer2 from peer1's peers: {stdout}")

    # control
    if "success" not in stdout:
        return False

    # Remove peer1 from peer2
    stdin, stdout, stderr = peer2_client.exec_command(
        f"sudo wg-quick down wg0 ; sudo python3 ~/wg_tolkit.py delete_peer " \
        f"{peer1_public_key} ; sudo wg-quick up wg0"
    )
    stdout = stdout.read().decode().strip()
    print(f"Result of removing peer1 from peer2's peers: {stdout}")
    
    # control
    if "success" not in stdout:
        return False
    
    
    # Test connection from peer1 to peer2 
    stdin, stdout, stderr = peer1_client.exec_command(
        f"ping -c 5 {peer2_wg_ip} -W 1 -c 5  &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()
    
    # control
    if status_code == "0":
        return False
    
    # Test connection from peer2 to peer1
    stdin, stdout, stderr = peer2_client.exec_command(
        f"ping -c 5 {peer1_wg_ip} -W 1 -c 5  &>/dev/null ; echo $?"
    )
    status_code = stdout.read().decode().strip()
    
    print(f"Connectivity status: {'ok' if status_code!='0' else 'fail'}")

    # control
    if status_code == "0":
        return False
    
    # Remove toolkits
    if not remove_toolkit(peer1_client): return False
    if not remove_toolkit(peer2_client):return False
    
    return True
    
     
def peers():
    client1 = paramiko.SSHClient()
    client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client2 = paramiko.SSHClient()
    client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client1.connect(
            hostname=host1_ip, 
            username=username1, 
            password=password1
            )
        client2.connect(
            hostname=host2_ip, 
            username=username2,
            password=password2
        )
        print("Connection to hosts has been established")
    except Exception as e:
        print(f"[!] Cannot connect to the SSH Server - {e}")
        return False

    if not install_peer_dependencies(client1): return False
    if not install_peer_dependencies(client2): return False
    
    # Get toolkits
    if not get_toolkit(client1): return False
    if not get_toolkit(client2):
        return False
    
    create_ok = create_peer_connection(client1, client2)
    delete_ok = delete_peer_connection(client1, client2)
    
    print("create_ok", create_ok)
    print("delete_ok", delete_ok)
    return create_ok and delete_ok

if __name__ == '__main__':
    peers()
