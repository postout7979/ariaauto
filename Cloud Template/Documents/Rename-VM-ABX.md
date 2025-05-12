```yaml

```

<img width="1226" alt="image" src="https://github.com/user-attachments/assets/c3cba822-d996-405a-8fca-945344b6b7f3" />

<img width="1233" alt="image" src="https://github.com/user-attachments/assets/0736134d-698b-4076-8894-d8877fa29512" />


Action

```yaml
def handler(context, inputs):
    """Set a name for a machine

    :param inputs
    :param inputs.resourceNames: Contains the original name of the machine.
           It is supplied from the event data during actual provisioning
           or from user input for testing purposes.
    :param inputs.newName: The new machine name to be set.
    :return The desired machine name.
    """
    old_name = inputs["resourceNames"][0]
    new_name = inputs["customProperties"]["newName"]

    outputs = {}
    outputs["resourceNames"] = inputs["resourceNames"]
    outputs["resourceNames"][0] = new_name

    print("Setting machine name from {0} to {1}".format(old_name, new_name))

    return outputs

```

<img width="1734" alt="image" src="https://github.com/user-attachments/assets/b1cd28a8-f52a-4613-ad7f-c2d6e1d70722" />


\

Blueprint

```yaml
name: Rename VM ABX-Do-NOT-Modify
version: 1
formatVersion: 1
inputs:
  user:
    type: string
    title: Username for SSH
    description: The username you would like to usee for admin.
    default: demouser
  password:
    type: string
    pattern: "[a-z0-9A-Z@#$]+"
    encrypted: true
    default: vRealiz3!
    title: Admin Account Password
    description: The password you would like to use for the ocuser account.
  MachineName:
    type: string
    title: Name for the VM
    description: Enter Name for VM.
  environment:
    type: string
    enum:
      - AWS
      - Azure
      - vSphere
    default: vSphere
    title: Select Environment for Deployment
    description: Target Environment
resources:
  ubuntuserver:
    type: Cloud.Machine
    properties:
      image: Ubuntu-16
      flavor: Medium
      newName: ${input.MachineName}
      funny: Stuff
      folderName: '${input.environment == "VMC" ? "Workloads" : ""}'
      cloudConfig: |
        
        users:
          - name: ${input.user}
            sudo: ['ALL=(ALL) NOPASSWD:ALL']
            groups: sudo
            shell: /bin/bash

        runcmd:
          - USER=${input.user}
          - PASS=${input.password}
          - echo $USER:$PASS | /usr/sbin/chpasswd
          - echo $USER:$PASS | /usr/sbin/chpasswd
          - sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/g" /etc/ssh/sshd_config
          - service ssh reload
          - export cloudip=$(curl http://checkip.amazonaws.com/)
          - export onpremip=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
          - export ip4=${input.environment == "vSphere" ? "$onpremip" : (input.environment == "VMC" ? "$onpremip" : "$cloudip")}
          - echo $ip4 >> /tmp/environment.txt
          - echo "Done" >> /tmp/environment.txt
      constraints:
        - tag: ${"env:" + to_lower(input.environment)}
      networks:
        - name: ${resource.Cloud_Network_1.name}
          network: ${resource.Cloud_Network_1.id}
          assignPublicIpAddress: 1
  Cloud_Network_1:
    type: Cloud.Network
    properties:
      name: Field-Demo
      networkType: existing
      constraints:
        - tag: ${"env:" + to_lower(input.environment)}

```
