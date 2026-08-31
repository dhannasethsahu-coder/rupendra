import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re
from urllib.parse import urlparse

class SimpleWebsiteAuditor:
    def __init__(self):
        pass
    
    def analyze_website(self, url):
        """Main analysis function"""
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'seo_analysis': {},
            'security_analysis': {},
            'performance_analysis': {},
            'scores': {},
            'recommendations': []
        }
        
        try:
            # Get website content
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SEO Analysis
            seo = {}
            seo['title'] = soup.title.string if soup.title else 'Missing Title'
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            seo['meta_description'] = meta_desc.get('content') if meta_desc else 'Missing'
            
            h1_tags = soup.find_all('h1')
            seo['h1_count'] = len(h1_tags)
            seo['h1_content'] = [h.text for h in h1_tags[:3]]
            
            images = soup.find_all('img')
            seo['total_images'] = len(images)
            seo['images_with_alt'] = sum(1 for img in images if img.get('alt'))
            
            links = soup.find_all('a', href=True)
            base_domain = urlparse(url).netloc
            seo['internal_links'] = sum(1 for link in links if base_domain in link['href'])
            seo['external_links'] = sum(1 for link in links if 'http' in link['href'] and base_domain not in link['href'])
            
            # Check mobile viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            seo['mobile_friendly'] = bool(viewport)
            
            results['seo_analysis'] = seo
            
            # Security Analysis
            security = {}
            # Check SSL
            security['has_ssl'] = url.startswith('https')
            
            # Check security headers
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security']
            for header in security_headers:
                security[header] = response.headers.get(header) is not None
            
            results['security_analysis'] = security
            
            # Performance Analysis
            performance = {}
            # Measure load time
            start_time = time.time()
            requests.get(url, timeout=5)
            load_time = time.time() - start_time
            performance['load_time'] = round(load_time, 2)
            
            # Page size
            performance['page_size_kb'] = round(len(response.content) / 1024, 2)
            
            # Check compression
            performance['compression'] = response.headers.get('Content-Encoding') is not None
            
            results['performance_analysis'] = performance
            
            # Calculate scores
            results['scores'] = self.calculate_scores(results)
            
            # Generate recommendations
            results['recommendations'] = self.generate_recommendations(results)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def calculate_scores(self, results):
        """Calculate scores based on analysis"""
        scores = {'seo': 50, 'security': 50, 'performance': 50, 'overall': 50}
        
        seo = results.get('seo_analysis', {})
        if seo:
            score = 30
            if seo.get('title') and 'Missing' not in seo['title']:
                score += 15
            if seo.get('meta_description') and 'Missing' not in seo['meta_description']:
                score += 15
            if seo.get('h1_count', 0) > 0:
                score += 10
            if seo.get('images_with_alt', 0) > 0:
                score += 10
            if seo.get('mobile_friendly'):
                score += 10
            if seo.get('internal_links', 0) > 5:
                score += 10
            scores['seo'] = min(100, score)
        
        security = results.get('security_analysis', {})
        if security:
            score = 40
            if security.get('has_ssl'):
                score += 20
            if security.get('X-Frame-Options'):
                score += 15
            if security.get('X-Content-Type-Options'):
                score += 15
            if security.get('Strict-Transport-Security'):
                score += 10
            scores['security'] = min(100, score)
        
        performance = results.get('performance_analysis', {})
        if performance:
            score = 40
            if performance.get('load_time', 10) < 2:
                score += 30
            elif performance.get('load_time', 10) < 4:
                score += 20
            else:
                score += 10
            if performance.get('compression'):
                score += 15
            if performance.get('page_size_kb', 5000) < 1000:
                score += 15
            scores['performance'] = min(100, score)
        
        scores['overall'] = (scores['seo'] + scores['security'] + scores['performance']) / 3
        return scores
    
    def generate_recommendations(self, results):
        """Generate recommendations based on findings"""
        recommendations = []
        
        seo = results.get('seo_analysis', {})
        if seo.get('title') and 'Missing' in seo['title']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'description': 'Add a title tag to your website - this is crucial for search engines',
                'effort': 'Low'
            })
        
        if seo.get('meta_description') and 'Missing' in seo['meta_description']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'description': 'Add a meta description to improve click-through rates from search results',
                'effort': 'Low'
            })
        
        if seo.get('h1_count', 0) == 0:
            recommendations.append({
                'category': 'SEO',
                'priority': 'Medium',
                'description': 'Add an H1 heading to help search engines understand your page content',
                'effort': 'Low'
            })
        
        total_images = seo.get('total_images', 0)
        if total_images > 0:
            with_alt = seo.get('images_with_alt', 0)
            without_alt = total_images - with_alt
            if without_alt > 0:
                recommendations.append({
                    'category': 'SEO',
                    'priority': 'Medium',
                    'description': f'Add alt text to {without_alt} images for better accessibility and SEO',
                    'effort': 'Medium'
                })
        
        security = results.get('security_analysis', {})
        if not security.get('has_ssl'):
            recommendations.append({
                'category': 'Security',
                'priority': 'Critical',
                'description': 'Install an SSL certificate to secure your website and build trust',
                'effort': 'Low'
            })
        
        performance = results.get('performance_analysis', {})
        if performance.get('load_time', 10) > 3:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'description': f'Your page loads in {performance["load_time"]}s - optimize for faster loading',
                'effort': 'Medium'
            })
        
        if not performance.get('compression'):
            recommendations.append({
                'category': 'Performance',
                'priority': 'Medium',
                'description': 'Enable GZIP compression to reduce page size and speed up loading',
                'effort': 'Low'
            })
        
        return recommendations

def generate_html_report(results):
    """Generate a simple HTML report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Audit Report</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
            .score-box {{ display: inline-block; width: 30%; margin: 10px; padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center; }}
            .score {{ font-size: 36px; font-weight: bold; }}
            .rec {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }}
            .priority-critical {{ border-left-color: #dc3545; }}
            .priority-high {{ border-left-color: #fd7e14; }}
            .priority-medium {{ border-left-color: #ffc107; }}
            .btn {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 Website Audit Report</h1>
                <p><strong>URL:</strong> {results['url']}</p>
                <p><strong>Date:</strong> {results['timestamp']}</p>
                <p><strong>Overall Score:</strong> {results['scores']['overall']:.1f}/100</p>
            </div>
            
            <h2>📊 Scores</h2>
            <div>
                <div class="score-box"><div class="score" style="color: #667eea">{results['scores']['seo']:.1f}</div>SEO</div>
                <div class="score-box"><div class="score" style="color: #dc3545">{results['scores']['security']:.1f}</div>Security</div>
                <div class="score-box"><div class="score" style="color: #28a745">{results['scores']['performance']:.1f}</div>Performance</div>
            </div>
            
            <h2>🎯 Recommendations</h2>
    """
    
    for rec in results.get('recommendations', []):
        priority_class = f"priority-{rec['priority'].lower()}"
        html += f"""
            <div class="rec {priority_class}">
                <strong>{rec['category']}</strong> - {rec['priority']} Priority<br>
                {rec['description']}<br>
                <small>Effort: {rec['effort']}</small>
            </div>
        """
    
    html += """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-top: 20px;">
                <h2>🚀 Ready to Fix These Issues?</h2>
                <p>Contact us for a free consultation!</p>
                <a href="#" class="btn">Get a Quote</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    st.set_page_config(page_title="AI Website Auditor", page_icon="🚀", layout="wide")
    
    st.title("🚀 AI Website Auditor")
    st.markdown("Analyze any website for SEO, security, and performance issues")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    target_url = st.sidebar.text_input("Website URL", placeholder="https://example.com")
    
    if st.sidebar.button("🚀 Start Audit", type="primary"):
        if not target_url:
            st.error("Please enter a website URL")
            return
        
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url
        
        with st.spinner("🔄 Analyzing website..."):
            auditor = SimpleWebsiteAuditor()
            results = auditor.analyze_website(target_url)
        
        if 'error' in results:
            st.error(f"Error: {results['error']}")
            return
        
        # Display scores
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("SEO Score", f"{results['scores']['seo']:.1f}/100")
        with col2:
            st.metric("Security Score", f"{results['scores']['security']:.1f}/100")
        with col3:
            st.metric("Performance Score", f"{results['scores']['performance']:.1f}/100")
        
        st.metric("Overall Score", f"{results['scores']['overall']:.1f}/100")
        
        # Show recommendations
        st.subheader("📋 Recommendations")
        for rec in results['recommendations']:
            with st.expander(f"🔴 {rec['category']} - {rec['priority']} Priority"):
                st.write(f"**{rec['description']}**")
                st.write(f"Effort: {rec['effort']}")
        
        # Generate and display report
        html_report = generate_html_report(results)
        st.subheader("📄 Report Preview")
        st.components.v1.html(html_report, height=500, scrolling=True)
        
        # Download button
        st.download_button(
            label="📥 Download HTML Report",
            data=html_report,
            file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
        
        st.success("✅ Analysis complete!")

if __name__ == "__main__":
    main()
