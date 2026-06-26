import requests
import json
import sys

API_URL = "http://localhost:8000/extract"


def test_with_pdf(pdf_path: str):
    """
    Sends a PDF file to the API and prints the response.
    Usage: python test_api.py path/to/your/paper.pdf
    """

    print(f"\n[TEST] Sending file: {pdf_path}")
    print("[TEST] Waiting for response...\n")

    with open(pdf_path, "rb") as pdf_file:
        response = requests.post(
            API_URL,
            files={"file": (pdf_path, pdf_file, "application/pdf")}
        )

    if response.status_code == 200:
        print("[SUCCESS] Got response from API!\n")
        result = response.json()

        print(json.dumps(result, indent=2))

        output_file = pdf_path.replace(".pdf", "_insights.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n[INFO] Result saved to: {output_file}")

    else:
        print(f"[ERROR] Request failed with status: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py path/to/paper.pdf")
        print("Example: python test_api.py sample_paper.pdf")
    else:
        test_with_pdf(sys.argv[1])
