Cloud

```yaml
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
```

## Zone

```yaml
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
```

## Flavor

```yaml
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
    title: VM Spec
```

## Image

```yaml
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
```

## Network

```yaml
net:
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
```

## Count

```yaml
  count:
    type: integer
    minimum: 1
    maximum: 3
    default: 1
    title: Web VM Count
```

## Version

```yaml
  version:
    type: string
    enum:
      - 5.0.7
      - 5.1.3
      - 5.2.4
    default: 5.2.4
    title: Wodpress Version
```

## Password

```yaml
  password:
    type: string
    title: Password
```

---

## Network

```yaml
  net:
    type: Cloud.Network
    properties:
      name: wp-net
      networkType: '${input.net=="dev"?"routed":(input.net=="dep"?"outbound":"existing")}'
      constraints:
        - tag: 'net:${input.net}'
```

## Load Balancer

```yaml
  lb:
    type: Cloud.LoadBalancer
    properties:
      name: wp-lb
      network: '${resource.net.id}'
      instances:
        - '${resource.web.id}'
      internetFacing: '${input.cloud=="vmw"?"false":"true"}'
      routes:
        - protocol: HTTP
          port: '80'
          instanceProtocol: HTTP
          instancePort: '80'
          healthCheckConfiguration:
            protocol: TCP
            port: '80'
            intervalSeconds: 10
            timeoutSeconds: 5
            unhealthyThreshold: 5
            healthyThreshold: 2
```

## Machine

```yaml
# Created by Quickstart/Setup Cloud wizard.
formatVersion: 1
inputs:
  cpuCount:
    type: integer
    description: Number of virtual processors
    default: 1
  totalMemoryMB:
    type: integer
    description: Machine virtual memory size in Megabytes
    default: 1024
resources:
  Cloud_Network_1:
    type: Cloud.Network
    properties:
      name: QSNetwork
      networkType: existing
      constraints:
        - tag: 'account:vmk-vcsa01a.vmk.local / SDDC-Datacenter-1'
  Cloud_vSphere_Machine_1:
    type: Cloud.vSphere.Machine
    properties:
      imageRef: Centos7_template
      cpuCount: '${input.cpuCount}'
      totalMemoryMB: '${input.totalMemoryMB}'
      cloudConfig: null
      customizationSpec: null
      constraints:
        - tag: 'account:vmk-vcsa01a.vmk.local / SDDC-Datacenter-1'
      networks:
        - network: '${resource.Cloud_Network_1.id}'
          assignment: static
```
