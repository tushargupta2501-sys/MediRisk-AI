import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 60)
    print("Starting MediRisk AI FastAPI Automated Integration Test Suite")
    print("=" * 60)

    # 1. Start Uvicorn Server
    print("\n[Step 1] Starting FastAPI uvicorn server in background...")
    server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for server to come online
    server_ready = False
    for attempt in range(15):
        time.sleep(1)
        try:
            req = urllib.request.Request(f"{BASE_URL}/")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    server_ready = True
                    break
        except Exception:
            pass

    if not server_ready:
        print("ERROR: Server failed to start within timeout.")
        server_process.terminate()
        out, err = server_process.communicate()
        print("Server stdout:", out)
        print("Server stderr:", err)
        sys.exit(1)

    print(" FastAPI server is UP and responding at http://127.0.0.1:8000")

    try:
        # 2. Test GET /
        print("\n[Step 2] Testing GET / (Root health check)...")
        req = urllib.request.Request(f"{BASE_URL}/")
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode())
            print(f"Status: {status}")
            print(f"Response: {body}")
            assert status == 200, f"Expected 200, got {status}"
            assert body == {"message": "MediRisk AI API is running"}
            print(" GET / test PASSED")

        # 3. Test POST /predict (Low Risk Patient)
        print("\n[Step 3] Testing POST /predict (Low-risk patient profile)...")
        low_risk_patient = {
            "age": 45.0,
            "sex": 0,
            "cp": 1,
            "trestbps": 115.0,
            "chol": 190.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 172.0,
            "exang": 0,
            "oldpeak": 0.0,
            "slope": 2,
            "ca": 0,
            "thal": 2,
        }
        data = json.dumps(low_risk_patient).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/predict",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode())
            print(f"Status: {status}")
            print(f"Response: {body}")
            assert status == 200, f"Expected 200, got {status}"
            assert "risk_probability" in body
            assert "prediction" in body
            assert body["message"] == "Prediction completed successfully"
            print(f" Risk Probability: {body['risk_probability']}, Prediction: {body['prediction']}")
            print(" POST /predict (low risk) test PASSED")

        # 4. Test POST /predict (High Risk Patient)
        print("\n[Step 4] Testing POST /predict (High-risk patient profile)...")
        high_risk_patient = {
            "age": 67.0,
            "sex": 1,
            "cp": 0,
            "trestbps": 160.0,
            "chol": 286.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 108.0,
            "exang": 1,
            "oldpeak": 1.5,
            "slope": 1,
            "ca": 3,
            "thal": 2,
        }
        data = json.dumps(high_risk_patient).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/predict",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode())
            print(f"Status: {status}")
            print(f"Response: {body}")
            assert status == 200, f"Expected 200, got {status}"
            assert body["prediction"] == 1, f"Expected prediction 1, got {body['prediction']}"
            print(f" High Risk Detected: Probability = {body['risk_probability']} (Prediction = {body['prediction']})")
            print(" POST /predict (high risk) test PASSED")

        # 5. Test Invalid Input Handling (422 Unprocessable Entity)
        print("\n[Step 5] Testing Pydantic validation on invalid inputs (age < 1)...")
        invalid_payload = {
            "age": -10.0,  # Invalid: age ge=1
            "sex": 1,
            "cp": 0,
            "trestbps": 140.0,
            "chol": 250.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 150.0,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 1,
            "ca": 0,
            "thal": 2,
        }
        req = urllib.request.Request(
            f"{BASE_URL}/predict",
            data=json.dumps(invalid_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(req)
            raise AssertionError("Server accepted invalid age without returning 422!")
        except urllib.error.HTTPError as e:
            print(f"Status: {e.code}")
            err_body = json.loads(e.read().decode())
            print(f"Validation Error Details: {err_body['detail'][0]['msg']}")
            assert e.code == 422, f"Expected 422, got {e.code}"
            print(" Pydantic 422 validation test PASSED")

        # 6. Test GET /predictions (History verification)
        print("\n[Step 6] Testing GET /predictions (History retrieval)...")
        req = urllib.request.Request(f"{BASE_URL}/predictions")
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            records = json.loads(resp.read().decode())
            print(f"Status: {status}")
            print(f"Total prediction records stored: {len(records)}")
            assert status == 200, f"Expected 200, got {status}"
            assert isinstance(records, list) and len(records) >= 2
            last_record = records[-1]
            print(f"Latest record probability: {last_record['risk_probability']}, prediction: {last_record['prediction']}")
            assert "created_at" in last_record
            assert "patient" in last_record
            print(" GET /predictions test PASSED")

        print("\n" + "=" * 60)
        print(" ALL 6 INTEGRATION TESTS COMPLETED SUCCESSFULLY! ")
        print("=" * 60)

    finally:
        print("\n[Cleanup] Shutting down test server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print(" Server shutdown complete.")

if __name__ == "__main__":
    run_tests()
