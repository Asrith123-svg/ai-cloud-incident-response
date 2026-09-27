# API Latency Runbook

## Symptoms

An API latency incident may produce:

- High request latency
- Slow API responses
- Increased request timeouts
- Customer-facing performance degradation
- Possible increase in error rates

## Possible Causes

1. Slow database queries
2. Downstream service latency
3. Network problems
4. Increased traffic
5. Resource exhaustion
6. Inefficient application code

## Investigation Steps

1. Check API latency metrics.
2. Check application CPU and memory.
3. Review application logs.
4. Check database response times.
5. Check downstream service latency.
6. Compare latency with traffic volume.
7. Check for recent application deployments.

## Recommended Actions

- Identify the slow component.
- Investigate database query performance.
- Check downstream dependencies.
- Review recent application changes.
- Scale the affected service when sustained traffic is confirmed.

## Severity

Usually MEDIUM, but can become HIGH when customer requests are significantly affected.