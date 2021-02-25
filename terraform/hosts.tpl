[all:children]
servers
clients

[all:vars]
ansible_ssh_private_key_file=aws.pem
ansible_user=ubuntu

[servers]
%{ for ip in servers ~}
${ip}
%{ endfor ~}

[clients]
%{ for ip in clients ~}
${ip}
%{ endfor ~}
