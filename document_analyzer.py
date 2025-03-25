import PyPDF2
import re
import nltk
from nltk.tokenize import sent_tokenize
import os
import sys
from datetime import datetime

class DocumentAnalyzer:
    def __init__(self, file_path):
        self.file_path = os.path.abspath(file_path)
        self.text_content = ""
        self.analysis_results = []
        
        # Check if file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PDF file not found at: {self.file_path}")
            
        # Print file info
        file_size = os.path.getsize(self.file_path)
        print(f"Processing PDF file: {self.file_path}")
        print(f"File size: {file_size / 1024:.2f} KB")

    def extract_text(self):
        """Extract text from PDF file."""
        try:
            with open(self.file_path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Print total pages
                print(f"Total pages in PDF: {len(pdf_reader.pages)}")
                
                # Reset text content
                self.text_content = ""
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Print page stats
                    print(f"Page {page_num + 1}: {len(text)} characters")
                    
                    if text.strip():
                        self.text_content += text + "\n"
                    else:
                        print(f"Warning: Page {page_num + 1} contains no text")
                
                # Print total extracted text stats
                print(f"Total extracted text length: {len(self.text_content)}")
                print("First 200 characters of extracted text:")
                print(self.text_content[:200])
                
                return True
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            import traceback
            print("Traceback:")
            print(traceback.format_exc())
            return False

    def simplify_text(self):
        """Clean and simplify the extracted text, focusing on key policy information."""
        try:
            # Clean the text
            text = self.text_content
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Initialize important sections with headers
            important_sections = [
                "POLICY DOCUMENT SUMMARY",
                "=" * 50,
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 50,
                ""
            ]
            
            # Extract policy identification
            policy_match = re.search(r'Policy\s+(?:Number|No\.?|ID)?\s*:?\s*([A-Z0-9-]+)', text)
            if policy_match:
                important_sections.extend([
                    "1. POLICY IDENTIFICATION",
                    "-" * 30,
                    f"Policy ID: {policy_match.group(1)}",
                    ""
                ])
            
            # Extract company details
            company_match = re.search(r'([A-Za-z\s]+(?:Limited|Ltd\.?))\s+IRDAI\s+Reg\.?\s+No\.?\s*:?\s*(\d+)', text)
            if company_match:
                important_sections.extend([
                    "2. INSURANCE COMPANY DETAILS",
                    "-" * 30,
                    f"Company Name: {company_match.group(1)}",
                    f"IRDAI Registration Number: {company_match.group(2)}",
                    ""
                ])
            
            # Extract sum insured range with detailed breakdown
            sum_insured = re.search(r'Sum\s+Insured\s+(?:range|options|from)?\s*:?\s*Rs\.?\s*([^.]+)', text, re.IGNORECASE)
            if sum_insured:
                important_sections.extend([
                    "3. COVERAGE DETAILS",
                    "-" * 30,
                    f"Sum Insured Range: Rs. {sum_insured.group(1)}",
                    ""
                ])
                
                # Extract additional coverage details
                coverage_details = re.findall(r'(?:coverage|sum insured)\s+(?:for|of)\s+([^.]+?)(?=\.|and)', text, re.IGNORECASE)
                if coverage_details:
                    important_sections.append("Coverage Breakdown:")
                    for detail in coverage_details[:5]:
                        important_sections.append(f"- {detail.strip()}")
                    important_sections.append("")
            
            # Extract eligibility with detailed criteria
            eligibility = re.search(r'(?:Eligibility|Age limit)\s*:?\s*([^.]+(?:years|age)[^.]+)', text, re.IGNORECASE)
            if eligibility:
                important_sections.extend([
                    "4. ELIGIBILITY CRITERIA",
                    "-" * 30,
                    f"Basic Eligibility: {eligibility.group(1)}",
                    ""
                ])
                
                # Extract additional eligibility details
                eligibility_details = re.findall(r'(?:eligible|qualify)\s+for\s+([^.]+?)(?=\.|and)', text, re.IGNORECASE)
                if eligibility_details:
                    important_sections.append("Additional Eligibility Requirements:")
                    for detail in eligibility_details[:3]:
                        important_sections.append(f"- {detail.strip()}")
                    important_sections.append("")
            
            # Extract key benefits with detailed descriptions
            benefits = []
            benefit_matches = re.findall(r'(?:Benefits?|Coverage)\s*:?\s*([^.]+(?:hospitalization|treatment|medical)[^.]+)', text, re.IGNORECASE)
            if benefit_matches:
                important_sections.extend([
                    "5. KEY BENEFITS AND COVERAGE",
                    "-" * 30,
                ])
                
                # Group benefits by category
                benefit_categories = {
                    'Hospitalization': [],
                    'Treatment': [],
                    'Medical': [],
                    'Other': []
                }
                
                for benefit in benefit_matches:
                    benefit = benefit.strip()
                    if 'hospital' in benefit.lower():
                        benefit_categories['Hospitalization'].append(benefit)
                    elif 'treatment' in benefit.lower():
                        benefit_categories['Treatment'].append(benefit)
                    elif 'medical' in benefit.lower():
                        benefit_categories['Medical'].append(benefit)
                    else:
                        benefit_categories['Other'].append(benefit)
                
                # Add categorized benefits
                for category, benefits_list in benefit_categories.items():
                    if benefits_list:
                        important_sections.append(f"\n{category} Benefits:")
                        for benefit in benefits_list[:3]:
                            important_sections.append(f"- {benefit}")
                important_sections.append("")
            
            # Extract waiting periods with detailed explanations
            waiting_periods = re.findall(r'(?:waiting\s+period)\s*:?\s*([^.]+(?:month|year|day)[^.]+)', text, re.IGNORECASE)
            if waiting_periods:
                important_sections.extend([
                    "6. WAITING PERIODS",
                    "-" * 30,
                ])
                
                for period in waiting_periods[:3]:
                    important_sections.append(f"- {period.strip()}")
                
                # Add waiting period exceptions
                exceptions = re.findall(r'(?:exception|excluded from waiting period)[^.]*?(?:condition|disease)[^.]+', text, re.IGNORECASE)
                if exceptions:
                    important_sections.append("\nWaiting Period Exceptions:")
                    for exception in exceptions[:2]:
                        important_sections.append(f"- {exception.strip()}")
                important_sections.append("")
            
            # Extract major exclusions with detailed explanations
            exclusions = re.findall(r'(?:Exclusions?|not\s+covered)\s*:?\s*([^.]+(?:condition|disease|treatment)[^.]+)', text, re.IGNORECASE)
            if exclusions:
                important_sections.extend([
                    "7. KEY EXCLUSIONS AND LIMITATIONS",
                    "-" * 30,
                ])
                
                # Group exclusions by type
                exclusion_categories = {
                    'Medical Conditions': [],
                    'Treatments': [],
                    'General': []
                }
                
                for exclusion in exclusions:
                    exclusion = exclusion.strip()
                    if any(term in exclusion.lower() for term in ['disease', 'condition', 'illness']):
                        exclusion_categories['Medical Conditions'].append(exclusion)
                    elif any(term in exclusion.lower() for term in ['treatment', 'procedure', 'surgery']):
                        exclusion_categories['Treatments'].append(exclusion)
                    else:
                        exclusion_categories['General'].append(exclusion)
                
                # Add categorized exclusions
                for category, exclusion_list in exclusion_categories.items():
                    if exclusion_list:
                        important_sections.append(f"\n{category}:")
                        for exclusion in exclusion_list[:3]:
                            important_sections.append(f"- {exclusion}")
                important_sections.append("")
            
            # Extract special features and discounts with detailed explanations
            features = re.findall(r'(?:Features?|discount)\s*:?\s*([^.]+(?:discount|bonus|benefit)[^.]+)', text, re.IGNORECASE)
            if features:
                important_sections.extend([
                    "8. SPECIAL FEATURES AND DISCOUNTS",
                    "-" * 30,
                ])
                
                # Group features by type
                feature_categories = {
                    'Discounts': [],
                    'Additional Benefits': [],
                    'Special Features': []
                }
                
                for feature in features:
                    feature = feature.strip()
                    if 'discount' in feature.lower():
                        feature_categories['Discounts'].append(feature)
                    elif 'benefit' in feature.lower():
                        feature_categories['Additional Benefits'].append(feature)
                    else:
                        feature_categories['Special Features'].append(feature)
                
                # Add categorized features
                for category, feature_list in feature_categories.items():
                    if feature_list:
                        important_sections.append(f"\n{category}:")
                        for feature in feature_list[:3]:
                            important_sections.append(f"- {feature}")
                important_sections.append("")
            
            # Add claims process information
            claims_info = re.findall(r'(?:claim|claims process)[^.]*?(?:document|submit|process)[^.]+', text, re.IGNORECASE)
            if claims_info:
                important_sections.extend([
                    "9. CLAIMS PROCESS",
                    "-" * 30,
                ])
                
                for info in claims_info[:3]:
                    important_sections.append(f"- {info.strip()}")
                important_sections.append("")
            
            # Add contact information
            contact_info = re.findall(r'(?:contact|helpline|toll free)[^.]*?(?:number|email)[^.]+', text, re.IGNORECASE)
            if contact_info:
                important_sections.extend([
                    "10. CONTACT INFORMATION",
                    "-" * 30,
                ])
                
                for info in contact_info[:2]:
                    important_sections.append(f"- {info.strip()}")
            
            # Join all sections with clear separation
            simplified_text = "\n".join(important_sections)
            
            # Save to file
            with open('simplified_text.txt', 'w', encoding='utf-8') as f:
                f.write(simplified_text)
            
            print(f"Simplified text saved to: {os.path.abspath('simplified_text.txt')}")
            return simplified_text
            
        except Exception as e:
            print(f"Error in simplify_text: {str(e)}")
            return None

    def analyze_text(self):
        """Analyze the text content for key policy information."""
        try:
            # Use original text content for analysis
            text = self.text_content
            
            if not text.strip():
                print("Error: No text to analyze")
                return False
            
            # Initialize analysis results with header
            analysis = [
                "POLICY DOCUMENT ANALYSIS REPORT",
                "=" * 50,
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 50,
                ""
            ]
            
            # Extract policy details
            policy_details = re.search(r'(Star Health Premier Insurance Policy.*?(?:Limited|Ltd).*?)(?=\n)', text)
            if policy_details:
                analysis.extend([
                    "1. POLICY OVERVIEW",
                    "-" * 30,
                    f"Policy Name: {policy_details.group(1).strip()}",
                    ""
                ])
            
            # Extract sum insured options with detailed breakdown
            sum_insured = re.findall(r'Sum\s+Insured\s*(?:of|is)?\s*Rs\.?\s*([\d,]+(?:,\d+)*(?:\.\d{2})?)\s*(?:lakhs?|Lakhs?|/-)?', text)
            if sum_insured:
                analysis.extend([
                    "2. COVERAGE AMOUNTS",
                    "-" * 30,
                ])
                
                unique_amounts = sorted(list(set(sum_insured)), key=lambda x: float(x.replace(',', '')), reverse=True)
                for amount in unique_amounts[:5]:
                    analysis.append(f"- Rs. {amount}")
                
                # Add coverage breakdown
                coverage_breakdown = re.findall(r'(?:coverage|sum insured)\s+(?:for|of)\s+([^.]+?)(?=\.|and)', text)
                if coverage_breakdown:
                    analysis.append("\nCoverage Breakdown:")
                    for detail in coverage_breakdown[:3]:
                        analysis.append(f"- {detail.strip()}")
                analysis.append("")
            
            # Extract eligibility criteria with detailed requirements
            eligibility = re.findall(r'Eligibility[^.]*(?:years?|age)[^.]+\.', text)
            if eligibility:
                analysis.extend([
                    "3. ELIGIBILITY REQUIREMENTS",
                    "-" * 30,
                ])
                
                unique_eligibility = list(set(eligibility))
                for criteria in unique_eligibility[:3]:
                    analysis.append(f"- {criteria.strip()}")
                
                # Add additional eligibility details
                additional_eligibility = re.findall(r'(?:eligible|qualify)\s+for\s+([^.]+?)(?=\.|and)', text)
                if additional_eligibility:
                    analysis.append("\nAdditional Eligibility Criteria:")
                    for detail in additional_eligibility[:2]:
                        analysis.append(f"- {detail.strip()}")
                analysis.append("")
            
            # Extract key benefits with detailed descriptions
            benefits = re.findall(r'(?:Medical [Ee]xpenses|[Tt]reatment|[Cc]overage)\s+(?:for|of|includes?)\s+([^.]+?)(?=\.|and)', text)
            if benefits:
                analysis.extend([
                    "4. BENEFITS AND COVERAGE",
                    "-" * 30,
                ])
                
                unique_benefits = list(set(benefits))
                for benefit in unique_benefits[:8]:
                    if len(benefit.strip()) > 10:
                        analysis.append(f"- {benefit.strip()}")
                
                # Add benefit categories
                benefit_categories = {
                    'Hospitalization': [],
                    'Treatment': [],
                    'Medical': [],
                    'Other': []
                }
                
                for benefit in unique_benefits:
                    if 'hospital' in benefit.lower():
                        benefit_categories['Hospitalization'].append(benefit)
                    elif 'treatment' in benefit.lower():
                        benefit_categories['Treatment'].append(benefit)
                    elif 'medical' in benefit.lower():
                        benefit_categories['Medical'].append(benefit)
                    else:
                        benefit_categories['Other'].append(benefit)
                
                analysis.append("\nBenefit Categories:")
                for category, benefit_list in benefit_categories.items():
                    if benefit_list:
                        analysis.append(f"\n{category}:")
                        for benefit in benefit_list[:3]:
                            analysis.append(f"- {benefit.strip()}")
                analysis.append("")
            
            # Extract waiting periods with detailed explanations
            waiting_periods = re.findall(r'(?:waiting period|shall be excluded)[^.]*?(?:\d+\s+(?:days?|months?|years?))[^.]+\.', text)
            if waiting_periods:
                analysis.extend([
                    "5. WAITING PERIODS",
                    "-" * 30,
                ])
                
                unique_periods = list(set(waiting_periods))
                for period in unique_periods[:4]:
                    analysis.append(f"- {period.strip()}")
                
                # Add waiting period exceptions
                exceptions = re.findall(r'(?:exception|excluded from waiting period)[^.]*?(?:condition|disease)[^.]+', text)
                if exceptions:
                    analysis.append("\nWaiting Period Exceptions:")
                    for exception in exceptions[:2]:
                        analysis.append(f"- {exception.strip()}")
                analysis.append("")
            
            # Extract exclusions with detailed explanations
            exclusions = re.findall(r'(?:Exclusions?|not covered|excluded)[^.]*?(?:following|expenses?|treatment)[^.]+?(?:\.|\n)', text)
            if exclusions:
                analysis.extend([
                    "6. EXCLUSIONS AND LIMITATIONS",
                    "-" * 30,
                ])
                
                unique_exclusions = list(set(exclusions))
                for exclusion in unique_exclusions[:8]:
                    if len(exclusion.strip()) > 15:
                        analysis.append(f"- {exclusion.strip()}")
                
                # Add exclusion categories
                exclusion_categories = {
                    'Medical Conditions': [],
                    'Treatments': [],
                    'General': []
                }
                
                for exclusion in unique_exclusions:
                    if any(term in exclusion.lower() for term in ['disease', 'condition', 'illness']):
                        exclusion_categories['Medical Conditions'].append(exclusion)
                    elif any(term in exclusion.lower() for term in ['treatment', 'procedure', 'surgery']):
                        exclusion_categories['Treatments'].append(exclusion)
                    else:
                        exclusion_categories['General'].append(exclusion)
                
                analysis.append("\nExclusion Categories:")
                for category, exclusion_list in exclusion_categories.items():
                    if exclusion_list:
                        analysis.append(f"\n{category}:")
                        for exclusion in exclusion_list[:3]:
                            analysis.append(f"- {exclusion.strip()}")
                analysis.append("")
            
            # Extract special features with detailed descriptions
            features = re.findall(r'(?:Features?|Benefits?)[^.]*?(?:provides?|includes?|offers?)[^.]+\.', text)
            if features:
                analysis.extend([
                    "7. SPECIAL FEATURES",
                    "-" * 30,
                ])
                
                unique_features = list(set(features))
                for feature in unique_features[:5]:
                    if len(feature.strip()) > 15:
                        analysis.append(f"- {feature.strip()}")
                
                # Add feature categories
                feature_categories = {
                    'Discounts': [],
                    'Additional Benefits': [],
                    'Special Features': []
                }
                
                for feature in unique_features:
                    if 'discount' in feature.lower():
                        feature_categories['Discounts'].append(feature)
                    elif 'benefit' in feature.lower():
                        feature_categories['Additional Benefits'].append(feature)
                    else:
                        feature_categories['Special Features'].append(feature)
                
                analysis.append("\nFeature Categories:")
                for category, feature_list in feature_categories.items():
                    if feature_list:
                        analysis.append(f"\n{category}:")
                        for feature in feature_list[:3]:
                            analysis.append(f"- {feature.strip()}")
                analysis.append("")
            
            # Extract premium discounts with detailed explanations
            discounts = re.findall(r'(?:discount|reduction)[^.]*?(?:\d+%|percent)[^.]+\.', text)
            if discounts:
                analysis.extend([
                    "8. PREMIUM DISCOUNTS",
                    "-" * 30,
                ])
                
                unique_discounts = list(set(discounts))
                for discount in unique_discounts[:4]:
                    analysis.append(f"- {discount.strip()}")
                
                # Add discount conditions
                discount_conditions = re.findall(r'(?:condition|requirement)\s+for\s+discount[^.]*?(?:policy|premium)[^.]+', text)
                if discount_conditions:
                    analysis.append("\nDiscount Conditions:")
                    for condition in discount_conditions[:2]:
                        analysis.append(f"- {condition.strip()}")
                analysis.append("")
            
            # Add claims process information
            claims_info = re.findall(r'(?:claim|claims process)[^.]*?(?:document|submit|process)[^.]+', text)
            if claims_info:
                analysis.extend([
                    "9. CLAIMS PROCESS",
                    "-" * 30,
                ])
                
                unique_claims = list(set(claims_info))
                for claim in unique_claims[:4]:
                    analysis.append(f"- {claim.strip()}")
                
                # Add required documents
                documents = re.findall(r'(?:document|paper|proof)\s+required[^.]*?(?:claim|submission)[^.]+', text)
                if documents:
                    analysis.append("\nRequired Documents:")
                    for doc in documents[:3]:
                        analysis.append(f"- {doc.strip()}")
                analysis.append("")
            
            # Add contact information
            contact_info = re.findall(r'(?:contact|helpline|toll free)[^.]*?(?:number|email)[^.]+', text)
            if contact_info:
                analysis.extend([
                    "10. CONTACT INFORMATION",
                    "-" * 30,
                ])
                
                unique_contacts = list(set(contact_info))
                for contact in unique_contacts[:3]:
                    analysis.append(f"- {contact.strip()}")
            
            # Save analysis results
            self.analysis_results = analysis
            with open('analysis_report.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(analysis))
            print(f"Analysis report saved to: {os.path.abspath('analysis_report.txt')}")
            
            return True
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python document_analyzer.py <pdf_file>")
        return
        
    pdf_file = sys.argv[1]
    
    try:
        analyzer = DocumentAnalyzer(pdf_file)
        
        print("\nStep 1: Extracting text from PDF...")
        if not analyzer.extract_text():
            print("Failed to extract text from PDF")
            return
            
        print("\nStep 2: Simplifying text...")
        if not analyzer.simplify_text():
            print("Failed to simplify text")
            return
            
        print("\nStep 3: Analyzing text...")
        if not analyzer.analyze_text():
            print("Failed to analyze text")
            return
            
        print("\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 