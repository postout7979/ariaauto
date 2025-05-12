cloudConfig를 사용해서 프로비저닝 시 키를 배포도 가능

## 프로비저닝 시 key pair 생성

- Cloud Assembly 통해서 key pair 생성 지원
- remoteAccess 항목을 추가

```yaml
type: Cloud.Machine
properties:
  name: our-vm2
  image: Linux18
  flavor: small
  remoteAccess:
    authentication: generatedPublicPrivatekey
    username: testuser
```

- 참조: https://docs.vmware.com/kr/vRealize-Automation/8.11/Using-and-Managing-Cloud-Assembly/GUID-5A072C53-5355-4EF6-807C-A6CA20AC8BCF.html

## 자체 공용-개인 키 쌍 생성

```yaml
type: Cloud.Machine
properties:
  name: our-vm1
  image: Linux18
  flavor: small
  remoteAccess:
    authentication: publicPrivateKey
    sshKey: ssh-rsa Iq+5aQgBP3ZNT4o1baP5Ii+dstIcowRRkyobbfpA1mj9tslf qGxvU66PX9IeZax5hZvNWFgjw6ag+ZlzndOLhVdVoW49f274/mIRild7UUW... 
    username: testuser
    
```

- 원격 연결을 위한 로컬에서 접속

```yaml
ssh -i 키-이름 사용자-이름@시스템-ip
```

## 사용자 이름 및 암호 제공

```yaml
type: Cloud.Machine
properties:
  name: our-vm3
  image: Linux18
  flavor: small
  remoteAccess:
    authentication: usernamePassword
    username: testuser
    password: admin123
```
