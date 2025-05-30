```yaml
name: Custom Username and Password - CloudInit
version: v1
inputs:
  hostname:
    type: string
  username:
    type: string
    title: Username
    default: adminuser
  password:
    type: string
    title: Password
    encrypted: true
    default: VMware123!
resources:
  web1:
    type: Cloud.Machine
    networks:
      - name: '${Cloud_Network_1.name}'
    properties:
      count: 1
      image: Ubuntu
      constraints:
        - tag: 'cloud:vsphere'
      flavor: medium
      cloudConfig: |
        #cloud-config
        hostname: ${input.hostname}
        ssh_pwauth: yes
        chpasswd:
          list: |
            ${input.username}:${input.password}
          expire: false
        users:
          - default
          - name: ${input.username}
            passwd: ${input.password}
            lock_passwd: false
            sudo: ['ALL=(ALL) NOPASSWD:ALL']
            groups: [wheel, sudo, admin]
            shell: '/bin/bash'
        runcmd:
          - echo "Defaults:${input.username}
      hostname: '${input.hostname}'
      networks:
        - name: '${AppNetwork.name}'
  AppNetwork:
    type: Cloud.Network
    properties:
      name: LB
      networkType: existing
```
