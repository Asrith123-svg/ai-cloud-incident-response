# Memory Exhaustion Runbook

## Symptoms

A memory exhaustion incident may produce:

- Memory utilization above 90%
- OutOfMemory warnings
- Application crashes
- Slow application performance
- Increased error rates

## Possible Causes

1. Memory leak
2. Excessive application workload
3. Large objects held in memory
4. Insufficient memory allocation
5. Increasing traffic
6. Inefficient caching

## Investigation Steps

1. Check memory utilization over time.
2. Review application logs for OutOfMemory errors.
3. Identify processes consuming excessive memory.
4. Check for recent application deployments.
5. Review application memory allocation.
6. Investigate possible memory leaks.

## Recommended Actions

- Identify the process consuming excessive memory.
- Investigate recent application changes.
- Restart the affected application if necessary.
- Increase available memory if sustained demand is confirmed.
- Fix memory leaks in the application.

## Severity

Usually HIGH when memory exhaustion causes application crashes.