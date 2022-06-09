# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   04-06-2022 12:25:45
# @Email:  rdireito@av.it.pt
# @Last Modified by:   Rafael Direito
# @Last Modified time: 09-06-2022 09:52:37
# @Description: 
import json
import base64

with open('my.json') as f:
    data = json.load(f)
    print(data)
    data_str = str(data)

    print(data_str)
    data_str = data_str.replace('\'', '\"')
    
    message_bytes = data_str.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    print(base64_message)

    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    print(message)

    res = json.loads(message)
    print(res)
    print(res["ns-id-1"]["vnf-id-1"]["vdu-id-1"]
          ["interface-id-1"]["ip-address"])
