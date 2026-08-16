# Catode32 — Repo Mandate: No PII / Secrets to Public Repos

The `engkon6/catode32` remote for this repository is **public**. Treat every
push to it as a public release.

## Rules

1. Never commit or push credentials, tokens, keys, passwords, or `.env`/`.pem`/
   `.key` files — in files, commit messages, or git config. Do not embed tokens
   in remote URLs.
2. Never push PII: real names/emails, usernames not meant to be public, absolute
   user paths (`/home/<user>`, `/mnt/c/Users/<user>`, `C:\Users\<user>`), device
   serial/MAC IDs, Wi-Fi credentials, IPs, or phone numbers.
3. A secret/PII already in history must be scrubbed from ALL commits (e.g.
   `git filter-repo --replace-text`) and force-pushed only with explicit owner
   approval — deleting just the current file is not enough.
4. Pre-push, always scan the tree and (for public repos) the history:
   `ghp_`, `BEGIN [RSA|EC|OPENSSH] PRIVATE`, `api[_-]?key`, `password`, `secret`,
   `token`, `/home/`, `C:\Users\`, `/mnt/c/Users/`, personal names/emails,
   `ssh-rsa`, `ssh-ed25519`, and check `git ls-files` for credential files.
5. After any push using temporary credentials, restore the remote URL to its
   clean, credential-free form.

## If you find anything

Stop, do not push, report the exact files/lines to the user, and propose the fix.
