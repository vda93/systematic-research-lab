# Security policy

Use [GitHub private vulnerability reporting](https://github.com/vda93/systematic-research-lab/security/advisories/new) for suspected vulnerabilities or accidental sensitive-data exposure. Include the affected commit, a minimal reproduction and the likely impact. Keep credentials and exploit details out of public issues. The maintainer reviews reports for the current `main` branch; historical portfolio snapshots do not receive separate security maintenance.

This public research package does not execute trades, connect to brokerage accounts or manage credentials. Security checks support source publication and reproducibility. They do not certify strategy safety, scientific correctness or deployment readiness.

The [security controls and their limits](docs/security.md) describe dependency auditing, secret scanning, CodeQL and the local verification commands. A successful scan applies to its recorded revision and advisory database at the time it ran.
