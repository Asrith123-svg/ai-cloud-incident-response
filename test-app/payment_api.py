import json
import time


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):

    path = event.get("rawPath", "/")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    print(f"Request received: {method} {path}")

    # Health check
    if path == "/health":
        print("Health check successful")

        return response(
            200,
            {
                "service": "payment-api",
                "status": "healthy"
            }
        )

    # Normal payment
    if path == "/payment":

        print("Processing payment")

        time.sleep(0.2)

        return response(
            200,
            {
                "payment_id": "PAY-001",
                "status": "success"
            }
        )

    # Simulate database failure
    if path == "/simulate-db-error":

        print("ERROR: Database connection timeout")
        print("ERROR: Connection pool exhausted")
        print("ERROR: Failed to execute database query")

        raise Exception(
            "Database connection timeout - connection pool exhausted"
        )

    # Simulate high latency
    if path == "/simulate-latency":

        print("WARNING: Payment API latency increased")

        time.sleep(5)

        return response(
            200,
            {
                "status": "slow",
                "latency": "5 seconds"
            }
        )

    # Simulate memory error
    if path == "/simulate-memory-error":

        print("ERROR: Memory usage exceeded threshold")
        print("ERROR: OutOfMemory warning")

        raise MemoryError(
            "Simulated memory exhaustion"
        )

    # Simulate CPU-intensive operation
    if path == "/simulate-high-cpu":

        print("WARNING: CPU-intensive operation started")

        start = time.time()

        while time.time() - start < 5:
            _ = 12345 * 67890

        print("CPU-intensive operation completed")

        return response(
            200,
            {
                "status": "completed",
                "message": "CPU load simulation finished"
            }
        )

    return response(
        404,
        {
            "error": "Route not found",
            "available_routes": [
                "/health",
                "/payment",
                "/simulate-db-error",
                "/simulate-latency",
                "/simulate-memory-error",
                "/simulate-high-cpu"
            ]
        }
    )