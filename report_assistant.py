import os
from docx import Document
from groq import Groq  # Import Groq client

def extract_text_from_docx(file_path):
    """Extracts text content from a Word document."""
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])

def get_all_assessment_reports(patient_name):
    """Finds all assessment reports for a given patient."""
    reports_dir = "Reports"
    
    if not os.path.exists(reports_dir):
        return []  # Return empty list if the folder doesn't exist
    
    reports = [
        os.path.join(reports_dir, file)
        for file in os.listdir(reports_dir)
        if file.startswith(f"assessment_report_{patient_name}") and file.endswith(".docx")
    ]
    return sorted(reports)  # Sort by name (date is embedded in the filename)

def analyze_memory_trends(reports, patient_name):
    """Uses Groq API to analyze memory trends based on assessment reports."""
    client = Groq(api_key="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")  # Replace with a secure method of storing keys
    
    # Extract text from all reports
    report_texts = [extract_text_from_docx(report) for report in reports]
    combined_text = "\n\n".join(report_texts)
    
    prompt = f"""
    The following are assessment reports for a patient named {patient_name}. Reporting back to a doctor or the patient's caretaker.
    
    Go through the questions and answers completely before providing any bold statements. If the patient answers correctly, don't highlight negatives.
    Summarize the overall memory activity trends, including:
    - Number of assessments reviewed
    - Is memory improving?
    - Any major behavioral changes?
    - Common memory problems?
    - Simple recommendations to help.
    - Provide an overall score between 1-10.
    
    Reports:
    {combined_text}
    """
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

def main():
    patient_name = input("Enter patient name: ")
    reports = get_all_assessment_reports(patient_name)
    
    if not reports:
        print("No assessment reports found for the patient.")
        return
    
    print("Analyzing memory activity...")
    summary = analyze_memory_trends(reports, patient_name)
    print("\nMemory Activity Summary:")
    print(summary)

if __name__ == "__main__":
    main()
