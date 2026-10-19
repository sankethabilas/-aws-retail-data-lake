# Day 1: remaining tasks and how to do them

Day 1 code setup is finished (repo, venv, folder layout, requirements, `.gitignore`).
What is left is the AWS account hygiene, plus a few small repo checks.
No AWS resources are created today, and none of these steps cost money.

Estimated time: 45-60 minutes.

---

## Status

| Task | Status |
|---|---|
| Repo, venv, folder layout, requirements, `.gitignore` | Done |
| Enable MFA on the root user | To do |
| Stop using root for daily work (create a daily-use user) | To do |
| Create a budget with an email alert at $1 | To do |
| Confirm the budget alert email | To do |
| Turn on Free Tier usage alerts (if offered) | To do |
| Record the account plan in `docs/aws-account.md` | To do |
| Check the GitHub repo is public | To check |
| Fresh-venv install check | To check |

---

## 1. Enable MFA on the root user

1. Sign in to the AWS Console as the **root user** (the account email).
2. Click your account name (top right), then **Security credentials**.
3. Under **Multi-factor authentication (MFA)**, click **Assign MFA device**.
4. Name it (for example `root-mfa`) and choose **Authenticator app**.
5. Scan the QR code with an authenticator app (Google Authenticator, Authy, 1Password and so on).
6. Enter two consecutive codes and click **Add MFA**.
7. Sign out and sign back in to confirm it asks for a code.

Done when: the Security credentials page lists an assigned MFA device.

---

## 2. Create a daily-use identity (stop using root)

Preferred: IAM Identity Center. Acceptable for a personal sandbox: an IAM user.
The Day 6 plan needs short-lived credentials via `aws configure sso`, so Identity Center is the better choice.

### Option A: IAM Identity Center (preferred)

1. In the console, search for **IAM Identity Center** and click **Enable**.
   Use the same region you plan to use for the whole project (for example `us-east-1`).
2. Go to **Users**, then **Add user**. Enter a username and your email. Complete the invite.
3. Go to **Permission sets**, then **Create permission set**, and pick **Predefined: AdministratorAccess**.
   This is for one-off setup steps only.
   On Day 6 you will switch daily work to the project policy from Appendix A.
4. Go to **AWS accounts**, select your account, click **Assign users or groups**, choose your user and the permission set.
5. Open the **AWS access portal URL** from the Identity Center dashboard, set the password and register MFA for this user.
6. Later, on Day 6: `aws configure sso --profile retail-dev`.

### Option B: IAM user (simpler)

1. Console, then **IAM**, then **Users**, then **Create user**.
2. Enable console access. Attach `AdministratorAccess` for now (restrict it on Day 6).
3. Enable MFA for this user: open the user, **Security credentials**, **Assign MFA device**.
4. Only create access keys when you need the CLI (Day 6). Never commit them.
5. Sign in as this user from now on. Do not use root again, except for account-level tasks.

Done when: you can sign in as the new identity, and `aws sts get-caller-identity` (Day 6) will not show the root ARN.

---

## 3. Create the budget with a $1 alert

1. Console, then **Billing and Cost Management**, then **Budgets**, then **Create budget**.
   If budgets are blocked for your IAM user, enable **IAM user and role access to Billing information** under
   Account settings (done as root).
2. Choose **Use a template (simplified)**.
3. Pick **Zero spend budget** (alerts when you pass $0.01), or **Monthly cost budget** with **$1** as the amount.
4. Enter the email address that should receive alerts.
5. Click **Create budget**.
6. Open the email AWS sends, and confirm the subscription if it asks.

Done when: the budget appears in the list and the alert email address is confirmed.

---

## 4. Turn on Free Tier usage alerts

1. Console, then **Billing and Cost Management**, then **Billing preferences** (the name varies by console version).
2. Under **Alert preferences**, tick **Receive AWS Free Tier alerts** and enter your email.
3. Also tick **Receive CloudWatch billing alerts** if offered (optional).
4. Save.

If your account plan does not offer this option, write "not offered" in `docs/aws-account.md`.

---

## 5. Identify and record your account plan

1. Open the current **AWS Free Tier** page, or **Billing and Cost Management**, then **Free Tier**.
2. Note which plan your account is on (for example a Free plan with credits, or a Paid plan), and when any credits expire.
   AWS changes these offers, so write down what you actually see, not what a blog says.
3. Edit `docs/aws-account.md`:
   - Replace each `_TODO_` with `Done`, `Not offered` or a short note.
   - Set `Checked on:` to today's date (`2026-10-19` or the day you did it).
   - Never write account IDs, access keys or the account email in this file.

---

## 6. Repo checks

Run these from the repo root.

**Fresh-venv install check**

```powershell
python -m venv .venv-test
.venv-test\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
deactivate
Remove-Item -Recurse -Force .venv-test
```

Done when: the install finishes with no errors.

**GitHub repo visibility**

- Open the repo, then **Settings**, then **General**, then **Danger Zone**. Confirm it is **Public**
  (the plan calls for a public portfolio repo).
- The repo name starts with a hyphen (`-aws-retail-data-lake`). A leading hyphen can trip up command-line tools.
  Consider renaming it to `aws-retail-data-lake` in Settings, then update the remote:

  ```powershell
  git remote set-url origin https://github.com/sankethabilas/aws-retail-data-lake.git
  ```

  The local folder name does not need to change.

**Commit and push the Day 1 docs**

```powershell
git add docs/aws-account.md docs/day1-remaining-tasks.md
git commit -m "Day 1: record AWS account hygiene status"
git push
```

You can merge `development/sanketh` into `main` now or later. Do it before Day 5, so that the CI badge is green on `main`.

---

## Day 1 definition of done

- [ ] Repo pushed with skeleton folders and requirements (done)
- [ ] `pip install` works in a fresh venv
- [ ] MFA on root enabled
- [ ] Budget alert email confirmed
- [ ] `docs/aws-account.md` filled in with real values

When all boxes are ticked, start Day 2 (`src/download_data.py` and profiling).
