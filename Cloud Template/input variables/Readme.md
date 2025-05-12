## 입력 매개 변수를 사용자가 입력 선택
```yaml
inputs:
  wp-size:
    type: string
    enum:
      - small
      - medium
    description: Size of Nodes
    title: Node Size
  wp-image:
    type: string
    enum:
      - coreos
      - ubuntu
    title: Select Image/OS
  wp-count:
    type: integer
    default: 2
    maximum: 5
    minimum: 2
    title: Wordpress Cluster Size
    description: Wordpress Cluster Size (Number of nodes)
```


## 입력 매개 변수를 참조

```yaml
resources:
  WebTier:
    type: Cloud.Machine
    properties:
      name: wordpress
      flavor: '${input.wp-size}'
      image: '${input.wp-image}'
      count: '${input.wp-count}'
```

## 중첩된 입력 사용

```yaml
inputs:
  cluster:
    type: integer
    title: Cluster
    default: 1
    minimum: 1
    maximum: 4
  level:
    type: object
    properties:
      cpu:
        type: integer
        title: CPU
        default: 1
        minimum: 1
        maxmum: 4
      memory:
        type: integer
        title: memory
        default: 2048
        minimum: 2048
        maximum: 8192

```

## 중첩된 입력 매개 변수를 참조

```yaml
resources:
  Disk_1:
    type: Cloud.vSphere.Disk
    allocatePerInstance: true
    properties:
      capacityGb: 1
      count: ${input.cluster}
  Machine_1:
    type: Cloud.vSphere.Machine
    allocatePerInstance: true
    properties:
      totalMemoryMB: ${input.level.memory}
      attachedDisks:
        - source: ${slice(resource.Disk_1[*].id, count.index, count.index + 1)[0]}
      count: ${input.cluster}
      imageRef: ubuntu
      cpuCount: ${input.level.cpu}
```

## 열거형이 포함된 예시

```yaml
  image:
    type: string
    title: Operating System
    description: The operating system version to use.
    enum:
      - ubuntu 16.04
      - ubuntu 18.04
    default: ubuntu 16.04

  shell:
    type: string
    title: Default shell
    Description: The default shell that will be configured for the created user.
    enum:
      - /bin/bash
      - /bin/sh
```

## 최소 및 최대 정수

```yaml
count:
  type: integer
  title: Machine Count
  description: blah blah
  maximum: 5
  minimum: 1
  default: 1
 
```

## 개체 어레이

```yaml
tags:
  type: array
  title: Tags
  items:
    type: object
    properties:
      key:
        type: string
        title: key
      value:
        type: string
        title: Value
        
```

## 친숙한 이름의 문자열

```yaml
platform:
  type: string
  oneOf:
    - title: AWS
    - const: platform:aws
    - title: Azure
    - const: platform:azure
    - title: vShere
    - const: platform:vsphere
  default: platform:vSphere
```

## 패턴 유효성 검사가 포함된 문자열

```yaml
username:
  type: string
  title: Username
  pattern: ^[a-zA-Z]+$
```

## 문자열을 암호로

```yaml
password:
  type: string
  title: Password
  encrypted: true
  writeonly: true
 
```

## 문자열을 텍스트 영역으로

```yaml
ssh_public_key:
  type: string
  title: SSH public key
  maxLength: 256
```

## 부울

```yaml
public_ip:
  type: boolean
  title: Assign public IP
  default: false
```

## 날짜 및 시간 일정 선택기

```yaml
leaseDate:
  tytpe: string
  title: Lease date
  format: date-time
```
