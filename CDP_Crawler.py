from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
import json
import getpass

device_cdp={}
device_list=[]
Done_Devices=[]
Failed_Devices=[]
def GET_CDP_NEIGHBORS(device_ip,username,password):
    current_device_list=[]
    device_list.append(device_ip)
    print("Connecting to device : {} to get CDP neighbors".format(device_ip))
    Device={
        'device_type': "cisco_ios",
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    net_connect=ConnectHandler(**Device)
    output=net_connect.send_command("show cdp neigh detail", use_genie=True)
    output=dict(output)
    net_connect.disconnect()
    count=output["total_entries_displayed"]
    print("\n\n-- List of Connected Devices --")
    device_cdp[device_ip]=[]
    for i in range(1,count):
        neigh_device_id=output["index"][i]["device_id"]
        entry_address=output["index"][i]["entry_addresses"]
        port_id=output["index"][i]["port_id"]
        local_interface=output["index"][i]["local_interface"]
        if(len(list(entry_address.keys()))):
            entry_address=list(entry_address.keys())[0]
        else : 
            entry_address="N/A"
        print(local_interface +"  " + neigh_device_id +"  " + entry_address +"  " + port_id)
        device_cdp[device_ip].append( 
            {
                "local_interface": local_interface,
                "neigh_device_id": neigh_device_id,
                "entry_address": entry_address,
                "port_id": port_id
            }
        )
        current_device_list.append(entry_address)
    Done_Devices.append(device_ip)
    print("----------------------------------------------------------------")
    print("List of Done Devices : {}".format(Done_Devices))
    print("List of Failed Devices : {}".format(Failed_Devices))
    print("----------------------------------------------------------------")
    for ip in current_device_list:
        if(ip not in device_list):
            try:
                GET_CDP_NEIGHBORS(ip,username,password)
            except (AuthenticationException):
                print ('Authentication failure: ' + ip)
                Failed_Devices.append(ip)
                continue
            except (NetMikoTimeoutException):
                print ('Timeout to device: ' + ip)
                Failed_Devices.append(ip)
                continue
            except (EOFError):
                print ('End of file while attempting device ' + ip)
                Failed_Devices.append(ip)
                continue
            except (SSHException):
                print ('SSH Issue. Are you sure SSH is enabled? ' + ip)
                Failed_Devices.append(ip)
                continue
            except Exception as unknown_error:
                print ('Some other error: ' + str(unknown_error))
                Failed_Devices.append(ip)
                continue
    current_device_list=[]
#######END OF Function############
print(".:: LAN CDP Crawler ::.")
ip=input("Enter Switch ip Address : ")
username=input("Enter username : ")
password=getpass.getpass("Enter Password : ")

GET_CDP_NEIGHBORS(ip,username,password)
