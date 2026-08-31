#!/usr/bin/env python3
"""
Lead Generation Agent - AI Website Auditor
Finds prospects, audits websites, and sends personalized emails
"""

import os
import sys
import time
import json
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from urllib.parse import urlparse

# Import the auditor
from app import SimpleWebsiteAuditor, generate_business_report

class LeadGenerationAgent:
    def __init__(self):
        self.auditor = SimpleWebsiteAuditor()
        self.prospects = []
        self.results = []
        
    def find_prospects(self, keyword, max_results=5):
        """Find potential customers using multiple sources"""
        print(f"🔍 Searching for prospects with keyword: {keyword}")
        
        # Method 1: Use a list of common business domains for testing
        # (This is a fallback when web search doesn't work)
        test_prospects = [
            {'url': 'https://example.com', 'domain': 'example.com'},
            {'url': 'https://testsite.com', 'domain': 'testsite.com'},
            {'url': 'https://demoweb.com', 'domain': 'demoweb.com'},
            {'url': 'https://samplecompany.com', 'domain': 'samplecompany.com'},
            {'url': 'https://mybusiness.com', 'domain': 'mybusiness.com'},
        ]
        
        # Try to use Google search first
        try:
            import re
            from urllib.parse import urlparse
            
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&num={max_results * 2}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract URLs from the response
                urls = re.findall(r'https?://[^\s<>"]+', response.text)
                
                seen = set()
                for url in urls:
                    # Skip unwanted domains
                    skip_patterns = ['google', 'youtube', 'facebook', 'twitter', 'linkedin', 'instagram', 'wikipedia']
                    if any(skip in url.lower() for skip in skip_patterns):
                        continue
                    
                    # Parse the URL
                    parsed = urlparse(url)
                    domain = parsed.netloc
                    
                    # Clean domain (remove www.)
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    
                    if domain and domain not in seen and '.' in domain:
                        seen.add(domain)
                        self.prospects.append({
                            'url': f"https://{domain}",
                            'domain': domain,
                            'keyword': keyword,
                            'found_date': datetime.now().isoformat()
                        })
                        
                        if len(self.prospects) >= max_results:
                            break
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
        
        # If no prospects found, use test prospects
        if not self.prospects:
            print("📌 Using test prospects for demonstration...")
            for p in test_prospects[:max_results]:
                self.prospects.append({
                    'url': p['url'],
                    'domain': p['domain'],
                    'keyword': keyword,
                    'found_date': datetime.now().isoformat()
                })
        
        print(f"✅ Found {len(self.prospects)} prospects")
        for p in self.prospects:
            print(f"   - {p['url']}")

    def audit_website(self, url):
        """Audit a single website"""
        print(f"📊 Auditing: {url}")
        
        try:
            # Run the audit
            results = self.auditor.analyze_website(url)
            
            # Check if audit was successful
            if 'error' in results:
                print(f"❌ Audit failed: {results['error']}")
                return None
            
            # Generate the business report
            report_html = generate_business_report(results)
            
            # Save the report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = url.replace('https://', '').replace('http://', '').replace('/', '_')
            report_filename = f"reports/lead_report_{domain}_{timestamp}.html"
            
            # Create reports directory if it doesn't exist
            os.makedirs('reports', exist_ok=True)
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            print(f"✅ Report saved: {report_filename}")
            
            # Extract key data for email
            scores = results.get('scores', {})
            overall = scores.get('overall', 0)
            impact = results.get('business_impact', {})
            
            return {
                'url': url,
                'scores': scores,
                'overall_score': overall,
                'revenue_potential': impact.get('revenue_loss', 0),
                'traffic_potential': impact.get('traffic_loss', 0),
                'risk_level': impact.get('risk_level', 'Unknown'),
                'report_path': report_filename,
                'report_html': report_html,
                'prospect': {
                    'url': url,
                    'domain': domain
                }
            }
            
        except Exception as e:
            print(f"❌ Audit error for {url}: {e}")
            return None
    
    def send_email(self, result):
        """Send personalized email with report attached"""
        if not result:
            return
        
        prospect = result.get('prospect', {})
        url = prospect.get('url', 'Unknown')
        domain = prospect.get('domain', 'Unknown')
        report_path = result.get('report_path', '')
        overall_score = result.get('overall_score', 0)
        revenue_potential = result.get('revenue_potential', 0)
        
        print(f"📧 Preparing email for: {domain}")
        
        # Email configuration (you need to set these up)
        sender_email = "your_email@gmail.com"  # CHANGE THIS
        sender_password = "your_app_password"  # CHANGE THIS
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Recipient (for testing, send to yourself)
        recipient_email = "your_email@gmail.com"  # CHANGE THIS
        
        # Subject line
        subject = f"Website Growth Report for {domain}"
        
        # Email body (personalized)
        body = f"""
Dear {domain} Team,

I recently analyzed your website and wanted to share some insights that could help grow your business.

📊 Key Findings:
- Overall Score: {overall_score}/100
- Potential Revenue Increase: ${revenue_potential:.0f}/month
- Traffic Opportunity: +{result.get('traffic_potential', 0)} visitors/month
- Risk Level: {result.get('risk_level', 'Unknown')}

I've attached a detailed Business Growth Report that shows specific opportunities to:
✅ Increase your website traffic
✅ Convert more visitors into customers
✅ Improve your online presence

This report is completely free - I'm offering it as a way to show how our services can help businesses like yours grow.

Would you be open to a quick 15-minute call to discuss the findings?

Best regards,
AI Website Auditor Team
P.S. If you're not interested, no problem - just ignore this email.
"""
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report if it exists
            if report_path and os.path.exists(report_path):
                with open(report_path, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(report_path)}'
                    )
                    msg.attach(attachment)
                    print(f"📎 Attached: {os.path.basename(report_path)}")
            else:
                print("⚠️ No report file found to attach")
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {domain}")
            
        except Exception as e:
            print(f"❌ Failed to send email to {domain}: {e}")
            print("💡 To enable email, update sender_email and sender_password in the code")
    
    def run(self, keyword, max_prospects=5, send_emails=False):
        """Full lead generation workflow"""
        print("🚀 Starting Lead Generation Campaign")
        print("=" * 50)
        print(f"📌 Keyword: {keyword}")
        print(f"📌 Max Prospects: {max_prospects}")
        print(f"📌 Send Emails: {send_emails}")
        print("=" * 50)
        
        # 1. Find prospects
        self.find_prospects(keyword, max_prospects)
        
        if not self.prospects:
            print("❌ No prospects found. Exiting.")
            return
        
        # 2. Audit each prospect
        print("\n📊 Starting audits...")
        for i, prospect in enumerate(self.prospects, 1):
            print(f"\n[{i}/{len(self.prospects)}] Processing: {prospect['url']}")
            result = self.audit_website(prospect['url'])
            if result:
                result['prospect'] = prospect
                self.results.append(result)
            time.sleep(2)  # Be polite to servers
        
        # 3. Send emails (if enabled)
        if send_emails:
            print("\n📧 Sending emails...")
            for result in self.results:
                self.send_email(result)
                time.sleep(1)
        else:
            print("\n💡 Email sending is disabled. Set send_emails=True to enable.")
            print("📁 Reports saved in: reports/")
            for result in self.results:
                print(f"   - {result.get('report_path', 'No report')}")
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 CAMPAIGN SUMMARY")
        print("=" * 50)
        print(f"✅ Prospects Found: {len(self.prospects)}")
        print(f"✅ Audits Completed: {len(self.results)}")
        
        if self.results:
            avg_score = sum(r.get('overall_score', 0) for r in self.results) / len(self.results)
            print(f"📈 Average Score: {avg_score:.1f}/100")
            
            total_revenue = sum(r.get('revenue_potential', 0) for r in self.results)
            print(f"💰 Total Revenue Opportunity: ${total_revenue:.0f}/month")
        
        print("\n✅ Lead Generation Campaign Complete!")


if __name__ == "__main__":
    agent = LeadGenerationAgent()
    agent.run("web development agency", max_prospects=3)
