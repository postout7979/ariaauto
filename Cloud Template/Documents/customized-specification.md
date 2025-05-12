```yaml
resources:
  WebTier:
    type: Cloud.vSphere.Machine    
    properties:     
        name: wordpress      
        cpuCount: 2
        totalMemoryMB: 1024
        imageRef: 'Template: ubuntu-18.04'      
        **customizationSpec: 'cloud-assembly-linux'    ### <<<< here**      
        folderName: '/Datacenters/Datacenter/vm/deployments'
```
