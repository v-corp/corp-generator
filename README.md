# Cancamusa

ISO: https://software-download.microsoft.com/download/pr/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO

### How it works

```
$ sudo python3 bin/corp-generator.py --iso /home/xurxo/Descargas/14393.0.161119-1705.RS1_REFRESH_SERVER_EVAL_X64FRE_ES-ES.ISO --name test-cancamusa --username paco --win-image 1
Current directory: /home/paco/test/corp-generator
Cache directory: /home/paco/test/corp-generator
Calculating MD5 of ISO image...
MD5 = 920a6148d79075d261c10c5cb906d39c
Checking Windows Image Type...
mount: /mnt/920a6148d79075d261c10c5cb906d39c: ATENCIÓN: el dispositivo está protegido contra escritura; se monta como sólo lectura.
Select a Windows Image:
1 - Windows Server 2016 SERVERSTANDARDCORE
2 - Windows Server 2016 SERVERSTANDARD
3 - Windows Server 2016 SERVERDATACENTERCORE
4 - Windows Server 2016 SERVERDATACENTER
2
WIN_IMAGE=Windows Server 2016 SERVERSTANDARD
Downloading Virtio drivers 0.1.172-1 from:
https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.172-1/virtio-win-0.1.172.iso
100% [..................................................] 371818496 / 371818496
Created answer file: answer/test-cancamusa/Autounattend.xml
Created packer file: packer-test-cancamusa.json
Created vagrant file: vagrant-files/vagrant-test-cancamusa.template
Copy script: firewall-disable.bat
Copy script: enable-winrm.ps1
Copy script: install-bginfo.ps1
Copy script: create-domain.ps1
Copy script: vagrant-ssh.bat
Copy script: unlimited-password-expiration.bat
Copy script: firewall-open-smb.bat
Copy script: execution-policy-unrestricted.bat
Copy script: zz-start-sshd.cmd
Copy script: install-cygwin-sshd.bat
Copy script: vagrant.bat
Copy script: install-iis.ps1
Copy script: fixnetwork.ps1
Copy script: copy-scripts.bat
Copy script: vagrant.pub
Copy script: firewall-open-ping.bat
Copy script: install-cygwin-sshd.sh
Copy script: disable-hibernate.bat
Copy script: disable-firewall.bat
Copy script: disablewinupdate.bat
Copy script: firewall-open-rdp.bat
Copy script: provision.ps1
Copy script: fill-ad.ps1
Copy script: disable-winrm.ps1
Copy script: install-chocolatey.ps1
Copy script: install-git.ps1
Copy script: join-domain.ps1
Copy script: enable-rdp.bat
Copy script: winrm-allow-basic.bat
Copy script: setup-net.ps1
Copy script: bginfo.bgi
Copy script: install-adfs2.ps1
Copy script: install-winrm.cmd
Copy script: install-rol.ps1
Copy script: uac-disable.bat
Created .gitignore
```
