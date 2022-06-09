# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   02-06-2022 18:36:54
# @Email:  rdireito@av.it.pt
# @Last Modified by:   Rafael Direito
# @Last Modified time: 09-06-2022 11:49:03
# @Description: 

import paramiko
import os
import time
from aux.nods_information_parser import NetworkInformationParser


network_info = os.getenv('encryption_network_info', "eyJucy1pZC0xIjogeyJ2bmYtaWQtMSI6IHsidmR1LWlkLTEiOiB7ImludGVyZmFjZS1pZC0xIjogeyJuYW1lIjogImV0aDAiLCAiaXAtYWRkcmVzcyI6ICIxMC4wLjEzLjk5IiwgIm1hYy1hZGRyZXNzIjogImZhOjE2OjNlOjkxOjczOjdhIiwgInR5cGUiOiAiUEFSQVZJUlQifSwgImludGVyZmFjZS1pZC0yIjogeyJuYW1lIjogImV0aDEiLCAiaXAtYWRkcmVzcyI6ICIiLCAibWFjLWFkZHJlc3MiOiAiIiwgInR5cGUiOiAiIn19fSwgInZuZi1pZC0yIjogeyJ2ZHUtaWQtMSI6IHsiaW50ZXJmYWNlLWlkLTEiOiB7Im5hbWUiOiAiZXRoMCIsICJpcC1hZGRyZXNzIjogIjEwLjAuMTMuMTIiLCAibWFjLWFkZHJlc3MiOiAiZmE6MTY6M2U6Y2Q6OWE6M2QiLCAidHlwZSI6ICJQQVJBVklSVCJ9LCAiaW50ZXJmYWNlLWlkLTIiOiB7Im5hbWUiOiAiZXRoMSIsICJpcC1hZGRyZXNzIjogIiIsICJtYWMtYWRkcmVzcyI6ICIiLCAidHlwZSI6ICIifX19LCAidm5mLWlkLTMiOiB7InZkdS1pZC0xIjogeyJpbnRlcmZhY2UtaWQtMSI6IHsibmFtZSI6ICJldGgwIiwgImlwLWFkZHJlc3MiOiAiMTAuMC4xMy4yMjQiLCAibWFjLWFkZHJlc3MiOiAiZmE6MTY6M2U6YzI6OTI6MjciLCAidHlwZSI6ICJQQVJBVklSVCJ9LCAiaW50ZXJmYWNlLWlkLTIiOiB7Im5hbWUiOiAiZXRoMSIsICJpcC1hZGRyZXNzIjogIiIsICJtYWMtYWRkcmVzcyI6ICIiLCAidHlwZSI6ICIifX19fX0=")

host1 = os.getenv('encryption_host1_ip', "ns_index=1,vnf_index=1,vdu_index=1,interface_index=1,field=ip-address")
username1 = os.getenv('encryption_host1_username')
password1 = os.getenv('encryption_host1_password')

host2 = os.getenv('encryption_host2_ip', "ns_index=1,vnf_index=2,vdu_index=1,interface_index=1,field=ip-address")
username2 = os.getenv('encryption_host2_username')
password2 = os.getenv('encryption_host2_password')

net_information_parser = NetworkInformationParser(network_info)

host1_ip = net_information_parser.get_field_info(host1)
host2_ip = net_information_parser.get_field_info(host2)


def get_log_file_name(prefix, interface):
    current_time = time.time()
    return f"{interface}_{prefix}_log_{current_time}.pcap"


def can_message_be_seen(client1, client2, http_server_ip, port, interface):
    message = "Hello NetSoft2022"
    log_filepath = get_log_file_name("public", interface)
    test_dir = "~/test"
    
    # 1. Create the files needed to run this test
    client1.exec_command(
        f"mkdir -p {test_dir} && cd {test_dir} && echo \"{message}\" > index.html"
    )
    
    # 2. Starting by Running an HTTP Server on port 8081
    # 2.1 Delete all processes running on port 8081
    client1.exec_command(
        "sudo kill -9 $(lsof -i :8081 | awk '{print $2}' | tail -n +2)"
    )
    
    # 2.2 Run python3 HTTP Server
    client1.get_transport().open_session().exec_command(
        f"cd {test_dir} && python3 -m http.server 8081 &>/dev/null &"
    )
    
    # 3. Start a Tcpdump on the public interface
    client1.get_transport().open_session().exec_command(
        f"sudo tcpdump -w {log_filepath} -n -A -i {interface} port {port} "
        "-s 65535 &>/dev/null &")
    
    # 4. Make a curl request to the server
    stdout = ""
    while message not in stdout:
        print("Waiting for the server to start...") 
        stdin, stdout, stderr = client2.exec_command(
            f"curl http://{http_server_ip}:8081")
        stdout = stdout.read().decode()
    print("Server Started!")
    print(f"Server Returned: {stdout.strip()}")

    time.sleep(5)
    
    # 5. Clean Up
    # 5.1 Stop the tcpdump
    client1.get_transport().open_session().exec_command(
        "sudo kill $(ps aux | grep tcpdump | awk '{print $2}')"
    )

    # 5.2 Stop the HTTP Server
    client1.exec_command(
        "sudo kill -9 $(lsof -i :8081 | awk '{print $2}' | tail -n +2)"
    )

    # 6. Get the Output and validate it
    # 6.1 Transform the pcap file to a txt one
    time.sleep(5)
    stdin, stdout, stderr = client1.exec_command(
        f"sudo tcpdump -n -A -i {interface} port {port} -r "\
        f"{log_filepath} >> {log_filepath.replace('pcap', 'txt')}"
    )
    stdout = stdout.read().decode()

    # 6.2.1 Get the content of the txt file
    stdin, stdout, stderr = client1.exec_command(
        f"cat {log_filepath.replace('pcap', 'txt')}")
    stdout = stdout.read().decode()
  
    
    # 7. Clean Up the Log Files
    client1.get_transport().open_session().exec_command(
        "sudo rm -rf *public_log*.txt *public_log*.pcap"
    )
    
    return message in stdout
    
    
def encryption():
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
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()

    print("When a curl is made to the public interface, can the message be seen in the public interface ?")
    curl_public_log_public = can_message_be_seen(client1, client2, host1_ip, "8081", "ens3")
    print(f"> {'Yes' if curl_public_log_public else 'No'}")
    
    print("When a curl is made to the WG interface, can the message be seen in the public interface ?")
    curl_wg_log_public = can_message_be_seen(client1, client2, "10.100.101.1", "51820", "ens3")
    print(f"> {'Yes' if curl_wg_log_public else 'No'}")
    
    print("When a curl is made to the WG interface, can the message be seen in the WG interface ?")
    curl_wg_log_wg = can_message_be_seen(client1, client2, "10.100.101.1", "8081",  "wg0")
    print(f"> {'Yes' if curl_wg_log_wg else 'No'}")

    return curl_public_log_public and not curl_wg_log_public and curl_wg_log_wg

if __name__ == '__main__':
    encryption()
