import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
api_key = "18ce006f0ac44579a36bfaf01653254c"

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])


def analyze_read_local_file(file_path, output_json_path):
    # Open the local file as a binary stream
    with open(file_path, "rb") as file:
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(api_key)
        )

        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=file
        )
        result = poller.result()

        # Extract relevant data into a dictionary
        document_data = {
            "content": result.content,
            "styles": [],
            "pages": []
        }

        for idx, style in enumerate(result.styles):
            document_data["styles"].append({
                "handwritten": style.is_handwritten
            })

        for page in result.pages:
            page_data = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": [],
                "words": []
            }

            for line_idx, line in enumerate(page.lines):
                page_data["lines"].append({
                    "line_number": line_idx,
                    "text": line.content,
                    "bounding_box": format_bounding_box(line.polygon)
                })

            for word in page.words:
                page_data["words"].append({
                    "text": word.content,
                    "confidence": word.confidence
                })

            document_data["pages"].append(page_data)

        # Save the document data as a JSON file
        with open(output_json_path, "w") as json_file:
            json.dump(document_data, json_file, indent=4)

        print(f"Document analysis result saved to {output_json_path}")


if __name__ == "__main__":
    # Replace with the path to your local file and the output location for JSON
    file_path = "/Users/kevinshieldsjr/Desktop/lf_test/sample/GU-LF-003737_P002.pdf"
    output_json_path = "/Users/kevinshieldsjr/Desktop/lf_test/analysis_output.json"
    analyze_read_local_file(file_path, output_json_path)