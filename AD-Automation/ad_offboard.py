import subprocess
import getpass
import datetime
import sys


# PS run helper

def run_ps(command):
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, result.stdout.strip()

# Admin creds inputs
admin_user = input("AD admin username (DOMAIN\\username): ").strip()
admin_pass = getpass.getpass("AD admin password: ").strip()

# Force AD login with admin creds provided
ps_cred = f"""
$secpasswd = ConvertTo-SecureString '{admin_pass}' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('{admin_user}', $secpasswd)
"""

# Input user - sAM varies by user, either name or email prefix
user_sam = input("sAMAccountName of user to offboard: ").strip()

# Check to find user
check_user_cmd = f"{ps_cred} Get-ADUser -Identity '{user_sam}' -Credential $cred"
success, output = run_ps(check_user_cmd)
if not success:
    print(f"Error: Cannot find user '{user_sam}' or invalid credentials:\n{output}")
    sys.exit(1)

# Disable user
disable_cmd = f"{ps_cred} Disable-ADAccount -Identity '{user_sam}' -Credential $cred"
success, output = run_ps(disable_cmd)
if not success:
    print(f"Error disabling user: {output}")
else:
    print(f"Disabled user {user_sam}")


# Group removal
groups_cmd = f"""
{ps_cred}
Get-ADUser -Identity '{user_sam}' -Property MemberOf -Credential $cred | 
Select-Object -ExpandProperty MemberOf | 
Where-Object {{ $_ -notlike 'CN=Domain Users,*' }} |
ForEach-Object {{ Remove-ADGroupMember -Identity $_ -Members '{user_sam}' -Credential $cred -Confirm:$false }}
"""
success, output = run_ps(groups_cmd)
if not success:
    print(f"Warning removing groups: {output}")
else:
    print(f"Removed user {user_sam} from all groups except Domain Users")


# Append term date to front of description
term_date = datetime.datetime.now().strftime("%m-%d-%y")
desc_cmd = f"""
{ps_cred}
$user = Get-ADUser '{user_sam}' -Credential $cred
$newDesc = '(TERM {term_date}) ' + ($user.Description)
Set-ADUser -Identity '{user_sam}' -Description $newDesc -Credential $cred
"""
success, output = run_ps(desc_cmd)
if not success:
    print(f"Warning updating description: {output}")
else:
    print(f"Updated description with termination date")


# User to Disabled OU
OU_disabled = "OU=Disabled Users,OU=2FA Exception,DC=DOMAIN,DC=com"
move_disabled_cmd = f"""
{ps_cred}
$user = Get-ADUser '{user_sam}' -Credential $cred
Move-ADObject -Identity $user.DistinguishedName -TargetPath '{OU_disabled}' -Credential $cred
"""
success, output = run_ps(move_disabled_cmd)
if not success:
    print(f"Warning moving to Disabled Users OU: {output}")
else:
    print(f"Moved user {user_sam} to Disabled Users OU")

print(f"-- Offboarding of {user_sam} complete. --")
