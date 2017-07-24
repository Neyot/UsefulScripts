import os, sys, fileinput

print("WARNING: This is only recommended for use on fresh SSHD installations (tested on a fresh DigitalOcean Debian configuration). Use on already changed sshd configurations may cause problems as this will change some of the lines in the SSHD config and will add a few onto the end.")
continue_with_script = input("Are you sure you want to continue? [y/n] ")
while True:
  if continue_with_script.lower() == "y" or "yes":
    break
  else:
    sys.exit()

group_name = input("Group name [Default: sftp_group]: ").strip() or "sftp_group"
restricted_dir = input("Directory to restrict to [Default: /home/{group name}]: ").strip() or "/home/" + group_name
user_name = input("User to create and add to group [Default: ftp_user]: ") or "ftp_user"
sshd_config = input("SSHD configuration file [Default: /etc/ssh/sshd_config]: ") or "/etc/ssh/sshd_config"

os.system("addgroup " + group_name)
print(" Added group " + group_name)

os.system("mkdir " + restricted_dir)
os.system("chmod g+rx " + restricted_dir)
print(" Created directory " + restricted_dir)

os.system("mkdir -p " + restricted_dir + "/files/")
os.system("chmod g+rwx " + restricted_dir + "/files/")
print(" Created directory " + restricted_dir + "/files/")

os.system("chgrp -R " + group_name + " " + restricted_dir)
print(" Assigned directory " + restricted_dir + " to group " + group_name)

os.system("cp " + sshd_config + " " + os.path.dirname(os.path.abspath(__file__)) + "/sshd_config.backup")
print(" Made a backup of sshd_config at " + os.path.dirname(os.path.abspath(__file__)) + "/sshd_config.backup")

with fileinput.FileInput(sshd_config, inplace=True, backup='.bak') as file:
  for line in file:
    if "Subsystem sftp" in line:
      print("Subsystem sftp internal-sftp")
    else:
      print(line, end='')

with open(sshd_config, "a") as file:
  file.write("\n")
  file.write("Match Group " + group_name + "\n")
  file.write("  # Force the connection to use SFTP and chroot to the required directory.\n")
  file.write("  ForceCommand internal-sftp\n")
  file.write("  ChrootDirectory " + restricted_dir + "\n")
  file.write("  #Disable tunneling, authentication agent, TCP and X11 forwarding.\n")
  file.write("  PermitTunnel no\n")
  file.write("  AllowAgentForwarding no\n")
  file.write("  AllowTcpForwarding no\n")
  file.write("  X11Forwarding no\n")
print(" Edited " + sshd_config + " to work with and secure the single dir account.")

os.system("useradd --groups " + group_name + " " + user_name)
os.system("passwd " + user_name)

os.system("service ssh restart")
