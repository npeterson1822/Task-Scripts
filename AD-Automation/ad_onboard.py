import subprocess
import getpass
import os

def run_ps(command, dry_run=False):
    """Run a PowerShell command. Dry-run prints it instead of executing."""
    if dry_run:
        print(f"[DRY-RUN] {command}\n")
        return ""
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Error:", result.stderr.strip())
    return result.stdout.strip()

# === Step 0: AD Credentials ===
ad_user = input("AD username (DOMAIN\\username): ").strip()
ad_pass = getpass.getpass("AD password: ")

# Build PowerShell credential object
ps_cred = f"""
$secpasswd = ConvertTo-SecureString '{ad_pass}' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('{ad_user}', $secpasswd)
"""

# === Step 1: Inputs for the new user ===
first = input("First name: ").strip()
last = input("Last name: ").strip()
copy_from = input("Copy-from user (sAMAccountName): ").strip()
orientation_date = input("Orientation date (MMDD): ").strip()
location = input("Location (e.g., location1, location2): ").strip()
alias_domain = input("Alias domain (leave blank if none): ").strip()
dry_run_input = input("Dry-run only? (y/n): ").strip().lower()
dry_run = dry_run_input == "y"

# === Step 1a: Build identifiers ===
sam = f"{first} {last}"   # legacy logon name
display_name = f"{first} {last}"

# UPN domain (placeholder)
upn = f"{first} {last}@example-corp.com"

# Primary email domain (placeholder)
email = f"{first[0].lower()}{last.lower()}@example-mail.com"

password = f"Change@{orientation_date}!"

# === Step 2: Get OU of copy-from user ===
ou_cmd = f"{ps_cred} (Get-ADUser -Identity '{copy_from}' -Credential $cred).DistinguishedName -replace '^CN=.*?,',''"
ou = run_ps(ou_cmd, dry_run=dry_run)
if not ou and not dry_run:
    print(f\"❌ Could not determine OU from copy-from user '{copy_from}'. Exiting.\")
    exit(1)
print(f\"Using OU: {ou}\")

# === Step 3: Create the new user ===
create_cmd = f"""
{ps_cred}
New-ADUser -Name '{display_name}' `
 -GivenName '{first}' `
 -Surname '{last}' `
 -SamAccountName '{sam}' `
 -DisplayName '{display_name}' `
 -UserPrincipalName '{upn}' `
 -EmailAddress '{email}' `
 -Path '{ou}' `
 -AccountPassword (ConvertTo-SecureString '{password}' -AsPlainText -Force) `
 -Enabled $true `
 -Credential $cred
"""
run_ps(create_cmd, dry_run=dry_run)

# === Step 4: Check user exists before continuing ===
check_cmd = f"{ps_cred} Get-ADUser -Identity '{sam}' -Credential $cred"
check_user = run_ps(check_cmd, dry_run=dry_run)
if not check_user and not dry_run:
    print(f\"❌ User '{sam}' was not created. Exiting.\")
    exit(1)

# === Step 5: Copy group memberships from template user ===
group_cmd = f"""
{ps_cred}
$groups = Get-ADUser -Identity '{copy_from}' -Property MemberOf -Credential $cred | Select-Object -Expand MemberOf
foreach ($g in $groups) {{
    Add-ADGroupMember -Identity $g -Members '{sam}' -Credential $cred
}}
"""
run_ps(group_cmd, dry_run=dry_run)

# === Step 6: Fix location group ===
fix_loc_cmd = f"""
{ps_cred}
Get-ADUser -Identity '{sam}' -Property MemberOf -Credential $cred | Select -Expand MemberOf |
 Where-Object {{ $_ -like 'CN=everyone-*' }} |
 ForEach-Object {{ Remove-ADGroupMember -Identity $_ -Members '{sam}' -Credential $cred -Confirm:$false }}
Add-ADGroupMember -Identity "everyone-{location}" -Members '{sam}' -Credential $cred
"""
run_ps(fix_loc_cmd, dry_run=dry_run)

# === Step 7: Set alias if provided ===
if alias_domain:
    alias_email = f"{first[0].lower()}{last.lower()}@{alias_domain}"
    alias_cmd = f"""
    {ps_cred}
    Set-ADUser -Identity '{sam}' -Clear extensionAttribute1 -Credential $cred
    Set-ADUser -Identity '{sam}' -Add @{{extensionAttribute1='{alias_email}'}} -Credential $cred
    """
    run_ps(alias_cmd, dry_run=dry_run)

print(f"✅ User {display_name} created. Login: {upn}, Email: {email}, Temp Password: {password}")
