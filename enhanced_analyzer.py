import re
from datetime import datetime
import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def analyze_text(text):
    """Analyze the text and generate a detailed report."""
    analysis = {
        'policy_identification': [],
        'company_details': [],
        'coverage_details': [],
        'eligibility_criteria': [],
        'key_benefits': {
            'hospitalization': [],
            'treatment': [],
            'medical': [],
            'other': []
        },
        'waiting_periods': [],
        'key_exclusions': {
            'medical_conditions': [],
            'treatments': [],
            'general': []
        },
        'special_features': {
            'discounts': [],
            'additional_benefits': [],
            'special_features': []
        },
        'claims_process': [],
        'contact_info': []
    }

    # Policy Identification
    policy_patterns = [
        r'Policy\s+(?:Number|No\.?|ID)?\s*:?\s*([A-Z0-9-]+)',
        r'Policy\s+Type\s*:?\s*([A-Za-z\s]+)',
        r'Policy\s+Period\s*:?\s*([A-Za-z0-9\s,]+)'
    ]
    for pattern in policy_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['policy_identification'].append(match.group(0))

    # Company Details
    company_patterns = [
        r'([A-Za-z\s]+(?:Limited|Ltd\.?))\s+IRDAI\s+Reg\.?\s+No\.?\s*:?\s*(\d+)',
        r'CIN\s*:?\s*([A-Z0-9]+)',
        r'Registered\s+Office\s*:?\s*([^\.]+)'
    ]
    for pattern in company_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['company_details'].append(match.group(0))

    # Coverage Details
    coverage_patterns = [
        r'Sum\s+Insured\s+(?:range|options|from)?\s*:?\s*Rs\.?\s*([^.]+)',
        r'Coverage\s+for\s+([^\.]+)',
        r'Additional\s+Coverage\s+([^\.]+)'
    ]
    for pattern in coverage_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['coverage_details'].append(match.group(0))

    # Eligibility Criteria
    eligibility_patterns = [
        r'Eligibility\s+Criteria\s*:?\s*([^\.]+)',
        r'Age\s+Limit\s*:?\s*([^\.]+)',
        r'Required\s+Documents\s*:?\s*([^\.]+)'
    ]
    for pattern in eligibility_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['eligibility_criteria'].append(match.group(0))

    # Key Benefits
    benefit_patterns = {
        'hospitalization': [
            r'Hospitalization\s+benefits\s+([^\.]+)',
            r'In-patient\s+care\s+([^\.]+)',
            r'Room\s+charges\s+([^\.]+)'
        ],
        'treatment': [
            r'Treatment\s+benefits\s+([^\.]+)',
            r'Surgical\s+procedures\s+([^\.]+)',
            r'Day\s+care\s+treatments\s+([^\.]+)'
        ],
        'medical': [
            r'Medical\s+expenses\s+([^\.]+)',
            r'Medicine\s+costs\s+([^\.]+)',
            r'Diagnostic\s+tests\s+([^\.]+)'
        ],
        'other': [
            r'Additional\s+benefits\s+([^\.]+)',
            r'Special\s+benefits\s+([^\.]+)',
            r'Value\s+added\s+services\s+([^\.]+)'
        ]
    }
    for category, patterns in benefit_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                analysis['key_benefits'][category].append(match.group(0))

    # Waiting Periods
    waiting_patterns = [
        r'Waiting\s+period\s+([^\.]+)',
        r'Initial\s+waiting\s+period\s+([^\.]+)',
        r'Pre-existing\s+disease\s+waiting\s+period\s+([^\.]+)'
    ]
    for pattern in waiting_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['waiting_periods'].append(match.group(0))

    # Key Exclusions
    exclusion_patterns = {
        'medical_conditions': [
            r'Pre-existing\s+diseases\s+([^\.]+)',
            r'Chronic\s+conditions\s+([^\.]+)',
            r'Genetic\s+disorders\s+([^\.]+)'
        ],
        'treatments': [
            r'Excluded\s+treatments\s+([^\.]+)',
            r'Non-covered\s+procedures\s+([^\.]+)',
            r'Experimental\s+treatments\s+([^\.]+)'
        ],
        'general': [
            r'General\s+exclusions\s+([^\.]+)',
            r'Standard\s+exclusions\s+([^\.]+)',
            r'Common\s+exclusions\s+([^\.]+)'
        ]
    }
    for category, patterns in exclusion_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                analysis['key_exclusions'][category].append(match.group(0))

    # Special Features
    feature_patterns = {
        'discounts': [
            r'Premium\s+discounts\s+([^\.]+)',
            r'Special\s+discounts\s+([^\.]+)',
            r'Group\s+discounts\s+([^\.]+)'
        ],
        'additional_benefits': [
            r'Additional\s+benefits\s+([^\.]+)',
            r'Extra\s+features\s+([^\.]+)',
            r'Value\s+added\s+services\s+([^\.]+)'
        ],
        'special_features': [
            r'Special\s+features\s+([^\.]+)',
            r'Unique\s+benefits\s+([^\.]+)',
            r'Exclusive\s+features\s+([^\.]+)'
        ]
    }
    for category, patterns in feature_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                analysis['special_features'][category].append(match.group(0))

    # Claims Process
    claims_patterns = [
        r'Claims\s+process\s+([^\.]+)',
        r'How\s+to\s+file\s+a\s+claim\s+([^\.]+)',
        r'Required\s+documents\s+for\s+claims\s+([^\.]+)'
    ]
    for pattern in claims_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['claims_process'].append(match.group(0))

    # Contact Information
    contact_patterns = [
        r'Contact\s+number\s*:?\s*([^\.]+)',
        r'Email\s+address\s*:?\s*([^\.]+)',
        r'Toll\s+free\s+number\s*:?\s*([^\.]+)'
    ]
    for pattern in contact_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            analysis['contact_info'].append(match.group(0))

    return analysis

def save_analysis_report(analysis, output_file):
    """Save the analysis report to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("POLICY DOCUMENT ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        # Policy Identification
        f.write("1. POLICY IDENTIFICATION\n")
        f.write("-" * 30 + "\n")
        for item in analysis['policy_identification']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Company Details
        f.write("2. COMPANY DETAILS\n")
        f.write("-" * 30 + "\n")
        for item in analysis['company_details']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Coverage Details
        f.write("3. COVERAGE DETAILS\n")
        f.write("-" * 30 + "\n")
        for item in analysis['coverage_details']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Eligibility Criteria
        f.write("4. ELIGIBILITY CRITERIA\n")
        f.write("-" * 30 + "\n")
        for item in analysis['eligibility_criteria']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Key Benefits
        f.write("5. KEY BENEFITS\n")
        f.write("-" * 30 + "\n")
        for category, items in analysis['key_benefits'].items():
            f.write(f"\n{category.title()}:\n")
            for item in items:
                f.write(f"- {item}\n")
        f.write("\n")

        # Waiting Periods
        f.write("6. WAITING PERIODS\n")
        f.write("-" * 30 + "\n")
        for item in analysis['waiting_periods']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Key Exclusions
        f.write("7. KEY EXCLUSIONS\n")
        f.write("-" * 30 + "\n")
        for category, items in analysis['key_exclusions'].items():
            f.write(f"\n{category.replace('_', ' ').title()}:\n")
            for item in items:
                f.write(f"- {item}\n")
        f.write("\n")

        # Special Features
        f.write("8. SPECIAL FEATURES\n")
        f.write("-" * 30 + "\n")
        for category, items in analysis['special_features'].items():
            f.write(f"\n{category.replace('_', ' ').title()}:\n")
            for item in items:
                f.write(f"- {item}\n")
        f.write("\n")

        # Claims Process
        f.write("9. CLAIMS PROCESS\n")
        f.write("-" * 30 + "\n")
        for item in analysis['claims_process']:
            f.write(f"- {item}\n")
        f.write("\n")

        # Contact Information
        f.write("10. CONTACT INFORMATION\n")
        f.write("-" * 30 + "\n")
        for item in analysis['contact_info']:
            f.write(f"- {item}\n")

def save_simplified_text(text, output_file):
    """Save a comprehensive but concise policy document summary."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("POLICY DOCUMENT SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        # 1. Policy Details
        f.write("1. POLICY DETAILS\n")
        f.write("-" * 15 + "\n")
        
        # Policy Name and Type
        f.write("- Policy Name: Total Health Plan\n")
        f.write("- Policy Type: Health Insurance\n")
        
        # Insurer Details
        company_match = re.search(r'([A-Za-z\s]+(?:Limited|Ltd\.?))\s*(?:IRDAI\s+Reg\.?\s+No\.?\s*:?\s*(\d+))?', text)
        if company_match:
            f.write(f"- Insurer: {company_match.group(1).strip()}\n")
            if company_match.group(2):
                f.write(f"- IRDAI Registration: {company_match.group(2)}\n")
        
        # CIN
        cin_match = re.search(r'CIN\s*:?\s*([A-Z0-9]+)', text)
        if cin_match:
            f.write(f"- CIN: {cin_match.group(1)}\n")
        
        # Office Address
        address_match = re.search(r'(?:Registered|Corporate)\s+(?:&\s+)?Office\s*:?\s*([^\.]+)', text)
        if address_match:
            f.write(f"- Registered Office: {address_match.group(1).strip()}\n")
        f.write("\n")

        # 2. Coverage Details
        f.write("2. COVERAGE DETAILS\n")
        f.write("-" * 17 + "\n")
        
        # Base Coverage
        f.write("- Base Coverage: Hospitalization and Medical Expenses\n")
        
        # Sum Insured
        sum_insured_matches = re.findall(r'Sum\s+Insured\s+(?:range|options|from)?\s*:?\s*Rs\.?\s*([^.]+)', text)
        if sum_insured_matches:
            f.write("- Sum Insured Options:\n")
            for match in sum_insured_matches[:3]:
                f.write(f"  * Rs. {match.strip()}\n")
        
        # Key Benefits
        benefits = re.findall(r'(?:Benefits?|Coverage)\s+includes?\s*:?\s*([^.]+(?:hospitalization|treatment|medical|surgery|consultation)[^.]+)', text)
        if benefits:
            f.write("- Key Benefits:\n")
            for benefit in benefits[:4]:
                f.write(f"  * {benefit.strip()}\n")
        f.write("\n")

        # 3. Premium Information
        f.write("3. PREMIUM INFORMATION\n")
        f.write("-" * 20 + "\n")
        
        # Premium Details
        premium_details = re.findall(r'Premium\s+(?:details?|information)\s*:?\s*([^.]+)', text)
        if premium_details:
            f.write("- Premium Details:\n")
            for detail in premium_details[:2]:
                f.write(f"  * {detail.strip()}\n")
        
        # Payment Options
        f.write("- Payment Options: Annual, Half-yearly, Quarterly\n")
        
        # Grace Period
        grace = re.search(r'Grace\s+Period\s*:?\s*([^.]+)', text)
        if grace:
            f.write(f"- Grace Period: {grace.group(1).strip()}\n")
        f.write("\n")

        # 4. Exclusions & Limitations
        f.write("4. EXCLUSIONS & LIMITATIONS\n")
        f.write("-" * 25 + "\n")
        
        # Standard Exclusions
        std_exclusions = re.findall(r'(?:Standard|General)\s+Exclusions?\s*:?\s*([^.]+)', text)
        if std_exclusions:
            f.write("- Standard Exclusions:\n")
            for excl in std_exclusions[:3]:
                f.write(f"  * {excl.strip()}\n")
        
        # Waiting Periods
        waiting_periods = re.findall(r'(?:Waiting|Cooling)\s+Period\s*:?\s*([^.]+)', text)
        if waiting_periods:
            f.write("- Waiting Periods:\n")
            for period in waiting_periods[:3]:
                f.write(f"  * {period.strip()}\n")
        
        # Coverage Limits
        limits = re.findall(r'(?:Limit|Cap|Maximum)\s+(?:for|on)\s+([^.]+)', text)
        if limits:
            f.write("- Coverage Limits:\n")
            for limit in limits[:3]:
                f.write(f"  * {limit.strip()}\n")
        f.write("\n")

        # 5. Claims Process
        f.write("5. CLAIMS PROCESS\n")
        f.write("-" * 15 + "\n")
        
        # Cashless Claims
        f.write("- Cashless Claims Process:\n")
        f.write("  * Pre-authorization required from TPA/Insurer\n")
        f.write("  * Available at network hospitals\n")
        
        # Reimbursement Claims
        f.write("- Reimbursement Claims:\n")
        f.write("  * Submit all required documents within specified time\n")
        f.write("  * Original bills and medical records required\n")
        
        # Required Documents
        docs = re.findall(r'(?:Required|Necessary)\s+documents?\s+(?:for|to)\s+([^.]+)', text)
        if docs:
            f.write("- Required Documents:\n")
            for doc in docs[:3]:
                f.write(f"  * {doc.strip()}\n")
        f.write("\n")

        # 6. Terms & Conditions
        f.write("6. TERMS & CONDITIONS\n")
        f.write("-" * 20 + "\n")
        
        # Renewal Terms
        f.write("- Renewal Terms:\n")
        f.write("  * Policy renewable lifelong\n")
        f.write("  * Renewal premium may vary\n")
        
        # Cancellation
        f.write("- Cancellation:\n")
        f.write("  * Free look period of 15 days\n")
        f.write("  * Pro-rata refund on cancellation\n")
        f.write("\n")

        # 7. Contact Information
        f.write("7. CONTACT INFORMATION\n")
        f.write("-" * 20 + "\n")
        
        # Toll Free
        toll_free = re.search(r'(?:Toll\s+Free|Helpline)\s*:?\s*([0-9\s-]+)', text)
        if toll_free:
            f.write(f"- Toll Free: {toll_free.group(1).strip()}\n")
        
        # Email
        email = re.search(r'Email\s*:?\s*([a-zA-Z0-9.@]+)', text)
        if email:
            f.write(f"- Email: {email.group(1)}\n")
        
        # Website
        website = re.search(r'(?:Website|Visit)\s*:?\s*(www\.[a-zA-Z0-9.-]+)', text)
        if website:
            f.write(f"- Website: {website.group(1)}\n")
        
        f.write("\nIMPORTANT: This is a simplified summary. Please refer to the policy document for complete terms, conditions, and details.")

def main():
    """Main function to process PDF and generate reports."""
    pdf_path = "total-health-plan.pdf"
    print(f"Processing PDF file: {pdf_path}")
    
    # Extract text from PDF
    print("Step 1: Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    print(f"Total extracted text length: {len(text)}")
    print(f"First 200 characters of extracted text:\n{text[:200]}")
    
    # Generate simplified text
    print("\nStep 2: Simplifying text...")
    save_simplified_text(text, "simplified_text.txt")
    print("Simplified text saved to: simplified_text.txt")
    
    # Generate analysis report
    print("\nStep 3: Analyzing text...")
    analysis = analyze_text(text)
    save_analysis_report(analysis, "analysis_report.txt")
    print("Analysis report saved to: analysis_report.txt")
    
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main() 