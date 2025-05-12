static IP 주소 생성 시, Assembly가 설정하는 방법과 cloud-init을 사용할 경우가 서로 충돌되지 않도록 지정

cloud-init 코드 없이 IP 주소 할당

```yaml
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      image: linux-template
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'
```

## 네트워크 할당 명령이 포함되지 않은 cloud-init 설정

참고: vSphere 사용자 지정 규격은 customizeGuestOs 속성을 true로 설정하거나 customizeGuestOs 속성을 생략해도 적용됩니다.

```yaml
### ubuntu
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      image: ubuntu-template
      customizeGuestOs: true
      cloudConfig: |
        #cloud-config
        ssh_pwauth: yes
        chpasswd:
          list: |
            root:Pa$$w0rd
          expire: false
        write_files:
          - path: /tmpFile.txt
            content: |
              ${resource.wpnet.dns}
        runcmd:
          - hostnamectl set-hostname --pretty ${self.resourceName}
          - touch /etc/cloud/cloud-init.disabled
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'
```

```yaml
### CentOS
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      image: centos-template
      customizeGuestOs: true
      cloudConfig: |
        #cloud-config
        write_files:
          - path: /test.txt
            content: |
              deploying in power off.
              then rebooting.
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'
```

## 네트워크 할당 명령이 포함된 cloud-init 코드

customizeGuestOs 속성은 false입니다.

```yaml
### ubuntu
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      image: ubuntu-template
      customizeGuestOs: false
      cloudConfig: |
        #cloud-config
        write_files:
          - path: /etc/netplan/99-installer-config.yaml
            content: |
              network:
                version: 2
                renderer: networkd
                ethernets:
                  ens160:
                    addresses:
                      - ${resource.DBTier.networks[0].address}/${resource.wpnet.prefixLength}
                    gateway4: ${resource.wpnet.gateway}
                    nameservers:
                      search: ${resource.wpnet.dnsSearchDomains}
                      addresses: ${resource.wpnet.dns}
        runcmd:
          - netplan apply
          - hostnamectl set-hostname --pretty ${self.resourceName}
          - touch /etc/cloud/cloud-init.disabled
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'

### CentOS
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      image: centos-template
      customizeGuestOs: false
      cloudConfig: |
        #cloud-config
        ssh_pwauth: yes
        chpasswd:
          list: |
            root:VMware1!
          expire: false
        runcmd:
          - nmcli con add type ethernet con-name 'custom ens192' ifname ens192 ip4 ${self.networks[0].address}/${resource.wpnet.prefixLength} gw4 ${resource.wpnet.gateway}
          - nmcli con mod 'custom ens192' ipv4.dns "${join(resource.wpnet.dns,' ')}"
          - nmcli con mod 'custom ens192' ipv4.dns-search "${join(resource.wpnet.dnsSearchDomains,',')}"
          - nmcli con down 'System ens192' ; nmcli con up 'custom ens192'
          - nmcli con del 'System ens192'
          - hostnamectl set-hostname --static `dig -x ${self.networks[0].address} +short | cut -d "." -f 1`
          - hostnamectl set-hostname --pretty ${self.resourceName}
          - touch /etc/cloud/cloud-init.disabled
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'
```

## 배포가 참조된 이미지에 기반하는 경우, 할당 명령 포함된 cloud-init 코드

customizeGuestOs 속성은 false입니다.

또한 클라우드 템플릿에 사용자 지정을 차단하는 ovfProperties 속성을 포함해서는 안 됩니다.

```yaml
resources:
  wpnet:
    type: Cloud.Network
    properties:
      name: wpnet
      networkType: public
      constraints:
        - tag: sqa
  DBTier:
    type: Cloud.vSphere.Machine
    properties:
      flavor: small
      imageRef: 'https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64.ova'
      customizeGuestOs: false
      cloudConfig: |
        #cloud-config
        ssh_pwauth: yes
        chpasswd:
          list: |
            root:Pa$$w0rd
            ubuntu:Pa$$w0rd
          expire: false
        write_files:
          - path: /etc/netplan/99-netcfg-vrac.yaml
            content: |
              network:
                version: 2
                renderer: networkd
                ethernets:
                  ens192:
                    dhcp4: no
                    dhcp6: no
                    addresses:
                      - ${resource.DBTier.networks[0].address}/${resource.wpnet.prefixLength}
                    gateway4: ${resource.wpnet.gateway}
                    nameservers:
                      search: ${resource.wpnet.dnsSearchDomains}
                      addresses: ${resource.wpnet.dns}
        runcmd:
          - netplan apply
          - hostnamectl set-hostname --pretty ${self.resourceName}
          - touch /etc/cloud/cloud-init.disabled
      networks:
        - name: '${wpnet.name}'
          assignment: static
          network: '${resource.wpnet.id}'
```
