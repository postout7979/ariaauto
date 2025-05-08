function Handler($context, $inputs) {
    $inputsString = $inputs | ConvertTo-Json -Compress
    $tmpl_pass = $context.getSecret($inputs.customProperties.tmpl_pass)
    $tmpl_user = $inputs.customProperties.tmpl_user
    $mioSegreto = $context.getSecret($inputs.customProperties.mioSegreto)   
    $vcuser = $context.getSecret($inputs.vcUsername)
    $vcpassword = $context.getSecret($inputs.vcPassword)  
    $vcfqdn = $context.getSecret($inputs.customProperties.vcfqdn)
    $vrss = $context.getSecret($inputs.vrss) 

    $name = $inputs.resourceNames[0]
    $hostname = $inputs.customProperties.hostname
    
    write-host $tmpl_pass
    write-host $tmpl_user
    write-host $mioSegreto
    write-host $vcuser
    write-host $vcpassword
    write-host $vcfdqn
    write-host $vrss
    write-host $name
    write-host $hostname

    Connect-VIServer $vcfqdn -User $vcuser -Password $vcpassword -Force
    write-host “Waiting for VM Tools to Start”
    do {
    $toolsStatus = (Get-vm -name $name | Get-View).Guest.ToolsStatus
    write-host $toolsStatus
    sleep 3
    } until ( $toolsStatus -eq ‘toolsOk’ )
    $vm = Get-vm -name $name
    $output = $inputs.customProperties.softwareName
    Write-Host "VM OS Type is "$output

    return $os_type

}


