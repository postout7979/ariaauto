```yaml
formatVersion: 1
inputs:
  cloud:
    type: string
    oneOf:
      - title: VMware
        const: vmw
      - title: AWS
        const: aws
    default: vmw
    title: CSP
  zone:
    type: string
    oneOf:
      - title: Any
        const: ''
      - title: Zone 1
        const: '01'
      - title: Zone 2
        const: '02'
      - title: Zone 3
        const: '03'
    default: ''
    title: Zone
  network:
    type: string
    oneOf:
      - title: Static Service
        const: static
      - title: Service Production
        const: prod
      - title: Service Staging
        const: stage
      - title: Service Testing
        const: test
      - title: New Department Network (SNAT)
        const: dep
      - title: New Development Network (BGP)
        const: dev
    default: test
    title: Network
  flavor:
    type: string
    oneOf:
      - title: 1Core 2GRam
        const: small
      - title: 2Core 4GRam
        const: medium
      - title: 2Core 8GRam
        const: large
      - title: 4Core 16GRam
        const: xlarge
    default: medium
    title: Flavor
  image:
    type: string
    oneOf:
      - title: Ubuntu 18
        const: ubuntu18
      - title: Ubuntu 20
        const: ubuntu20
      - title: CentOS 7
        const: centos7
      - title: CentOS 8
        const: centos8
      - title: Redhat 7
        const: rhel7
      - title: Redhat 8
        const: rhel8
      - title: Windows 10
        const: windows10
    default: ubuntu18
    title: Image
  password:
    type: string
    title: Password
resources:
  net:
    type: Cloud.Network
    properties:
      name: net
      networkType: '${input.network=="dev"?"routed":(input.network=="dev"?"outbound":"existing")}'
      constraints:
        - tag: 'net:${input.network}'
  vm:
    type: Cloud.vSphere.Machine
    properties:
      name: vm
      image: '${input.image}'
      flavor: '${input.flavor}'
      networks:
        - network: '${resource.net.id}'
          assignment: '${input.cloud=="vmw"?"static":"dynamic"}'
      constraints:
        - tag: 'env:${input.cloud + input.zone}'
      customizationSpec: linux
      cloudConfig: |
        #cloud-config
        users:
          - name: ${env.requestedBy}
            sudo: ALL=(ALL) NOPASSWD:ALL
            shell: /bin/bash
            groups: adm, sudo, wheel, users
            ssh_authorized_keys:
              - ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAi/KwSSOccFcKrtavBQuNtvp8o7HX/iJGb/t1P8zCUkfjL7FFkVh7wnzvstPU49r5rxnp6umWJ5vXM2ImzJXVjePDcWtvRK4z3JIHJt275NHqlc0ETJrFNMD5B+Ad8yX1+pXEavK92mDvIapPC2e4HowQVoU+nDoJrOmZHduNcy1ZV62fLAzCaWwdTjFWng9ggZGIEdmT43I5nAaRYd9rkX0SZPciSoEA/CPliilNwcnUxBXMxZtauKc+3uuniQNMt5EpjQHVT8+206ysa0GUhwKbKg1av30tcmXLX7vJ5CzbZMjRzE9iztK688MetHnzMe/j8+Sm/bOPL+sa2zInlQ==
            lock_passwd: false
        chpasswd:
          list: |
            ${env.requestedBy}:${input.password}
          expire: false
        ssh_pwauth: true
        repo_update: true
        repo_upgrade: all
```
