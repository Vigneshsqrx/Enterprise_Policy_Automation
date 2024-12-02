import os
import re
from xhtml2pdf import pisa
from io import BytesIO

def generate_pdf(metadata):
    # Create HTML content for the PDF
    html_content = """
    <html>
        <head>
            <style>
                body {
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 10pt;
                    margin: 0;
                    padding: 0;
                }
                .section {
                    margin-bottom: 20px;
                }
                .header {
                    font-size: 14pt;
                    font-weight: bold;
                }
                .footer {
                    position: fixed;
                    bottom: 20px;
                    left: 0;
                    right: 0;
                    text-align: center;
                }
                /* Style for the logo in the top-right corner */
                .logo {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    width: 150px;  /* Adjust the size of the logo */
                }
            </style>
        </head>
        <body>
            <!-- Add logo to the top-right corner -->
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7t4Pvhj2gVpdXIcOw-iJVms99lmXSSG44pA&s" alt="Logo" class="logo">
    """

    # Add metadata summary
    if metadata:
        html_content += f'<div class="section"><span class="header">Platform Name:</span> {metadata[0].get("platform_name", "Not found")}</div>'
        html_content += f'<div class="section"><span class="header">Extension Used:</span> {metadata[0].get("extension_used", "Not found")}</div>'
        html_content += f'<div class="section"><span class="header">Tenant URL:</span> {metadata[0].get("tenant_url", "Not found")}</div>'
        html_content += '<div class="section"><hr></div>'

    # Add each metadata item to the PDF content
    for item in metadata:
        html_content += f'<div class="section"><span class="header">Output File:</span> {item["file"]}</div>'
        html_content += f'<div class="section"><span class="header">Script Name:</span> {item.get("script_name", "Not found")}</div>'
        html_content += f'<div class="section"><span class="header">Policy Generation Method:</span> {item["method_selected"]}</div>'
        html_content += f'<div class="section"><span class="header">AI Prompt:</span> {item["ai_prompt"]}</div>'
        html_content += f'<div class="section"><span class="header">Policy Property:</span> {item["policy"]}</div>'

        html_content += f'<div class="section"><span class="header">Browser:</span> {item["browser_name"]}</div>'
        html_content += f'<div class="section"><span class="header">Browser Version:</span> {item["browser_version"]}</div>'

        # Check if there's an automation error and mark it
        if item.get("automation_error", False):
            html_content += f'<div class="section" style="color:red;"><strong>Automation Error</strong></div>'

        # If middle_lines are present, print them and mark test as fail
        elif item.get('middle_lines'):  # If middle_lines are present
            for middle_line in item['middle_lines']:
                html_content += f'<div class="section">{middle_line}</div>'
            html_content += f'<div class="section" style="color:red;"><strong>TEST FAIL</strong></div>'

        # If neither middle_lines nor automation_error are present, mark as pass in green
        else:  # No middle_lines and no automation_error
            html_content += f'<div class="section" style="color:green;"><strong>TEST PASS</strong></div>'

        html_content += '<div class="section"><hr></div>'

    # # Footer
    # html_content += '<div class="footer">SquareX</div>'
    #
    # html_content += "</body></html>"

    # Convert HTML to PDF using xhtml2pdf
    pdf_file = "Automation_output_report.pdf"
    with open(pdf_file, "wb") as pdf:
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf)

    if pisa_status.err:
        print("Error generating PDF")
    else:
        print("PDF generated successfully")




def extract_metadata(folder_path):
    # Define regex patterns for various metadata fields
    patterns = {
        "platform_name": r"Platform name:\s*(.+)",
        "extension_used": r"Extension Used:\s*(.+)",
        "tenant_url": r"Current URL\s*::\s*(.+)",
        "current_file": r"Current file name:\s*(.*\.py)"  # Adjusted to capture .py files directly
    }

    method_patterns = {
        "browser_name": r"Browser\s*name:\s*(.+)",  # More flexible to capture Browser Name
        "browser_version": r"Browser\s*version:\s*(.+)",  # More flexible to capture Browser Version
        "method_selected": r"(LUA|Ruler)\s+Method\s+Selected",  # Matching Lua or Ruler method
        "ai_prompt": r"AI PROMPT::\s*(.+)",  # Pattern for AI PROMPT
        "policy": r"Policy::\s*(.+)",  # Pattern for Policy
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
            automation_error = False  # Flag to track if "Error:" is found in content

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Check if "Error:" is found in the content
                if "Error:" in content:
                    automation_error = True  # Set the flag if "Error:" is found

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

                # Extract Browser Name and Browser Version using the updated regex
                browser_name_match = re.search(method_patterns["browser_name"], content)
                if browser_name_match:
                    metadata["browser_name"] = browser_name_match.group(1).strip()  # Store the browser name

                browser_version_match = re.search(method_patterns["browser_version"], content)
                if browser_version_match:
                    metadata["browser_version"] = browser_version_match.group(1).strip()  # Store the browser version

            # Store the metadata, execution status, method, and middle lines
            metadata["execution_status"] = script_execution_status
            metadata["method_selected"] = selected_method
            metadata["ai_prompt"] = ai_prompt  # Add AI PROMPT to metadata
            metadata["policy"] = policy  # Add Policy to metadata
            metadata["middle_lines"] = middle_lines
            metadata["automation_error"] = automation_error  # Add the flag to metadata
            metadata_results.append(metadata)

    return metadata_results

# Assuming folder_path is set
folder_path = "./Automation_output"  # Change this to your folder path

# Extract metadata
metadata = extract_metadata(folder_path)
if metadata:
    print(f"Platform Name: {metadata[0].get('platform_name', 'Not found')}")
    print(f"Extension Used: {metadata[0].get('extension_used', 'Not found')}")
    print(f"Tenant URL: {metadata[0].get('tenant_url', 'Not found')}")
    print("      ")

# Print metadata for each file
for item in metadata:
    print(f"Output File: {item['file']}")
    print(f"Script Name: {item.get('script_name', 'Not found')}")
    print(f"Browser Name: {item.get('browser_name', 'Not found')}")
    print(f"Browser Version: {item.get('browser_version', 'Not found')}")
    print(f"Policy Generation Method: {item['method_selected']}")
    print(f"AI PROMPT: {item['ai_prompt']}")
    print(f"Policy Property: {item['policy']}")

    # Check if "Error:" is found in the file content
    if item.get("automation_error", False):
        print("Automation Error")
        print("     ")

    elif item['middle_lines']:
        for middle_line in item['middle_lines']:
            print(f"  {middle_line}")
        print("TEST FAIL")
        print("     ")
        print("     ")
    else:
        print("TEST PASS")
        print("     ")
        print("     ")


generate_pdf(metadata)