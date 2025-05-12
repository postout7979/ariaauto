# [Commented Cloud Template](https://vra-examples.github.io/#commentedcloudtemplate)

This blueprint shows various ways to enhance a blueprint via YAML with explanations of the various parameters. There are comments throughout for your refernce. You can clone this blueprint and then experiment a bit with YAML if you want. If you are totally new to YAML then you can visit https://yaml.org/ to get more familiar with it.

```yaml
name: Blueprint with Comments
# Dont forget to give your blueprint a useful name!
formatVersion: 1
version: 1
# version is needed if you are going to source control the blueprint in GIT.
inputs:
  # Inputs section is where you define inputs that the user will be able to choose from at deployment time.
  # There are a number of various methods by which we can present inputs to the user. Inputs can also influence
  # placement decisions and configuration. There are a few examples below of various input types and how to use them.
  platform:
    type: string
    # The inputs section is where we list out our inputs that the user can choose from at deployment time.
    title: Deploy to
    oneOf:
      # This particular section lists out the various cloud endpoints that the user can choose from. 
      # The input variable will be referenced in the resources section. Title is what the user sees, const is the tag for the endpoints.
      - title: AWS
        const: aws
      - title: Azure
        const: azure
      - title: vSphere
        const: vsphere
    default: vsphere
  image:
    type: string
    #String with enumeration -enum , enum and oneOf are slightly differnet in that oneOf allows for a friendly title.
    title: Operating System
    description: Which OS to use
    enum:
      - Ubuntu
      - Windows
  # Common situation where you can list your various Flavor Mappings, if a user chooses Ubuntu and the 
  # system deploys to AWS for instance, then the AMI that is listed in Flavor Mapping "Ubuntu" would be chosen for AWS. 
  dbenvsize:
    type: string
    enum:
      - Small
      - Large
  Mtags:
    type: array
    # Array of objects - syntax: $'{['key1', 'key2']} , try clicking the Test button and you will see how the array appears to a user during deployment.
    title: Tags
    description: tags to apply to machines
    items:
      type: object
      properties:
        key:
          type: string
          title: Key
        value:
          type: string
          title: Value
  username:
    type: string
    # Inputs like username and password allow the user to define these parameters at request time.
    # These types of inputs can also be helpful for configurations within cloud-init scripts, cloud-init is 
    # described below in the resources section of the blueprint.
    minLength: 4
    maxLength: 20
    pattern: '[a-z]+'
    title: Database Username
    description: Database Username
  userpassword:
    type: string
    pattern: '[a-z0-9A-Z@#$]+'
    encrypted: true
    title: Database Password
    description: Database Password
  databaseDiskSize:
    type: number
    # This input allows the user to choose the disk size.
    default: 4
    maximum: 10
    title: MySQL Data Disk Size
    description: Size of database disk
  clusterSize:
    # This clusersize will be refernced in a count.index input below in WebTier. 
    # If a user chooses small from the dropdown then only 2 machines will be deployed.
    type: string
    enum:
      - small
      - medium
      - large
    title: Wordpress Cluster Size
    description: Wordpress Cluster Size
  archiveDiskSize:
    type: number
    default: 4
    maximum: 10
    title: Wordpress Archive Disk Size
    description: Size of Wordpress archive disk
resources:
  # The resources section is where we configure the machines, networks, volumes and other objects that will get deployed.
  DBTier:
    type: Cloud.Machine
    properties:
      # Properties section is where parameterize and configure the resource. 
      name: mysql
      # Name of virtual machine
      # Image and Flavor could also be variables and inputs as well. # Image Mapping from the Infrastructure tab, 
      # this is one way that vRA abstracts various "clouds" so the system can be cloud agnostic.
      image: CloudImage
      # Specifies the cloud image, depending on where the machine goes will determine what image is actually used across 
      # clouds. Pretty neat!
      flavor: small
      # Flavor Mapping - basically t-shrirt sizing for multi-cloud.
      constraints:
        - tag: '${"cloud:" + to_lower(input.platform)}'
      # This constraint is using a tag that will specify the cloud, then lower case the input to match the tag case. 
      # there are other function operators besides to_lower, some of them are: to_upper, merge, trim, replace..
      tags: '${input.Mtags}'
      count: '${input.dbenvsize == "Small" ? 1 : 2}' # You can use conditions to determine things like size of the environment. 
      # In this example if you choose "small" then count = 1, if you choose the other option then it defaults to 2 machines. 
      # You could also do something like: '${input.count < 5 && input.size == 'small'} , or '${input.count < 2 ? "small" : "large}'. 
      networks:
        - name: '${resource.WP_Network.name}'
          #Resource variables let you bind to resource properties from other resources ex. - ${resource.app[0].id}
          network: '${resource.WP_Network.id}'
      remoteAccess:
        #remote access property enables you to specify a remote access mechanism for the deployed machine
        authentication: usernamePassword
        username: '${input.username}'
        password: '${input.userpassword}'
      ACMECorpID: 9333 #You can add custom properties to the YAML. Then these properties can be used to kick off an extensiblity subscription for instance. 
      # In the section below you will see a bit of code under a heading "cloudConfig", you can use cloud config to run commands in the Operating System of the machine , cross cloud. 
      # Examples include, setting a hostname, generating ssh private keys, installing packages.
      # For more information on cloud-init - https://cloudinit.readthedocs.io/en/latest/
      cloudConfig: |
        #cloud-config
        repo_update: true
        repo_upgrade: all

        packages:
         - mysql-server

        runcmd:
         - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf
         - service mysql restart
         - mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'mysqlpassword';"
         - mysql -e "FLUSH PRIVILEGES;"
      attachedDisks: []
  WebTier:
    type: Cloud.Machine
    properties:
      name: wordpress
      # Name of the virtual machine
      image: CloudImage
      # Image Mapping from the Infrastructure tab, this is one way that vRA abstracts "clouds" and become more agnostic.
      flavor: small
      # Flavor Mapping - basically t-shrirt sizing for multi-cloud.
      count: '${input.clusterSize== "small" ? 2 : (input.clusterSize == "medium" ? 3 : 4)}'
      # This is a cluster count index example, the two options are small, medium and large clusters. Small deploys 2 machines,
      # Medium deploys 3 machines , and it is implied that Large would deploy 4 machines so we do not need to specify large in the code
      tags:
        - key: cas.requestedBy
          value: '${env.requestedBy}' # Environmental variables can be helpful if you want to get info about the object displayed in the properties section of the deployment, other examples - {env.blueprintID}
      ACMECorpID: 9333
      constraints:
        - tag: '${"cloud:" + to_lower(input.platform)}' # This constaint will allow for the YAML to present a Upper-Case as display but the tags on the endpoints can be lower-case. 
      # This is important because the options in a list need to match the "case" of the tag.
      networks:
        - name: '${resource.WP_Network.name}'
          # This is a resource variable, lets you bind to resource properties from other resources, in this case the network that gets deployed.
          network: '${resource.WP_Network.id}'
      cloudConfig: |
        #cloud-config
        repo_update: true
        repo_upgrade: all

        packages:
          - apache2
          - php
          - php-mysql
          - libapache2-mod-php
          - php-mcrypt
          - mysql-client
         
        runcmd:
          - mkdir -p /var/www/html/mywordpresssite && cd /var/www/html && wget https://wordpress.org/latest.tar.gz && tar -xzf /var/www/html/latest.tar.gz -C /var/www/html/mywordpresssite --strip-components 1
          - i=0; while [ $i -le 5 ]; do mysql --connect-timeout=3 -h ${DBTier.networks[0].address} -u root -pmysqlpassword -e "SHOW STATUS;" && break || sleep 15; i=$((i+1)); done
          - mysql -u root -pmysqlpassword -h ${resource.DBTier.networks[0].address} -e "create database wordpress_blog;"
          - mv /var/www/html/mywordpresssite/wp-config-sample.php /var/www/html/mywordpresssite/wp-config.php
          - sed -i -e s/"define('DB_NAME', 'database_name_here');"/"define('DB_NAME', 'wordpress_blog');"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define('DB_USER', 'username_here');"/"define('DB_USER', 'root');"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define('DB_PASSWORD', 'password_here');"/"define('DB_PASSWORD', 'mysqlpassword');"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define('DB_HOST', 'localhost');"/"define('DB_HOST', '${resource.DBTier.networks[0].address}');"/ /var/www/html/mywordpresssite/wp-config.php
          - service apache2 reload
  WP_Network:
    type: Cloud.Network
    properties:
      name: WP_Network
      networkType: existing
# Parameter "networkType" selects an existing network in this case, you could also use a constraint tag to limit the network to a tagged network, for instance a "PCI" tagged network.
# There are other networkTypes, e.g., private or public. 
#****************************************************************************************************************************************************************
# Blueprints via API - example, you can create blueprints etc, or you can query to get input schema you are intending to request:
# GET https://api.mgmt.cloud.vmware.com/blueprint/api/blueprints/{blueprint_id}/inputs-schema
# Link to the Swagger Docs: https://www.mgmt.cloud.vmware.com/blueprint/api/swagger/swagger-ui.html
```

```yaml
# *************************************************************************
# 
# This WordPress cloud template is enhanced with comments to explain its 
# parameters.
# 
# Try cloning it and experimenting with its YAML code. If you're new to 
# YAML, visit yaml.org for general information.
# 
# The cloud template deploys a minimum of 3 virtual machines and runs scripts 
# to install packages. 
# 
# *************************************************************************
# 
# ------------------------------------------------------------------------
# Templates need a descriptive name and version if
# source controlled in git.
# ------------------------------------------------------------------------
name: WordPress Template with Comments
formatVersion: 1
version: 1
#
# ------------------------------------------------------------------------
# Inputs create user selections that appear at deployment time. Inputs 
# can set placement decisions and configurations, and are referenced 
# later, by the resources section.
# ------------------------------------------------------------------------
inputs:
# 
# ------------------------------------------------------------------------
# Choose a cloud endpoint. 'Title' is the visible 
# option text (oneOf allows for the friendly title). 'Const' is the 
# tag that identifies the endpoint, which was set up earlier, under the 
# Cloud Assembly Infrastructure tab.
# ------------------------------------------------------------------------
  platform:
    type: string
    title: Deploy to
    oneOf:
      - title: AWS
        const: aws
      - title: Azure
        const: azure
      - title: vSphere
        const: vsphere
    default: vsphere
# 
# ------------------------------------------------------------------------
# Choose the operating system. Note that the Cloud Assembly
# Infrastructure must also have an AWS, Azure, and vSphere Ubuntu image 
# mapped. In this case, enum sets the option that you see, meaning there's
# no friendly title feature this time. Also, only Ubuntu is available 
# here, but having this input stubbed in lets you add more operating
# systems later. 
# ------------------------------------------------------------------------
  osimage:
    type: string
    title: Operating System
    description: Which OS to use
    enum:
      - Ubuntu
# 
# ------------------------------------------------------------------------
# Set the number of machines in the database cluster. Small and large 
# correspond to 1 or 2  machines, respectively, which you see later,
# down in the resources section. 
# ------------------------------------------------------------------------
  dbenvsize:
    type: string
    title: Database cluster size
    enum:
      - Small
      - Large
# 
# ------------------------------------------------------------------------
# Dynamically tag the machines that will be created. The 
# 'array' of objects means you can create as many key-value pairs as 
# needed. To see how array input looks when it's collected,
# open the cloud template and click TEST.
# ------------------------------------------------------------------------
  Mtags:
    type: array
    title: Tags
    description: Tags to apply to machines
    items:
      type: object
      properties:
        key:
          type: string
          title: Key
        value:
          type: string
          title: Value
# 
# ------------------------------------------------------------------------
# Create machine credentials. These credentials are needed in
# remote access configuration later, in the resources section.
# ------------------------------------------------------------------------
  username:
    type: string
    minLength: 4
    maxLength: 20
    pattern: '[a-z]+'
    title: Database Username
    description: Database Username
  userpassword:
    type: string
    pattern: '[a-z0-9A-Z@#$]+'
    encrypted: true
    title: Database Password
    description: Database Password
# 
# ------------------------------------------------------------------------
# Set the database storage disk size.
# ------------------------------------------------------------------------
  databaseDiskSize:
    type: number
    default: 4
    maximum: 10
    title: MySQL Data Disk Size
    description: Size of database disk
# 
# ------------------------------------------------------------------------
# Set the number of machines in the web cluster. Small, medium, and large 
# correspond to 2, 3, and 4 machines, respectively, which you see later,
# in the WebTier part of the resources section.
# ------------------------------------------------------------------------
  clusterSize:
    type: string
    enum:
      - small
      - medium
      - large
    title: Wordpress Cluster Size
    description: Wordpress Cluster Size
# 
# ------------------------------------------------------------------------
# Set the archive storage disk size.
# ------------------------------------------------------------------------
  archiveDiskSize:
    type: number
    default: 4
    maximum: 10
    title: Wordpress Archive Disk Size
    description: Size of Wordpress archive disk
#
# ------------------------------------------------------------------------
# The resources section configures the deployment of machines, disks, 
# networks, and other objects. In several places, the code pulls from 
# the preceding interactive user inputs.
# ------------------------------------------------------------------------
resources:
# 
# ------------------------------------------------------------------------
# Create the database server. Choose a cloud agnostic machine 'type' so
# that it can deploy to AWS, Azure, or vSphere. Then enter its property 
# settings.
# ------------------------------------------------------------------------
  DBTier:
    type: Cloud.Machine
    properties:
# 
# ------------------------------------------------------------------------
# Descriptive name for the virtual machine. Does not become the hostname 
# upon deployment. 
# ------------------------------------------------------------------------
      name: mysql
# 
# ------------------------------------------------------------------------
# Hard-coded operating system image to use. To pull from user input above,
# enter the following instead. 
# image: '${input.osimage}' 
# ------------------------------------------------------------------------
      image: Ubuntu
# 
# ------------------------------------------------------------------------
# Hard-coded capacity to use. Note that the Cloud Assembly 
# Infrastructure must also have AWS, Azure, and vSphere flavors 
# such as small, medium, and large mapped. 
# ------------------------------------------------------------------------
      flavor: small
# 
# ------------------------------------------------------------------------
# Tag the database machine to deploy to the cloud vendor chosen from the 
# user input. Tags are case-sensitive, so 'to_lower' forces the tag to 
# lowercase to ensure a match with a site's tagging convention. It's 
# important if platform input were to contain any upper case characters.
# ------------------------------------------------------------------------
      constraints:
        - tag: '${"env:" + to_lower(input.platform)}'
# 
# ------------------------------------------------------------------------
# Also tag the database machine with any free-form tags that were created 
# during user input. 
# ------------------------------------------------------------------------
      tags: '${input.Mtags}'
# 
# ------------------------------------------------------------------------
# Set the database cluster size by referencing the dbenvsize user 
# input. Small is one machine, and large defaults to two. 
# ------------------------------------------------------------------------
      count: '${input.dbenvsize == "Small" ? 1 : 2}' 
# 
# ------------------------------------------------------------------------
# Add a variable to connect the machine to a network resource based on 
# a property binding to another resource. In this case, it's the 
# 'WP_Network' network that gets defined further below.
# ------------------------------------------------------------------------
      networks:
        - network: '${resource.WP_Network.id}'
# 
# ------------------------------------------------------------------------
# Enable remote access to the database server. Reference the credentials 
# from the user input. 
# ------------------------------------------------------------------------
      remoteAccess:
        authentication: usernamePassword
        username: '${input.username}'
        password: '${input.userpassword}'
# 
# ------------------------------------------------------------------------
# You are free to add custom properties, which might be used to initiate 
# an extensiblity subscription, for example. 
# ------------------------------------------------------------------------
      ABC-Company-ID: 9393 
# 
# ------------------------------------------------------------------------
# Run OS commands or scripts to further configure the database machine, 
# via operations such as setting a hostname, generating SSH private keys,
# or installing packages.
# ------------------------------------------------------------------------
      cloudConfig: |
        #cloud-config
        repo_update: true
        repo_upgrade: all
        packages:
        - mysql-server
        runcmd:
        - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf
        - service mysql restart
        - mysql -e "CREATE USER 'root'@'%' IDENTIFIED BY 'mysqlpassword';" 
        - mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';"
        - mysql -e "FLUSH PRIVILEGES;"
      attachedDisks: []
# 
# ------------------------------------------------------------------------
# Create the web server. Choose a cloud agnostic machine 'type' so that it
# can deploy to AWS, Azure, or vSphere. Then enter its property settings.
# ------------------------------------------------------------------------
  WebTier:
    type: Cloud.Machine
    properties:
# 
# ------------------------------------------------------------------------
# Descriptive name for the virtual machine. Does not become the hostname 
# upon deployment. 
# ------------------------------------------------------------------------
      name: wordpress
# 
# ------------------------------------------------------------------------
# Hard-coded operating system image to use. To pull from user input above,
# enter the following instead:
# image: '${input.osimage}' 
# ------------------------------------------------------------------------
      image: Ubuntu
# 
# ------------------------------------------------------------------------
# Hard-coded capacity to use. Note that the Cloud Assembly
# Infrastructure must also have AWS, Azure, and vSphere flavors 
# such as small, medium, and large mapped.
# ------------------------------------------------------------------------
      flavor: small 
# 
# ------------------------------------------------------------------------
# Set the web server cluster size by referencing the clusterSize user 
# input. Small is 2 machines, medium is 3, and large defaults to 4. 
# ------------------------------------------------------------------------
      count: '${input.clusterSize== "small" ? 2 : (input.clusterSize == "medium" ? 3 : 4)}'
# 
# ------------------------------------------------------------------------
# Set an environment variable to display object information under the 
# Properties tab, post-deployment. Another example might be 
# {env.blueprintID} 
# ------------------------------------------------------------------------
      tags:
        - key: cas.requestedBy
          value: '${env.requestedBy}' 
# 
# ------------------------------------------------------------------------
# You are free to add custom properties, which might be used to initiate 
# an extensiblity subscription, for example. 
# ------------------------------------------------------------------------
      ABC-Company-ID: 9393 
# 
# ------------------------------------------------------------------------
# Tag the web server to deploy to the cloud vendor chosen from the 
# user input. Tags are case-sensitive, so 'to_lower' forces the tag to 
# lowercase to ensure a match with your site's tagging convention. It's 
# important if platform input were to contain any upper case characters.
# ------------------------------------------------------------------------
      constraints:
        - tag: '${"env:" + to_lower(input.platform)}' 
# 
# ------------------------------------------------------------------------
# Add a variable to connect the machine to a network resource based on 
# a property binding to another resource. In this case, it's the 
# 'WP_Network' network that gets defined further below.
# ------------------------------------------------------------------------
      networks:
        - network: '${resource.WP_Network.id}'
# 
# ------------------------------------------------------------------------
# Run OS commands or scripts to further configure the web server, 
# with operations such as setting a hostname, generating SSH private keys,
# or installing packages.
# ------------------------------------------------------------------------
      cloudConfig: |
        #cloud-config
        repo_update: true
        repo_upgrade: all
        packages:
        - apache2
        - php
        - php-mysql
        - libapache2-mod-php
        - mysql-client
        - gcc
        - make
        - autoconf
        - libc-dev
        - pkg-config
        - libmcrypt-dev
        - php-pear
        - php-dev
        runcmd:
        - mkdir -p /var/www/html/mywordpresssite && cd /var/www/html && wget https://wordpress.org/latest.tar.gz && tar -xzf /var/www/html/latest.tar.gz -C /var/www/html/mywordpresssite --strip-components 1
        - i=0; while [ $i -le 10 ]; do mysql --connect-timeout=3 -h ${DBTier.networks[0].address} -u root -pmysqlpassword -e "SHOW STATUS;" && break || sleep 15; i=$((i+1)); done
        - mysql -u root -pmysqlpassword -h ${DBTier.networks[0].address} -e "create database wordpress_blog;"
        - mv /var/www/html/mywordpresssite/wp-config-sample.php /var/www/html/mywordpresssite/wp-config.php
        - pecl channel-update pecl.php.net
        - pecl update-channels
        - pecl install mcrypt
        - sed -i -e s/"define( 'DB_NAME', 'database_name_here' );"/"define( 'DB_NAME', 'wordpress_blog' );"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define( 'DB_USER', 'username_here' );"/"define( 'DB_USER', 'root' );"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define( 'DB_PASSWORD', 'password_here' );"/"define( 'DB_PASSWORD', 'mysqlpassword' );"/ /var/www/html/mywordpresssite/wp-config.php && sed -i -e s/"define( 'DB_HOST', 'localhost' );"/"define( 'DB_HOST', '${DBTier.networks[0].address}' );"/ /var/www/html/mywordpresssite/wp-config.php
        - sed -i '950i extension=mcrypt.so' /etc/php/7.4/apache2/php.ini
        - service apache2 reload
# 
# ------------------------------------------------------------------------
# Create the network that the database and web servers connect to. 
# Choose a cloud agnostic network 'type' so that it can deploy to AWS, 
# Azure, or vSphere. Then enter its property settings.
# ------------------------------------------------------------------------
  WP_Network:
    type: Cloud.Network
    properties:
# 
# ------------------------------------------------------------------------
# Descriptive name for the network. Does not become the network name 
# upon deployment. 
# ------------------------------------------------------------------------
      name: WP_Network
# 
# ------------------------------------------------------------------------
# Set the networkType to an existing network. You could also use a 
# constraint tag to target a specific, like-tagged network. 
# The other network types are private or public.
# ------------------------------------------------------------------------
      networkType: existing
# 
# ************************************************************************
# 
# VMware hopes that you found this commented template useful. Note that 
# you can also access an API to create templates, or query for input 
# schema that you intend to request. See the following Swagger 
# documentation.
# 
# www.mgmt.cloud.vmware.com/blueprint/api/swagger/swagger-ui.html
# 
# ************************************************************************

```
