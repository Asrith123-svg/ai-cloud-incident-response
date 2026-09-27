# Database Failure Runbook

## Symptoms

A database failure may produce:

- High application error rates
- Increased request latency
- Database connection timeouts
- Connection pool exhaustion
- Failed database queries

## Possible Causes

1. Database server unavailable
2. Network connectivity problems
3. Connection pool exhaustion
4. Database overload
5. Invalid database credentials
6. Database connection limit reached

## Investigation Steps

1. Check database availability.
2. Check application logs for connection errors.
3. Check database connection pool usage.
4. Check database CPU and memory utilization.
5. Check recent configuration changes.
6. Verify database credentials and connectivity.

## Recommended Actions

- Verify database availability.
- Check database connection limits.
- Investigate connection pool exhaustion.
- Review recent application or database configuration changes.
- Restore connectivity before restarting application components.

## Severity

Usually HIGH when database connectivity affects payment processing.