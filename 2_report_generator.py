import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def extract_metadata(folder_path):
    # Define regex patterns for various metadata fields
    patterns = {
        "browser_name": r"Browser name:\s*(.+)",
        "browser_version": r"Browser version:\s*(.+)",
        "platform_name": r"Platform name:\s*(.+)",
        "extension_used": r"Extension Used:\s*(.+)",
        "tenant_url": r"Current URL\s*::\s*(.+)",
        "current_file": r"Current file name:\s*(.*\.py)"  # Adjusted to capture .py files directly
    }

    method_patterns = {
        "method_selected": r"(LUA|Ruler)\s+Method\s+Selected",
        "ai_prompt": r"AI PROMPT::\s*(.+)",  # Pattern for AI PROMPT
        "policy": r"Policy::\s*(.+)",
        "script_name": r"Current file name:\s*(.*\.py)"  # Pattern for capturing script name with .py extension
    }

    metadata_results = []  # Store metadata results

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Process only .txt files
            file_path = os.path.join(folder_path, filename)
            metadata = {"file": filename}  # Start with the file name
            script_execution_status = "Error"  # Default status is "Error"
            selected_method = "Not found"  # Default method is "Not found"
            ai_prompt = "Not found"  # Default AI prompt
            policy = "Not found"  # Default policy
            middle_lines = []  # Store all middle lines found

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Extract each metadata field using regex patterns
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        metadata[key] = match.group(1).strip()

                # Check for "Browser Closed."
                if re.search(r"Browser closed\.", content, re.IGNORECASE):
                    script_execution_status = "Pass"
                else:
                    script_execution_status = "Error!"  # If not found, it's a failure

                # Check for method selection (LUA or Ruler)
                method_match = re.search(method_patterns["method_selected"], content)
                if method_match:
                    selected_method = method_match.group(1)  # Capture the method (LUA or Ruler)

                # Check for AI PROMPT and Policy
                ai_prompt_match = re.search(method_patterns["ai_prompt"], content)
                if ai_prompt_match:
                    ai_prompt = ai_prompt_match.group(1).strip()  # Capture AI PROMPT

                policy_match = re.search(method_patterns["policy"], content)
                if policy_match:
                    policy = policy_match.group(1).strip()  # Capture Policy

                # Check for the pattern surrounded by asterisks and capture all middle lines
                if script_execution_status == "Pass":
                    # Look for content between lines surrounded by asterisks
                    asterisk_pattern = r"\*{2,}\s*(.*?)\s*\*{2,}"
                    matches = re.findall(asterisk_pattern, content, re.DOTALL)

                    # Store all the middle lines found between asterisks
                    for match in matches:
                        middle_lines.append(match.strip())

                # Now try to capture the script name using the regex pattern
                script_name_match = re.search(method_patterns["script_name"], content)
                if script_name_match:
                    metadata["script_name"] = script_name_match.group(1).strip()  # Store the script name

            # Store the metadata, execution status, method, and middle lines
            metadata["execution_status"] = script_execution_status
            metadata["method_selected"] = selected_method
            metadata["ai_prompt"] = ai_prompt  # Add AI PROMPT to metadata
            metadata["policy"] = policy  # Add Policy to metadata
            metadata["middle_lines"] = middle_lines
            metadata_results.append(metadata)

    return metadata_results


# Specify the folder containing the text files
folder_path = "Automation_output"  # Change this to your folder path

# Extract metadata
metadata = extract_metadata(folder_path)

# Generate PDF report
def generate_pdf(metadata):
    pdf_file = "Automation_output_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 10)
    y_position = height - 40  # Start near the top of the page

    if metadata:
        # Print summary from the first metadata entry
        c.drawString(40, y_position, f"Platform Name: {metadata[0].get('platform_name', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, f"Browser Name: {metadata[0].get('browser_name', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, f"Browser Version: {metadata[0].get('browser_version', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, f"Extension Used: {metadata[0].get('extension_used', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, f"Tenant URL: {metadata[0].get('tenant_url', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, "      ")  # Add space after the summary
        y_position -= 10

    for item in metadata:
        # Print file-specific details
        c.drawString(40, y_position, f"Output File: {item['file']}")
        y_position -= 20
        c.drawString(40, y_position, f"Script Name: {item.get('script_name', 'Not found')}")
        y_position -= 20
        c.drawString(40, y_position, f"Policy Generation Method: {item['method_selected']}")
        y_position -= 20
        c.drawString(40, y_position, f"AI PROMPT: {item['ai_prompt']}")
        y_position -= 20
        c.drawString(40, y_position, f"Policy Property: {item['policy']}")
        y_position -= 20

        if item['middle_lines']:
            for middle_line in item['middle_lines']:
                c.drawString(40, y_position, f"  {middle_line}")
                y_position -= 20
            c.setFillColor(colors.red)
            c.drawString(40, y_position, "TEST FAIL")
            y_position -= 20
            c.setFillColor(colors.black)  # Reset to black color
        else:
            c.setFillColor(colors.green)
            c.drawString(40, y_position, "TEST PASS")
            y_position -= 20
            c.setFillColor(colors.black)  # Reset to black color

        y_position -= 20  # Add some extra space before the next file's details

        # If the page is getting too full, start a new page
        if y_position < 50:
            c.showPage()  # Create a new page
            c.setFont("Helvetica", 10)  # Reset font
            y_position = height - 40  # Reset position to top of the new page

    c.save()

    print("PDF FILE GENERATED")


# Call the function to generate the PDF


# Also print summary and results on the console
# Print summary (if you want to print it only once for the first file)
# if metadata:
#     print(f"Platform Name: {metadata[0].get('platform_name', 'Not found')}")
#     print(f"Browser Name: {metadata[0].get('browser_name', 'Not found')}")
#     print(f"Browser Version: {metadata[0].get('browser_version', 'Not found')}")
#     print(f"Extension Used: {metadata[0].get('extension_used', 'Not found')}")
#     print(f"Tenant URL: {metadata[0].get('tenant_url', 'Not found')}")
#     print("      ")
#
# for item in metadata:
#     print(f"Output File: {item['file']}")
#     print(f"Script Name: {item.get('script_name', 'Not found')}")
#     print(f"Policy Generation Method: {item['method_selected']}")
#     print(f"AI PROMPT: {item['ai_prompt']}")
#     print(f"Policy Property: {item['policy']}")
#
#     if item['middle_lines']:
#         for middle_line in item['middle_lines']:
#             print(f"  {middle_line}")
#         print("TEST FAIL")
#         print("     ")
#         print("     ")
#     else:
#         print("TEST PASS")
#         print("     ")
#         print("     ")
#
generate_pdf(metadata)




