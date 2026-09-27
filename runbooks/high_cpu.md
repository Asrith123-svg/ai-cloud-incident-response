# High CPU Incident Runbook

## Symptoms

A high CPU incident may produce:

- CPU utilization above 80%
- Increased application latency
- Slow request processing
- Increased error rates
- Application workers consuming excessive CPU

## Possible Causes

1. Sudden traffic increase
2. CPU-intensive application operation
3. Infinite loop or inefficient code
4. Excessive background processing
5. Resource contention

## Investigation Steps

1. Check CPU utilization over time.
2. Check request traffic and request rate.
3. Review application logs.
4. Identify processes consuming high CPU.
5. Check for recent application deployments.
6. Compare CPU usage with latency and error rate.

## Recommended Actions

- Investigate sudden traffic increases.
- Review recent application changes.
- Identify CPU-intensive processes.
- Stop or restart a stuck application process if appropriate.
- Scale the application if sustained high traffic is confirmed.

## Severity

Usually MEDIUM to HIGH depending on application impact.