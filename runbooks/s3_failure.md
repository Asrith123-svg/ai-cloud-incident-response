# S3 Failure Runbook

## Symptoms

An S3-related incident may produce:

- Failed object retrieval
- Failed object uploads
- AccessDenied errors
- NoSuchKey errors
- Increased application errors
- Increased request latency

## Possible Causes

1. Incorrect IAM permissions
2. Incorrect bucket or object path
3. Missing object
4. Incorrect bucket configuration
5. Application configuration error

## Investigation Steps

1. Check the application logs.
2. Identify the affected S3 bucket.
3. Verify the object key.
4. Check IAM permissions.
5. Check whether the object exists.
6. Review recent configuration changes.

## Recommended Actions

- Verify the S3 bucket and object key.
- Verify IAM permissions.
- Confirm that the required object exists.
- Review application configuration.
- Restore the required permissions or configuration.

## Severity

Usually MEDIUM, but can be HIGH when S3 is required for critical application functionality.