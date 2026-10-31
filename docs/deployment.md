# Fly.io production

Requested 31 October 2026: publish English only, preserve selected design A, host FastAPI on Fly.io, and deploy on every push to main.

- App: `goeksu-blog`, personal organization, primary region `fra` (Frankfurt).
- One shared CPU, 256 MB, no database/volume, one machine kept running. `--ha=false` prevents automatic creation of a second machine. This configuration can have a short interruption during deployment; it does not promise high availability.
- HTTPS enforced by Fly Proxy; `/healthz` checked before traffic is routed. Routine Uvicorn access logging is disabled; platform/error logs remain possible.
- `.github/workflows/fly.yml` verifies lint, tests, content and static export before deploying the same commit. The former Pages deployment workflow is removed.
- GitHub repository secret `FLY_API_TOKEN` holds an app-scoped deploy token, valid for 8760 hours from setup. Renew it before expiry; never commit or print credentials.
- Apex DNS uses Fly shared IPv4 and dedicated IPv6. `www` follows apex. ACME CNAME records permit certificate issuance and renewal. Preserve all email and unrelated DNS records.
- `gddy` is the official GoDaddy CLI. Refreshable OAuth credentials are held in macOS Keychain. Future DNS work can use `gddy dns list goeksu.me --env prod`; no API key is required for this authenticated CLI path. GoDaddy CLI's default OAuth grant includes capabilities beyond DNS; mutations remain limited to the user's explicit task.
- A private full-zone snapshot is held outside the repository at `~/.config/personal-blog/dns-before-fly-2026-10-31.json` for rollback. Do not publish account data or credentials.
- Fly's processing agreement must be signed by the account owner; requesting it is separate from executing it. Track actual signature status separately from deployment.

## Operations

Use `fly status -a goeksu-blog`, `fly checks list -a goeksu-blog`, and `fly certs check goeksu.me -a goeksu-blog`. Verify public HTTPS, response contents, redirects and DNS separately from CLI success. A green GitHub run proves the automatic path only when the deployed image/release corresponds to that run's commit.

Rollback code through a reviewed revert on main so it follows the same pipeline. Reconcile DNS against the current zone and backup before making any rollback changes; never replace the entire zone blindly.

## Primary references

- [Fly GitHub Actions deployment](https://docs.fly.io/launch/continuous-deployment-with-github-actions)
- [Fly custom domains](https://docs.fly.io/networking/custom-domain)
- [Fly security and privacy questionnaire](https://fly.io/legal/security-questionnaire/)
- [Fly processing agreement](https://fly.io/documents)
- [GoDaddy CLI authentication](https://developer.godaddy.com/en/docs/api-users/cli/set-up)
