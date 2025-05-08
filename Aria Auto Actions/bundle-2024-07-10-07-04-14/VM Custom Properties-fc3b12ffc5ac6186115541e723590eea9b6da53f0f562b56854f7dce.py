def handler(context, inputs):
    outputs = {}
    outputs["customProperties"] = inputs["customProperties"]
    
    # Cloud Assembly Infrastructure Secret passed as customProperties in Cloud Template
    tmpl_pass = context.getSecret(inputs["customProperties"]["tmpl_pass"])  
    
    # Project's Custom Property Secret 
    mioSegreto = context.getSecret(inputs["customProperties"]["mioSegreto"])
    
    # Script ABX Action Secret
    vcuser = context.getSecret(inputs["vcUsername"])
    vcpassword = context.getSecret(inputs["vcPassword"])
    vcfqdn = context.getSecret(inputs["customProperties"]["vcfqdn"])
    vrss = context.getSecret(inputs["vrss"])
    
    print("Cloud Assembly Infrastructure Secret passed as customProperties in Cloud Template : " + tmpl_pass)
    print("Project's Custom Property Secret : " + mioSegreto)

    print("Script Secret : " + vcuser + " / " + vcpassword + " vcenter : " + vcfqdn + " vRSS : " + vrss )

    print("Setting custom properties: {0}".format(outputs["customProperties"]))

    return outputs
    # Plain Input in Cloud Template mapped to plain customProperty
    #msg_public = inputs["customProperties"]["msg_public"]
    
    # Encrypted Input in Cloud Template mapped to encrypted customProperty
    #msg_private = context.getSecret(inputs["customProperties"]["msg_private"])
    
    # ABX Action Secret
    #msg = context.getSecret(inputs["abxsecret"])
    #outputs["customProperties"]["UserName"] = inputs["__metadata"]["userName"]
    #outputs["customProperties"]["EventTopic"] = inputs["__metadata"]["eventTopicId"]
    

    #print("Plain Input in Cloud Template mapped to plain customProperty : " + msg_public)
    #print("Encrypted Input in Cloud Template mapped to encrypted customProperty : " + msg_private)
    #print("ABX Action Secret : " + msg)