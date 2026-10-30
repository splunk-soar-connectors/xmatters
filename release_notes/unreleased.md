**Unreleased**

* Migrated the connector to the Splunk SOAR SDK. The minimum supported SOAR version is now 7.0.0 (previously 5.2.0); existing action names and username/password or client ID asset configuration remain available.
* Added the `make request` action for authenticated requests to xMatters API paths. Endpoints must be relative paths; absolute URLs are rejected.
* Test connectivity now returns `Test connectivity successful` instead of `Connectivity test succeeded`. Update playbooks or scripts that match the exact message.
