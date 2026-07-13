# PingOne Identity Utility Tool

An open-source, locally-hosted web application to streamline PingOne Identity Operations. Currently supports **Bulk Password Updates**, allowing administrators to reset passwords for multiple PingOne users simultaneously via the PingOne API.

> **Disclaimer:** This project is not officially affiliated with or endorsed by Ping Identity. Use at your own risk. Ensure you have the appropriate permissions before executing bulk updates in a production environment.

## Features
* **Bootstrapping UI:** Easily configure your Environment ID and Worker App credentials.
* **Bulk Password Reset:** Paste a list of usernames to securely resolve their PingOne UUIDs and reset their passwords using the PingOne Admin APIs.
* **More coming soon:** Future updates will include Diagnostic Scanner (3-second scan of user profile metadata for login failures), Kill Switch (emergency offboarding to disable user, delete all sessions, update with random password and removing memberships) and MFA Compliance (check MFA adoption percentage, check weak MFA methods, user notification to use modern methods etc.,).

## Prerequisites
* Python 3.7+
* A PingOne environment.
* A PingOne "Worker App" configured with `Identity Data Admin` roles to allow User read/update capabilities.
