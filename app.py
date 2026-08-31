from dotenv import load_dotenv
# New imports for enhanced features
from readability import Document
import colorama
import concurrent.futures
from urllib.parse import urljoin
import hashlib

import ssl
import socket
import OpenSSL
import dns.resolver

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
# Advanced Security Imports
import publicsuffix2
import pygments
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer as JSONLexer
# Bug Bounty Recon Imports
import subprocess
import shodan
import nmap
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed



# Load environment variables
load_dotenv()

class SimpleWebsiteAuditor:
    def __init__(self):
        pass

    def analyze_competitors(self, url):
        """Analyze top competitors for the website"""
        try:
            from urllib.parse import urlparse
            import requests
            from bs4 import BeautifulSoup
            
            # Extract domain for search
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Try to find competitors by searching the domain name
            search_query = domain.replace('.', ' ')
            competitor_urls = []
            
            # Check if domain exists and get related sites
            try:
                response = requests.get(f"https://api.duckduckgo.com/?q={search_query}&format=json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'RelatedTopics' in data:
                        for topic in data['RelatedTopics'][:5]:
                            if 'FirstURL' in topic:
                                competitor_urls.append(topic['FirstURL'])
            except:
                pass
            
            # If no competitors found, try to get related domains via reverse IP
            if not competitor_urls:
                try:
                    import socket
                    ip = socket.gethostbyname(domain)
                    competitor_urls = [
                        f"https://www.google.com/search?q=related:{url}",
                    ]
                except:
                    pass
            
            # Analyze each competitor (basic comparison)
            competitor_analysis = []
            for comp_url in competitor_urls[:3]:
                try:
                    response = requests.get(comp_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        title = soup.title.string if soup.title else 'No title'
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        desc = meta_desc.get('content') if meta_desc else 'No description'
                        
                        # Simple analysis
                        word_count = len(response.text.split())
                        competitor_analysis.append({
                            'url': comp_url,
                            'title': title[:100],
                            'description': desc[:150],
                            'word_count': word_count,
                            'has_ssl': comp_url.startswith('https')
                        })
                except:
                    continue
            
            return competitor_analysis
            

        except Exception as e:
            return {'error': str(e), 'competitors': []}

    def analyze_conversions(self, soup, url):
        """Analyze conversion optimization elements"""
        cro_analysis = {
            'cta_count': 0,
            'cta_texts': [],
            'trust_signals': [],
            'forms': 0,
            'checkout_steps': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Find all buttons and links that look like CTAs
        cta_keywords = ['buy', 'purchase', 'order', 'sign up', 'subscribe', 'download', 'get', 'start', 'try', 'add to cart', 'checkout']
        all_buttons = soup.find_all(['button', 'a'])
        for element in all_buttons:
            text = element.get_text().lower().strip()
            if any(keyword in text for keyword in cta_keywords):
                cro_analysis['cta_count'] += 1
                if len(text) < 30:
                    cro_analysis['cta_texts'].append(text[:50])
        
        # Check for trust signals
        trust_keywords = ['testimonial', 'review', 'rating', 'star', 'guarantee', 'secure', 'ssl', 'trust', 'verified', 'award', 'certified', 'money back', 'refund']
        trust_elements = soup.find_all(['span', 'div', 'section', 'img'])
        for element in trust_elements:
            text = element.get_text().lower()
            if any(keyword in text for keyword in trust_keywords):
                trust_signal = text[:100].strip()
                if len(trust_signal) > 10:
                    cro_analysis['trust_signals'].append(trust_signal[:100])
        
        # Check for forms
        forms = soup.find_all('form')
        cro_analysis['forms'] = len(forms)
        for form in forms:
            inputs = form.find_all('input')
            if len(inputs) < 3:
                cro_analysis['issues'].append('Form has too few fields (could be too simple or not capturing enough data)')
            if not (form.find('input', {'type': 'submit'}) or form.find('button', {'type': 'submit'})):
                cro_analysis['issues'].append('Form missing submit button')
        
        # Check for checkout process
        checkout_links = soup.find_all('a', href=re.compile(r'cart|checkout|basket|shop|order', re.I))
        cro_analysis['checkout_steps'] = len(checkout_links)
        
        # CRO recommendations
        if cro_analysis['cta_count'] < 3:
            cro_analysis['recommendations'].append('Add more clear calls-to-action to guide visitors through your sales funnel')
        if len(cro_analysis['trust_signals']) < 2:
            cro_analysis['recommendations'].append('Add trust signals (testimonials, reviews, guarantees) to build customer confidence')
        if cro_analysis['forms'] == 0:
            cro_analysis['recommendations'].append('Add a lead capture form to convert visitors into leads')
        if cro_analysis['checkout_steps'] == 0 and any(word in url for word in ['product', 'shop', 'store']):
            cro_analysis['recommendations'].append('Optimize your checkout process - ensure it\'s visible and easy to find')
        
        return cro_analysis

    def analyze_accessibility(self, soup):
        """Analyze website accessibility (WCAG compliance)"""
        accessibility_issues = {
            'alt_text_missing': 0,
            'heading_issues': [],
            'color_contrast_issues': [],
            'aria_issues': [],
            'keyboard_issues': [],
            'score': 100
        }
        
        # Check alt text on images
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt') or img['alt'] == '':
                accessibility_issues['alt_text_missing'] += 1
        
        # Check heading structure
        heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        heading_levels = {}
        for tag in heading_tags:
            heading_levels[tag] = len(soup.find_all(tag))
        
        # Check if h1 exists
        if heading_levels.get('h1', 0) == 0:
            accessibility_issues['heading_issues'].append('Missing h1 tag - page needs a primary heading')
        
        # Check heading order
        if heading_levels.get('h1', 0) > 0 and heading_levels.get('h2', 0) == 0:
            accessibility_issues['heading_issues'].append('h1 exists but no h2 found - consider adding subheadings')
        
        # Check for ARIA labels
        aria_elements = soup.find_all(attrs={'aria-label': True})
        if len(aria_elements) == 0:
            accessibility_issues['aria_issues'].append('No ARIA labels found - consider adding them for accessibility')
        
        # Check for link text
        links = soup.find_all('a')
        vague_links = ['click here', 'read more', 'learn more', 'more', 'here']
        for link in links:
            if link.get_text().strip().lower() in vague_links:
                accessibility_issues['aria_issues'].append('Found vague link text - consider using more descriptive text')
        
        # Calculate accessibility score
        issues_count = (
            accessibility_issues['alt_text_missing'] * 5 +
            len(accessibility_issues['heading_issues']) * 10 +
            len(accessibility_issues['aria_issues']) * 8
        )
        accessibility_issues['score'] = max(0, 100 - issues_count)
        
        return accessibility_issues


    def analyze_ux(self, url, soup):
        """Analyze user experience and technical issues"""
        ux_analysis = {
            'broken_links': [],
            'console_errors': [],
            'mobile_issues': [],
            'page_weight': 0,
            'render_blocking': [],
            'issues': []
        }
        
        # Check for broken links
        links = soup.find_all('a', href=True)
        for link in links[:20]:  # Limit to first 20 to avoid timeouts
            href = link['href']
            if href.startswith('http') and not href.startswith(url):
                try:
                    response = requests.head(href, timeout=3, allow_redirects=True)
                    if response.status_code >= 400:
                        ux_analysis['broken_links'].append({'url': href, 'status': response.status_code})
                except:
                    ux_analysis['broken_links'].append({'url': href, 'status': 'Timeout'})
        
        # Check mobile viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            ux_analysis['mobile_issues'].append('Missing viewport meta tag - site may not be mobile-friendly')
        elif 'width=device-width' not in str(viewport):
            ux_analysis['mobile_issues'].append('Viewport tag not properly configured for mobile devices')
        
        # Check CSS and JS loading
        css_files = soup.find_all('link', rel='stylesheet')
        js_files = soup.find_all('script', src=True)
        if len(css_files) > 5:
            ux_analysis['render_blocking'].append(f'Too many CSS files ({len(css_files)}) - consider consolidating')
        if len(js_files) > 5:
            ux_analysis['render_blocking'].append(f'Too many JavaScript files ({len(js_files)}) - consider consolidating')
        
        # Check for async/defer on scripts
        for script in js_files:
            if not script.get('async') and not script.get('defer'):
                ux_analysis['render_blocking'].append(f'Script {script.get("src", "")} is blocking page rendering')
        
        # Check page weight (approximate)
        if hasattr(soup, 'text'):
            ux_analysis['page_weight'] = round(len(str(soup)) / 1024, 2)
        
        return ux_analysis

    def analyze_business_logic(self, url, soup):
        """Analyze business logic vulnerabilities - workflow bypass, parameter tampering"""
        logic_issues = []
        
        # 1. Check for sensitive endpoints that could be abused
        sensitive_paths = [
            '/admin', '/dashboard', '/api', '/graphql', '/swagger',
            '/actuator', '/env', '/heapdump', '/debug', '/test',
            '/staging', '/dev', '/qa', '/backup', '/config'
        ]
        
        found_sensitive = []
        for path in sensitive_paths:
            test_url = f"{url}{path}"
            try:
                response = requests.get(test_url, timeout=3, allow_redirects=False)
                if response.status_code in [200, 301, 302, 403]:
                    found_sensitive.append({
                        'path': path,
                        'status': response.status_code,
                        'exposed': response.status_code == 200
                    })
            except:
                pass
        
        if found_sensitive:
            logic_issues.append({
                'category': 'Sensitive Endpoint Exposure',
                'severity': 'High',
                'details': found_sensitive,
                'description': 'Sensitive endpoints may be exposed. Check for admin panels, debug endpoints, or API documentation.'
            })
        
        # 2. Check for forms that might have tamperable parameters
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all('input')
            hidden_inputs = [inp for inp in inputs if inp.get('type') == 'hidden']
            
            if hidden_inputs:
                logic_issues.append({
                    'category': 'Hidden Parameter Tampering',
                    'severity': 'Medium',
                    'details': [{'name': inp.get('name'), 'value': inp.get('value', '')[:50]} for inp in hidden_inputs[:5]],
                    'description': 'Hidden form parameters found. These can be tampered with to manipulate business logic.'
                })
                break
        
        # 3. Check for exposed .git or .env files
        sensitive_files = ['/.git/config', '/.env', '/.aws/credentials', '/.ssh/id_rsa']
        for file_path in sensitive_files:
            test_url = f"{url}{file_path}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    logic_issues.append({
                        'category': 'Sensitive File Exposure',
                        'severity': 'Critical',
                        'details': [{'path': file_path, 'status': response.status_code}],
                        'description': f'Sensitive file {file_path} is exposed. This may contain credentials or configuration.'
                    })
            except:
                pass
        
        # 4. Check for IDOR indicators (sequential IDs)
        id_patterns = ['id=', 'user_id=', 'product_id=', 'order_id=', 'account=']
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            for pattern in id_patterns:
                if pattern in href:
                    logic_issues.append({
                        'category': 'Potential IDOR (Insecure Direct Object Reference)',
                        'severity': 'High',
                        'details': [{'url': href}],
                        'description': f'URL contains {pattern} - test if you can access other users\' data by changing the ID'
                    })
                    break
        
        # 5. Check for GraphQL endpoints
        graphql_endpoints = ['/graphql', '/graphiql', '/graphql/console']
        for endpoint in graphql_endpoints:
            test_url = f"{url}{endpoint}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    logic_issues.append({
                        'category': 'GraphQL Endpoint Exposed',
                        'severity': 'Medium',
                        'details': [{'endpoint': endpoint, 'status': response.status_code}],
                        'description': 'GraphQL endpoint exposed. Check for introspection queries that leak schema.'
                    })
            except:
                pass
        
        return logic_issues

    def analyze_security_misconfigurations(self, url):
        """Check for common security misconfigurations"""
        misconfigurations = []
        
        # Check common admin paths
        admin_paths = ['/admin', '/login', '/wp-admin', '/administrator', '/dashboard']
        for path in admin_paths:
            test_url = f"{url}{path}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    misconfigurations.append({
                        'category': 'Admin Panel Exposed',
                        'severity': 'High',
                        'details': [{'path': path, 'status': response.status_code}],
                        'description': f'Admin panel at {path} is accessible. Ensure strong authentication is in place.'
                    })
            except:
                pass
        
        # 2. Check for exposed debugging endpoints
        debug_endpoints = [
            '/debug', '/debug/pprof', '/_status', '/status',
            '/health', '/metrics', '/prometheus', '/actuator/health'
        ]
        for endpoint in debug_endpoints:
            test_url = f"{url}{endpoint}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    misconfigurations.append({
                        'category': 'Debug Endpoint Exposed',
                        'severity': 'Medium',
                        'details': [{'endpoint': endpoint, 'status': response.status_code}],
                        'description': f'Debug/status endpoint {endpoint} is exposed. May leak sensitive system information.'
                    })
            except:
                pass
        
        # 3. Check for exposed .git folders
        git_paths = ['/.git/config', '/.git/HEAD', '/.git/index']
        for path in git_paths:
            test_url = f"{url}{path}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    misconfigurations.append({
                        'category': 'Git Repository Exposed',
                        'severity': 'Critical',
                        'details': [{'path': path, 'status': response.status_code}],
                        'description': f'Git repository file {path} is exposed. This may leak source code and credentials.'
                    })
            except:
                pass
        
        # 4. Check for open directory listing
        test_url = f"{url}/images/"
        try:
            response = requests.get(test_url, timeout=3)
            if response.status_code == 200 and 'Index of' in response.text:
                misconfigurations.append({
                    'category': 'Directory Listing Enabled',
                    'severity': 'Medium',
                    'details': [{'path': '/images/', 'status': response.status_code}],
                    'description': 'Directory listing is enabled. This can expose sensitive files.'
                })
        except:
            pass
        
        # 5. Check for server version disclosure
        try:
            response = requests.get(url, timeout=3)
            server_header = response.headers.get('Server', '')
            if server_header:
                misconfigurations.append({
                    'category': 'Server Version Disclosure',
                    'severity': 'Low',
                    'details': [{'server': server_header}],
                    'description': f'Server version {server_header} is exposed. This helps attackers identify vulnerabilities.'
                })
            
            # Check X-Powered-By
            powered_by = response.headers.get('X-Powered-By', '')
            if powered_by:
                misconfigurations.append({
                    'category': 'Technology Stack Disclosure',
                    'severity': 'Low',
                    'details': [{'powered_by': powered_by}],
                    'description': f'Technology stack {powered_by} is exposed. This helps attackers find version-specific exploits.'
                })
        except:
            pass
        
        return misconfigurations

    def analyze_advanced_headers(self, url):
        """Analyze security headers in depth - CSP, CORS, Permissions-Policy"""
        headers_analysis = {
            'csp': {},
            'cors': {},
            'permissions_policy': {},
            'issues': []
        }
        
        try:
            response = requests.get(url, timeout=5)
            headers = response.headers
            
            # 1. Content-Security-Policy Analysis
            csp = headers.get('Content-Security-Policy', '')
            if csp:
                # Parse CSP directives
                directives = {}
                for part in csp.split(';'):
                    part = part.strip()
                    if ' ' in part:
                        key, value = part.split(' ', 1)
                        directives[key] = value
                    else:
                        directives[part] = ''
                
                headers_analysis['csp'] = {
                    'present': True,
                    'directives': directives,
                    'weaknesses': []
                }
                
                # Check for unsafe directives
                if 'script-src' in directives:
                    if "'unsafe-inline'" in directives['script-src']:
                        headers_analysis['csp']['weaknesses'].append({
                            'type': 'unsafe-inline',
                            'severity': 'High',
                            'description': 'script-src uses unsafe-inline - XSS protection is weakened'
                        })
                    if "'unsafe-eval'" in directives['script-src']:
                        headers_analysis['csp']['weaknesses'].append({
                            'type': 'unsafe-eval',
                            'severity': 'High',
                            'description': 'script-src uses unsafe-eval - XSS protection is weakened'
                        })
                    if '*' in directives['script-src']:
                        headers_analysis['csp']['weaknesses'].append({
                            'type': 'wildcard',
                            'severity': 'High',
                            'description': 'script-src uses wildcard - allows scripts from any source'
                        })
                
                if 'default-src' in directives and directives['default-src'] == '*':
                    headers_analysis['csp']['weaknesses'].append({
                        'type': 'wildcard',
                        'severity': 'High',
                        'description': 'default-src uses wildcard - allows resources from any source'
                    })
            else:
                headers_analysis['csp'] = {
                    'present': False,
                    'weaknesses': [{
                        'type': 'missing',
                        'severity': 'High',
                        'description': 'Content-Security-Policy header missing - XSS prevention is limited'
                    }]
                }
            
            # 2. CORS Analysis
            cors = headers.get('Access-Control-Allow-Origin', '')
            if cors:
                headers_analysis['cors'] = {
                    'present': True,
                    'value': cors,
                    'weaknesses': []
                }
                
                if cors == '*':
                    headers_analysis['cors']['weaknesses'].append({
                        'type': 'wildcard',
                        'severity': 'High',
                        'description': 'CORS allows all origins - sensitive data may be leaked to any website'
                    })
                elif cors.startswith('http'):
                    # Check if it's a valid origin
                    headers_analysis['cors']['weaknesses'].append({
                        'type': 'limited',
                        'severity': 'Low',
                        'description': f'CORS allows specific origin: {cors}. Ensure this is intended.'
                    })
            else:
                headers_analysis['cors'] = {
                    'present': False,
                    'weaknesses': [{
                        'type': 'missing',
                        'severity': 'Medium',
                        'description': 'CORS headers missing - API access may be restricted but also may cause issues'
                    }]
                }
            
            # 3. Permissions-Policy Analysis
            permissions_policy = headers.get('Permissions-Policy', '')
            if permissions_policy:
                # Parse permissions
                permissions = {}
                for part in permissions_policy.split(','):
                    part = part.strip()
                    if '=' in part:
                        key, value = part.split('=', 1)
                        permissions[key.strip()] = value.strip()
                    else:
                        permissions[part] = ''
                
                headers_analysis['permissions_policy'] = {
                    'present': True,
                    'permissions': permissions,
                    'weaknesses': []
                }
                
                # Check for missing important permissions
                important_permissions = ['geolocation', 'microphone', 'camera', 'payment']
                for perm in important_permissions:
                    if perm not in permissions:
                        headers_analysis['permissions_policy']['weaknesses'].append({
                            'type': 'missing',
                            'severity': 'Low',
                            'description': f'Permission {perm} not restricted - may be used without user consent'
                        })
            else:
                headers_analysis['permissions_policy'] = {
                    'present': False,
                    'weaknesses': [{
                        'type': 'missing',
                        'severity': 'Low',
                        'description': 'Permissions-Policy header missing - browser features may be abused'
                    }]
                }
            
            # 4. Check for missing important headers
            important_headers = {
                'Strict-Transport-Security': 'HSTS missing - HTTPS not enforced',
                'X-Content-Type-Options': 'X-Content-Type-Options missing - MIME sniffing possible',
                'X-Frame-Options': 'X-Frame-Options missing - clickjacking possible',
                'Referrer-Policy': 'Referrer-Policy missing - referrer leakage possible'
            }
            
            for header, issue in important_headers.items():
                if header not in headers:
                    headers_analysis['issues'].append({
                        'type': 'missing',
                        'severity': 'Medium',
                        'description': issue,
                        'header': header
                    })
            
            return headers_analysis
            
        except Exception as e:
            return {'error': str(e)}


    def analyze_exploit_chains(self, results):
        """Detect potential exploit chains by cross-referencing findings"""
        chains = []
        
        # Collect all findings with their categories and severities
        findings = results.get('recommendations', [])
        
        # 1. XSS + Missing CSP = Exploit Chain
        xss_found = False
        csp_missing = False
        
        for finding in findings:
            if 'XSS' in finding.get('description', '') or 'script' in finding.get('description', '').lower():
                xss_found = True
            if 'Content-Security-Policy' in finding.get('description', ''):
                csp_missing = True
        
        if xss_found and csp_missing:
            chains.append({
                'name': 'XSS + Missing CSP = Full Account Takeover',
                'severity': 'Critical',
                'description': 'XSS vulnerability exists and Content-Security-Policy is missing. This combination allows attackers to execute arbitrary JavaScript and steal session cookies.',
                'findings': ['XSS Vulnerability', 'Missing Content-Security-Policy'],
                'impact': 'Account takeover, data theft, session hijacking'
            })
        
        # 2. IDOR + Missing CORS = Data Exfiltration
        idor_found = False
        cors_wildcard = False
        
        for finding in findings:
            if 'IDOR' in finding.get('description', '') or 'Insecure Direct Object Reference' in finding.get('description', ''):
                idor_found = True
            if 'CORS' in finding.get('description', '') and 'allows all origins' in finding.get('description', ''):
                cors_wildcard = True
        
        if idor_found and cors_wildcard:
            chains.append({
                'name': 'IDOR + Wildcard CORS = Mass Data Exfiltration',
                'severity': 'Critical',
                'description': 'IDOR vulnerability combined with permissive CORS allows attackers to access and exfiltrate other users\' data from any website.',
                'findings': ['IDOR Vulnerability', 'Wildcard CORS Policy'],
                'impact': 'Data breach, privacy violation, regulatory non-compliance'
            })
        
        # 3. Admin Panel + Default Credentials = Full Compromise
        admin_found = False
        default_creds_found = False
        
        for finding in findings:
            if 'Admin Panel' in finding.get('description', ''):
                admin_found = True
            if 'default credentials' in finding.get('description', '').lower():
                default_creds_found = True
        
        if admin_found and default_creds_found:
            chains.append({
                'name': 'Admin Panel + Default Credentials = System Compromise',
                'severity': 'Critical',
                'description': 'Admin panel is exposed AND default credentials are suspected. Attackers can gain administrative access.',
                'findings': ['Exposed Admin Panel', 'Default Credentials'],
                'impact': 'Full system compromise, data breach, ransomware'
            })
        
        # 4. SQL Injection + Debug Endpoint = Database Access
        sql_found = False
        debug_found = False
        
        for finding in findings:
            if 'SQL' in finding.get('description', ''):
                sql_found = True
            if 'debug' in finding.get('description', '').lower() or 'status' in finding.get('description', '').lower():
                debug_found = True
        
        if sql_found and debug_found:
            chains.append({
                'name': 'SQL Injection + Debug Endpoint = Database Access',
                'severity': 'Critical',
                'description': 'SQL injection vulnerability combined with exposed debug endpoints allows attackers to enumerate the database schema and extract data.',
                'findings': ['SQL Injection', 'Exposed Debug Endpoint'],
                'impact': 'Data breach, database compromise, data loss'
            })
        
        # 5. Git Exposure + Server Info = Credential Leak
        git_found = False
        server_info_found = False
        
        for finding in findings:
            if '.git' in finding.get('description', '') or 'repository' in finding.get('description', '').lower():
                git_found = True
            if 'Server version' in finding.get('description', '') or 'Technology stack' in finding.get('description', ''):
                server_info_found = True
        
        if git_found and server_info_found:
            chains.append({
                'name': 'Git Exposure + Server Info = Source Code + Credentials',
                'severity': 'Critical',
                'description': 'Git repository exposed AND server/tech stack disclosed. Attackers can download source code and identify specific vulnerabilities.',
                'findings': ['Git Repository Exposed', 'Server Version Disclosure'],
                'impact': 'Source code theft, credential exposure, targeted attacks'
            })
        
        # 6. Missing Security Headers Chain
        missing_headers = []
        for finding in findings:
            if 'header missing' in finding.get('description', '').lower():
                missing_headers.append(finding.get('description', ''))
        
        if len(missing_headers) >= 3:
            chains.append({
                'name': 'Multiple Missing Security Headers = Defense-in-Depth Failure',
                'severity': 'High',
                'description': f'{len(missing_headers)} security headers are missing. This significantly reduces the security posture of the application.',
                'findings': missing_headers[:5],
                'impact': 'Increased attack surface, multiple vulnerabilities possible'
            })
        
        return chains


    def analyze_cloud_misconfigurations(self, url):
        """Check for cloud-related misconfigurations"""
        cloud_issues = []
        
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            # 1. Check for public S3 buckets
            s3_patterns = [
                f'{domain}.s3.amazonaws.com',
                f's3.amazonaws.com/{domain}',
                f'{domain}.s3-website.amazonaws.com'
            ]
            
            for pattern in s3_patterns:
                try:
                    test_url = f'https://{pattern}'
                    response = requests.get(test_url, timeout=3)
                    if response.status_code == 200:
                        # Check if it's actually an S3 bucket
                        if 'ListBucketResult' in response.text or 'NoSuchBucket' not in response.text:
                            cloud_issues.append({
                                'category': 'Public S3 Bucket',
                                'severity': 'Critical',
                                'details': [{'bucket': pattern, 'status': response.status_code}],
                                'description': f'S3 bucket {pattern} is publicly accessible. May contain sensitive data.'
                            })
                except:
                    pass
            
            # 2. Check for exposed AWS metadata
            metadata_endpoints = [
                'http://169.254.169.254/latest/meta-data/',
                'http://169.254.169.254/latest/user-data/',
                'http://169.254.169.254/latest/dynamic/instance-identity/document'
            ]
            
            for endpoint in metadata_endpoints:
                try:
                    response = requests.get(endpoint, timeout=2)
                    if response.status_code == 200:
                        cloud_issues.append({
                            'category': 'AWS Metadata Exposure',
                            'severity': 'Critical',
                            'details': [{'endpoint': endpoint, 'status': response.status_code}],
                            'description': 'AWS metadata endpoint is accessible. This can expose instance credentials and IAM roles.'
                        })
                except:
                    pass
            
            # 3. Check for exposed .aws/credentials
            cred_paths = ['/.aws/credentials', '/.aws/config']
            for path in cred_paths:
                test_url = f"{url}{path}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if response.status_code == 200:
                        cloud_issues.append({
                            'category': 'AWS Credentials Exposed',
                            'severity': 'Critical',
                            'details': [{'path': path, 'status': response.status_code}],
                            'description': f'AWS credentials file {path} is exposed. This can lead to account compromise.'
                        })
                except:
                    pass
            
            # 4. Check for Kubernetes secrets exposure
            k8s_paths = [
                '/.kube/config',
                '/var/run/secrets/kubernetes.io/serviceaccount/token',
                '/api/v1/namespaces/default/secrets'
            ]
            for path in k8s_paths:
                test_url = f"{url}{path}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if response.status_code == 200:
                        cloud_issues.append({
                            'category': 'Kubernetes Secrets Exposure',
                            'severity': 'Critical',
                            'details': [{'path': path, 'status': response.status_code}],
                            'description': f'Kubernetes secrets at {path} are exposed. This can lead to cluster compromise.'
                        })
                except:
                    pass
            
            # 5. Check for exposed Docker API
            docker_endpoints = [
                '/v1.40/version',
                '/v1.40/containers/json',
                '/v1.40/images/json'
            ]
            for endpoint in docker_endpoints:
                test_url = f"{url}{endpoint}"
                try:
                    response = requests.get(test_url, timeout=2)
                    if response.status_code == 200:
                        cloud_issues.append({
                            'category': 'Docker API Exposure',
                            'severity': 'Critical',
                            'details': [{'endpoint': endpoint, 'status': response.status_code}],
                            'description': f'Docker API endpoint {endpoint} is exposed. This can allow container manipulation.'
                        })
                except:
                    pass
            
            # 6. Check for exposed .env files with cloud credentials
            env_paths = ['/.env', '/.env.production', '/.env.local']
            for path in env_paths:
                test_url = f"{url}{path}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if response.status_code == 200:
                        # Check for cloud credentials in response
                        content = response.text
                        if 'AWS' in content or 'SECRET' in content or 'KEY' in content or 'TOKEN' in content:
                            cloud_issues.append({
                                'category': 'Cloud Credentials in .env',
                                'severity': 'Critical',
                                'details': [{'path': path, 'status': response.status_code}],
                                'description': f'.env file {path} contains cloud credentials. This is a critical security risk.'
                            })
                except:
                    pass
            
            return cloud_issues
            
        except Exception as e:
            return {'error': str(e)}


    # ============================================
    # BUG BOUNTY RECON METHODS
    # ============================================

    def discover_subdomains(self, domain):
        """Discover subdomains using multiple sources"""
        subdomains = set()
        
        # 1. Using subfinder
        try:
            result = subprocess.run(
                ['subfinder', '-d', domain, '-silent'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.stdout:
                for line in result.stdout.splitlines():
                    subdomains.add(line.strip())
        except Exception as e:
            print(f"Subfinder error: {e}")
        
        # 2. Using crt.sh (Certificate Transparency)
        try:
            import requests
            response = requests.get(
                f"https://crt.sh/?q=%25.{domain}&output=json",
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry.get('name_value', '')
                    if name and name.endswith(domain):
                        subdomains.add(name.strip())
        except Exception as e:
            print(f"crt.sh error: {e}")
        
        # 3. Using DNS brute force (common subdomains)
        common_subdomains = ['www', 'mail', 'ftp', 'admin', 'dev', 'test', 'api', 'app', 'blog', 'shop', 'support']
        for sub in common_subdomains:
            test_domain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(test_domain)
                subdomains.add(test_domain)
            except:
                pass
        
        return list(subdomains)

    def discover_urls(self, domain):
        """Discover historical URLs from Wayback Machine"""
        urls = set()
        
        try:
            import requests
            response = requests.get(
                f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey",
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                for entry in data[1:]:  # Skip header
                    if isinstance(entry, list) and entry:
                        urls.add(entry[0])
        except Exception as e:
            print(f"Wayback error: {e}")
        
        # Also try gau (if installed)
        try:
            result = subprocess.run(
                ['gau', domain],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                for line in result.stdout.splitlines():
                    urls.add(line.strip())
        except:
            pass
        
        return list(urls)[:500]  # Limit to 500 URLs

    def scan_ports(self, domain):
        """Scan for open ports using nmap"""
        open_ports = []
        
        try:
            nm = nmap.PortScanner()
            nm.scan(domain, arguments='-sS -T4 -p 21,22,23,25,53,80,110,143,443,993,995,3306,3389,5432,5900,8080,8443,27017')
            
            if domain in nm.all_hosts():
                for proto in nm[domain].all_protocols():
                    ports = nm[domain][proto].keys()
                    for port in ports:
                        state = nm[domain][proto][port]['state']
                        service = nm[domain][proto][port]['name']
                        if state == 'open':
                            open_ports.append({
                                'port': port,
                                'protocol': proto,
                                'service': service,
                                'state': state
                            })
        except Exception as e:
            print(f"Nmap error: {e}")
        
        return open_ports

    def detect_technologies(self, url):
        """Detect technologies used by the website using Wappalyzer-style logic"""
        technologies = {
            'server': [],
            'frameworks': [],
            'javascript_libraries': [],
            'cms': [],
            'cloud': [],
            'analytics': []
        }
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            headers = response.headers
            content = response.text.lower()
            
            # Server
            if 'Server' in headers:
                technologies['server'].append(headers['Server'])
            
            # CMS Detection
            if 'wp-content' in content or 'wp-includes' in content:
                technologies['cms'].append('WordPress')
            if 'drupal' in content:
                technologies['cms'].append('Drupal')
            if 'joomla' in content:
                technologies['cms'].append('Joomla')
            
            # JavaScript Libraries
            if 'jquery' in content:
                technologies['javascript_libraries'].append('jQuery')
            if 'react' in content and 'react-dom' in content:
                technologies['javascript_libraries'].append('React')
            if 'angular' in content:
                technologies['javascript_libraries'].append('Angular')
            if 'vue' in content:
                technologies['javascript_libraries'].append('Vue.js')
            
            # Cloud Services
            if 'cloudflare' in headers.get('Server', '').lower() or 'cloudflare' in headers.get('Cf-Ray', '').lower():
                technologies['cloud'].append('Cloudflare')
            if 'aws' in headers.get('X-Amz-Id-2', '').lower():
                technologies['cloud'].append('AWS')
            if 'azure' in headers.get('X-Powered-By', '').lower():
                technologies['cloud'].append('Azure')
            
            # Analytics
            if 'google-analytics' in content or 'ga(' in content:
                technologies['analytics'].append('Google Analytics')
            if 'gtag' in content:
                technologies['analytics'].append('Google Tag Manager')
            if 'facebook-pixel' in content or 'fbq(' in content:
                technologies['analytics'].append('Facebook Pixel')
            
        except Exception as e:
            print(f"Tech detection error: {e}")
        
        return technologies

    def perform_recon(self, domain):
        """Complete recon workflow"""
        recon_results = {
            'domain': domain,
            'subdomains': [],
            'urls': [],
            'open_ports': [],
            'technologies': {},
            'summary': {}
        }
        
        print(f"🔍 Starting reconnaissance for {domain}...")
        
        # 1. Discover subdomains
        print("📡 Discovering subdomains...")
        subdomains = self.discover_subdomains(domain)
        recon_results['subdomains'] = subdomains
        recon_results['summary']['subdomains_found'] = len(subdomains)
        
        # 2. Discover URLs
        print("🌐 Discovering URLs from Wayback...")
        urls = self.discover_urls(domain)
        recon_results['urls'] = urls
        recon_results['summary']['urls_found'] = len(urls)
        
        # 3. Scan ports on main domain
        print("🔌 Scanning open ports...")
        ports = self.scan_ports(domain)
        recon_results['open_ports'] = ports
        recon_results['summary']['open_ports'] = len(ports)
        
        # 4. Detect technologies
        print("⚙️ Detecting technologies...")
        tech = self.detect_technologies(f"https://{domain}")
        recon_results['technologies'] = tech
        
        print("✅ Recon complete!")
        return recon_results

    def save_report_automatically(self, results):
        """Auto-save report to file without manual download"""
        try:
            import os
            import json
            from datetime import datetime
            
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Ensure all required keys exist in results
            if 'scores' not in results:
                results['scores'] = {'seo': 0, 'security': 0, 'performance': 0, 'overall': 0}
            else:
                # Ensure each individual score exists
                if 'seo' not in results['scores']:
                    results['scores']['seo'] = 0
                if 'security' not in results['scores']:
                    results['scores']['security'] = 0
                if 'performance' not in results['scores']:
                    results['scores']['performance'] = 0
                if 'overall' not in results['scores']:
                    results['scores']['overall'] = 0
            
            # Generate both reports
            html_report = generate_html_report(results)
            business_report = generate_business_report(results)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = results.get('url', 'unknown').replace('https://', '').replace('http://', '').replace('/', '_')
            
            # Save technical report
            tech_filename = f"{reports_dir}/technical_report_{domain}_{timestamp}.html"
            with open(tech_filename, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            # Save business report
            biz_filename = f"{reports_dir}/business_report_{domain}_{timestamp}.html"
            with open(biz_filename, 'w', encoding='utf-8') as f:
                f.write(business_report)
            
            # Save summary to JSON
            json_filename = f"{reports_dir}/summary_{domain}_{timestamp}.json"
            results_copy = results.copy()
            if 'timestamp' in results_copy:
                results_copy['timestamp'] = str(results_copy['timestamp'])
            # Ensure scores are JSON serializable
            if 'scores' in results_copy:
                results_copy['scores'] = {k: float(v) for k, v in results_copy['scores'].items()}
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(results_copy, f, indent=2, default=str)
            
            print(f"✅ Reports saved to {reports_dir}/")
            print(f"   - Technical: {tech_filename}")
            print(f"   - Business: {biz_filename}")
            print(f"   - JSON: {json_filename}")
            
        except Exception as e:
            print(f"❌ Error saving reports: {e}")

    def calculate_business_impact(self, results):
        """Calculate estimated business impact of issues"""
        impact = {
            'traffic_loss': 0,
            'conversion_loss': 0,
            'revenue_loss': 0,
            'risk_level': 'Low',
            'opportunities': []
        }
        
        # Estimate traffic loss from SEO issues
        seo_score = results.get('scores', {}).get('seo', 50)
        if seo_score < 80:
            impact['traffic_loss'] = round((80 - seo_score) * 10)
            impact['opportunities'].append(f'Improve SEO to gain approximately {impact["traffic_loss"]} more visitors/month')
        
        # Estimate conversion loss from CRO issues
        cro_analysis = results.get('cro_analysis', {})
        if cro_analysis:
            if cro_analysis.get('cta_count', 0) < 3:
                impact['conversion_loss'] += 15
            if len(cro_analysis.get('trust_signals', [])) < 2:
                impact['conversion_loss'] += 20
            if impact['conversion_loss'] > 0:
                impact['opportunities'].append(f'Improve conversions to increase sales by up to {impact["conversion_loss"]}%')
        
        # Estimate revenue loss (simplified)
        if impact['traffic_loss'] > 0 or impact['conversion_loss'] > 0:
            estimated_visitors = 1000
            conversion_rate = 0.02
            avg_order_value = 50
            current_revenue = estimated_visitors * conversion_rate * avg_order_value
            
            new_visitors = estimated_visitors + impact['traffic_loss']
            new_conversion_rate = conversion_rate * (1 + impact['conversion_loss'] / 100)
            potential_revenue = new_visitors * new_conversion_rate * avg_order_value
            
            impact['revenue_loss'] = round(potential_revenue - current_revenue, 2)
            if impact['revenue_loss'] > 0:
                impact['opportunities'].append(f'Potential revenue increase: ${impact["revenue_loss"]}/month')
        
        # Determine risk level
        security_score = results.get('scores', {}).get('security', 50)
        if security_score < 70:
            impact['risk_level'] = 'High'
        elif security_score < 85:
            impact['risk_level'] = 'Medium'
        else:
            impact['risk_level'] = 'Low'
        
        return impact

    def check_ssl_certificate(self, url):
        """Check SSL certificate details and validity"""
        try:
            # Extract domain
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse certificate details
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (expiry_date - datetime.now()).days
                    
                    return {
                        'issued_to': cert.get('subject', [])[0][0][1] if cert.get('subject') else 'Unknown',
                        'issued_by': cert.get('issuer', [])[0][0][1] if cert.get('issuer') else 'Unknown',
                        'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                        'days_remaining': days_remaining,
                        'is_valid': days_remaining > 0,
                        'expired': days_remaining <= 0,
                        'expiring_soon': days_remaining < 30
                    }
        except Exception as e:
            return {'error': str(e), 'is_valid': False, 'has_ssl': False}

    def check_security_headers(self, url):
        """Check for complete security headers"""
        try:
            response = requests.get(url, timeout=5)
            headers = response.headers
            
            security_headers = {
                'X-Frame-Options': headers.get('X-Frame-Options', 'Missing'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Missing'),
                'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Missing'),
                'Content-Security-Policy': headers.get('Content-Security-Policy', 'Missing'),
                'X-XSS-Protection': headers.get('X-XSS-Protection', 'Missing'),
                'Referrer-Policy': headers.get('Referrer-Policy', 'Missing'),
                'Permissions-Policy': headers.get('Permissions-Policy', 'Missing'),
            }
            
            return security_headers
        except Exception as e:
            return {'error': str(e)}


    def check_email_security(self, url):
        """Check email security - SPF, DKIM, DMARC"""
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            email_security = {}
            
            # Check SPF
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                spf_records = [str(r) for r in answers if 'v=spf1' in str(r)]
                email_security['SPF'] = 'Found' if spf_records else 'Missing'
            except:
                email_security['SPF'] = 'Missing'
            
            # Check DMARC
            try:
                dmarc_domain = f'_dmarc.{domain}'
                answers = dns.resolver.resolve(dmarc_domain, 'TXT')
                dmarc_records = [str(r) for r in answers if 'v=DMARC1' in str(r)]
                email_security['DMARC'] = 'Found' if dmarc_records else 'Missing'
            except:
                email_security['DMARC'] = 'Missing'
            
            # Check DKIM (simplified)
            try:
                dkim_domain = f'default._domainkey.{domain}'
                answers = dns.resolver.resolve(dkim_domain, 'TXT')
                email_security['DKIM'] = 'Found' if answers else 'Missing'
            except:
                email_security['DKIM'] = 'Missing'
            
            return email_security
        except Exception as e:
            return {'error': str(e)}


    def test_sql_injection(self, url):
        """Test for SQL injection vulnerabilities (safe test only)"""
        try:
            from urllib.parse import urlparse, parse_qs
            
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # If there are query parameters, test with safe payload
            if query_params:
                vulnerable = False
                details = []
                
                # Add a safe test parameter
                test_url = f"{url}?test=1' OR '1'='1"
                try:
                    response = requests.get(test_url, timeout=3)
                    if "SQL" in response.text or "error" in response.text.lower():
                        vulnerable = True
                        details.append('Potential SQL injection vulnerability detected')
                except:
                    pass
                
                return {'vulnerable': vulnerable, 'details': details}
            else:
                return {'vulnerable': False, 'details': ['No query parameters to test']}
        except Exception as e:
            return {'vulnerable': False, 'details': [str(e)]}


    def test_xss(self, url):
        """Test for XSS vulnerabilities (safe test only)"""
        try:
            # Add a safe test parameter
            test_url = f"{url}?test=<script>alert('test')</script>"
            try:
                response = requests.get(test_url, timeout=3)
                if "<script>" in response.text and "alert" in response.text:
                    return {'vulnerable': True, 'details': ['Potential XSS vulnerability detected']}
            except:
                pass
            
            return {'vulnerable': False, 'details': ['No XSS vulnerabilities detected']}
        except Exception as e:
            return {'vulnerable': False, 'details': [str(e)]}


    def check_malware(self, url):
        """Check for known malware indicators"""
        try:
            response = requests.get(url, timeout=5)
            text = response.text.lower()
            
            malware_indicators = [
                'malware', 'virus', 'trojan', 'ransomware',
                'phishing', 'spam', 'hacked', 'compromised'
            ]
            
            detected = []
            for indicator in malware_indicators:
                if indicator in text:
                    detected.append(indicator)
            
            if detected:
                return {'status': 'Suspicious', 'details': detected}
            else:
                return {'status': 'Clean', 'details': ['No malware signatures detected']}
        except Exception as e:
            return {'status': 'Unknown', 'details': [str(e)]}


    def check_blacklists(self, url):
        """Check if site is on security blacklists"""
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            # Check against a few common blacklists (DNS-based)
            blacklists = [
                f'{domain}.dbl.spamhaus.org',
                f'{domain}.surbl.org',
            ]
            
            blacklisted = []
            for bl in blacklists:
                try:
                    dns.resolver.resolve(bl, 'A')
                    blacklisted.append(bl)
                except:
                    pass
            
            if blacklisted:
                return {'status': 'Blacklisted', 'details': blacklisted}
            else:
                return {'status': 'Clean', 'details': ['Not found on blacklists']}
        except Exception as e:
            return {'status': 'Unknown', 'details': [str(e)]}

    def check_open_ports(self, url):
        """Check for common open ports"""
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 27017]
            open_ports = []
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((domain, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass
            
            return open_ports
        except Exception as e:
            return []

    def scan_sensitive_files(self, url):
        """Broader sensitive file / config exposure scan (concurrent, read-only GET requests)"""
        wordlist = [
            '/.git/config', '/.git/HEAD', '/.gitignore',
            '/.env', '/.env.local', '/.env.production', '/.env.backup',
            '/.aws/credentials', '/.ssh/id_rsa', '/.ssh/id_rsa.pub',
            '/.htpasswd', '/.htaccess', '/.DS_Store',
            '/wp-config.php', '/wp-config.php.bak', '/wp-config.php.old',
            '/config.php.bak', '/config.yml', '/settings.py',
            '/docker-compose.yml', '/Dockerfile', '/.dockerenv',
            '/composer.json', '/composer.lock', '/package.json', '/package-lock.json',
            '/web.config', '/appsettings.json', '/appsettings.Development.json',
            '/backup.zip', '/backup.sql', '/backup.tar.gz', '/db.sql', '/dump.sql',
            '/.vscode/sftp.json', '/.idea/workspace.xml',
            '/server-status', '/server-info',
            '/.well-known/security.txt', '/phpinfo.php', '/info.php',
            '/.circleci/config.yml', '/.travis.yml', '/.github/workflows',
            '/credentials.json', '/secrets.yml', '/id_rsa'
        ]

        found = []

        def check(path):
            test_url = f"{url}{path}"
            try:
                resp = requests.get(test_url, timeout=3, allow_redirects=False)
                if resp.status_code == 200 and len(resp.content) > 0:
                    # crude false-positive filter: skip if response looks like a generic HTML 200 page (SPA catch-all)
                    is_probably_real = not (b'<html' in resp.content[:200].lower() and path not in ['/.well-known/security.txt'])
                    return {
                        'path': path,
                        'status': resp.status_code,
                        'size_bytes': len(resp.content),
                        'likely_real': is_probably_real
                    }
            except:
                pass
            return None

        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(check, path): path for path in wordlist}
                for future in as_completed(futures, timeout=30):
                    result = future.result()
                    if result:
                        found.append(result)
        except Exception as e:
            pass

        return found

    def scan_js_secrets(self, url, soup, max_files=15):
        """Fetch linked JS files and regex-scan them for likely leaked API keys/tokens (read-only)"""
        secret_patterns = {
            'AWS Access Key': r'AKIA[0-9A-Z]{16}',
            'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
            'Generic Bearer Token': r'bearer\s+[a-zA-Z0-9_\-\.=]{20,}',
            'Slack Token': r'xox[baprs]-[0-9A-Za-z\-]{10,}',
            'Stripe Live Key': r'sk_live_[0-9a-zA-Z]{24,}',
            'Firebase URL': r'[a-z0-9-]+\.firebaseio\.com',
            'Private Key Header': r'-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----',
            'Generic Secret Assignment': r'(?i)(api[_-]?key|secret|token|password)["\']?\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']'
        }

        findings = []
        try:
            scripts = soup.find_all('script', src=True)
            js_urls = []
            for s in scripts[:max_files]:
                src = s.get('src')
                if src:
                    js_urls.append(urljoin(url, src))

            for js_url in js_urls:
                try:
                    resp = requests.get(js_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if resp.status_code == 200:
                        content = resp.text
                        for label, pattern in secret_patterns.items():
                            for match in re.finditer(pattern, content):
                                snippet = match.group(0)
                                # redact most of the matched value before reporting
                                redacted = snippet[:6] + '…redacted…' if len(snippet) > 10 else '…redacted…'
                                findings.append({
                                    'file': js_url,
                                    'type': label,
                                    'preview': redacted
                                })
                except:
                    continue
        except Exception as e:
            pass

        return findings[:50]

    def lookup_cves(self, technologies, max_lookups=5):
        """Look up known CVEs for detected technologies via the NVD public API (best-effort, rate-limited)"""
        cve_matches = []
        seen = set()
        techs_flat = []
        for category, items in (technologies or {}).items():
            for item in items:
                # strip version-looking noise, keep short product names
                name = item.split('/')[0].strip()
                if name and name.lower() not in seen and len(name) > 2:
                    seen.add(name.lower())
                    techs_flat.append(name)

        for tech in techs_flat[:max_lookups]:
            try:
                resp = requests.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={'keywordSearch': tech, 'resultsPerPage': 3},
                    timeout=8
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for vuln in data.get('vulnerabilities', [])[:3]:
                        cve = vuln.get('cve', {})
                        cve_id = cve.get('id', 'Unknown')
                        descriptions = cve.get('descriptions', [])
                        desc_text = next((d['value'] for d in descriptions if d.get('lang') == 'en'), '')
                        metrics = cve.get('metrics', {})
                        score = None
                        for key in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                            if key in metrics and metrics[key]:
                                score = metrics[key][0].get('cvssData', {}).get('baseScore')
                                break
                        cve_matches.append({
                            'technology': tech,
                            'cve_id': cve_id,
                            'description': desc_text[:250],
                            'cvss_score': score
                        })
                time.sleep(1.5)  # be polite to the public NVD rate limit
            except Exception:
                continue

        return cve_matches

    def test_open_redirect(self, url):
        """Passively test common redirect parameters for open-redirect behavior (safe external test domain)"""
        redirect_params = ['redirect', 'url', 'next', 'dest', 'destination', 'return', 'return_url', 'redirect_uri', 'continue']
        payload_domain = "example.com"
        findings = []

        for param in redirect_params:
            test_url = f"{url}{'&' if '?' in url else '?'}{param}=https://{payload_domain}"
            try:
                resp = requests.get(test_url, timeout=4, allow_redirects=False)
                location = resp.headers.get('Location', '')
                if resp.status_code in (301, 302, 303, 307, 308) and payload_domain in location:
                    findings.append({'parameter': param, 'redirects_to': location, 'status': resp.status_code})
            except:
                continue

        return findings

    def check_ssrf_indicators(self, soup, url):
        """Passively flag parameters/forms that look like SSRF attack surface (does not attempt exploitation)"""
        ssrf_keywords = ['url', 'uri', 'path', 'dest', 'redirect', 'callback', 'webhook', 'fetch', 'proxy', 'src', 'target', 'host', 'file', 'load', 'import']
        indicators = []

        for form in soup.find_all('form'):
            for inp in form.find_all('input'):
                name = (inp.get('name') or '').lower()
                if any(k in name for k in ssrf_keywords):
                    indicators.append({
                        'surface': 'form input',
                        'name': inp.get('name'),
                        'form_action': form.get('action', '')
                    })

        for link in soup.find_all('a', href=True):
            href = link['href']
            for k in ssrf_keywords:
                if f'{k}=' in href.lower():
                    indicators.append({'surface': 'URL parameter', 'name': k, 'example_url': href[:150]})
                    break

        # dedupe
        seen = set()
        unique = []
        for i in indicators:
            key = json.dumps(i, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique.append(i)

        return unique[:25]

    def analyze_jwt(self, url):
        """Look for JWTs in cookies/response and flag common weaknesses (alg=none, missing exp, weak claims)"""
        import base64

        def decode_segment(seg):
            seg += '=' * (-len(seg) % 4)
            try:
                return json.loads(base64.urlsafe_b64decode(seg))
            except Exception:
                return None

        findings = []
        try:
            resp = requests.get(url, timeout=5)
            jwt_pattern = re.compile(r'eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+')

            candidates = set()
            for cookie_val in resp.cookies.values():
                candidates.update(jwt_pattern.findall(str(cookie_val)))
            candidates.update(jwt_pattern.findall(resp.text[:20000]))

            for token in list(candidates)[:5]:
                parts = token.split('.')
                if len(parts) != 3:
                    continue
                header = decode_segment(parts[0])
                payload = decode_segment(parts[1])
                issues = []
                if header:
                    alg = str(header.get('alg', '')).lower()
                    if alg == 'none':
                        issues.append('alg=none accepted — signature bypass risk')
                    if alg.startswith('hs') :
                        issues.append('HMAC alg in use — check for algorithm confusion / weak shared secret')
                if payload:
                    if 'exp' not in payload:
                        issues.append('No expiration (exp) claim — token may never expire')
                    if payload.get('exp') and payload['exp'] < time.time():
                        issues.append('Token appears expired but was still accepted/present')
                findings.append({
                    'token_preview': token[:20] + '...',
                    'header': header,
                    'payload_keys': list(payload.keys()) if payload else [],
                    'issues': issues
                })
        except Exception:
            pass

        return findings

    def estimate_cvss(self, severity):
        """Rough CVSS v3 base-score band + vector hint for a qualitative severity label (indicative only)"""
        mapping = {
            'Critical': {'range': '9.0–10.0', 'vector_hint': 'AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (example)'},
            'High': {'range': '7.0–8.9', 'vector_hint': 'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (example)'},
            'Medium': {'range': '4.0–6.9', 'vector_hint': 'AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (example)'},
            'Low': {'range': '0.1–3.9', 'vector_hint': 'AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:L/A:N (example)'}
        }
        return mapping.get(severity, {'range': 'Unknown', 'vector_hint': ''})

    def analyze_advanced_security(self, url):
        """Advanced security analysis - SSL, malware, headers, vulnerabilities"""
        security_results = {
            'ssl_certificate': {},
            'malware_check': {'status': 'Clean', 'details': []},
            'blacklist_check': {'status': 'Clean', 'details': []},
            'sql_injection': {'vulnerable': False, 'details': []},
            'xss': {'vulnerable': False, 'details': []},
            'security_headers': {},
            'email_security': {},
            'open_ports': [],
            'sensitive_files': [],
            'open_redirect': [],
            'ssrf_indicators': [],
            'jwt_analysis': [],
            'critical_issues': [],
            'warnings': []
        }
        
        try:
            # 1. SSL/TLS Certificate Analysis
            security_results['ssl_certificate'] = self.check_ssl_certificate(url)
            
            # 2. Security Headers
            security_results['security_headers'] = self.check_security_headers(url)
            
            # 3. Email Security (SPF, DKIM, DMARC)
            security_results['email_security'] = self.check_email_security(url)
            
            # 4. SQL Injection Test
            security_results['sql_injection'] = self.test_sql_injection(url)
            
            # 5. XSS Test
            security_results['xss'] = self.test_xss(url)
            
            # 6. Malware Check
            security_results['malware_check'] = self.check_malware(url)
            
            # 7. Blacklist Check
            security_results['blacklist_check'] = self.check_blacklists(url)
            
            # 8. Open Ports
            security_results['open_ports'] = self.check_open_ports(url)

            # 9. Expanded sensitive file exposure scan
            security_results['sensitive_files'] = self.scan_sensitive_files(url)

            # 10. Open redirect check
            security_results['open_redirect'] = self.test_open_redirect(url)

            # 11. JWT analysis
            security_results['jwt_analysis'] = self.analyze_jwt(url)
            
            # Generate security issues
            critical, warnings = self.generate_security_issues(security_results)
            security_results['critical_issues'] = critical
            security_results['warnings'] = warnings
            
        except Exception as e:
            security_results['error'] = str(e)
        
        return security_results


    def generate_security_issues(self, security_results):
        """Generate security issues and warnings"""
        critical = []
        warnings = []
        
        # SSL issues
        ssl = security_results.get('ssl_certificate', {})
        if not ssl.get('has_ssl', True):
            critical.append('No SSL certificate - site is not encrypted')
        elif ssl.get('expired', False):
            critical.append('SSL certificate has expired - site is not secure')
        elif ssl.get('expiring_soon', False):
            warnings.append(f'SSL certificate expires in {ssl.get("days_remaining", 0)} days')
        
        # Security headers
        headers = security_results.get('security_headers', {})
        if headers:
            if headers.get('X-Frame-Options') == 'Missing':
                warnings.append('X-Frame-Options header missing - site is vulnerable to clickjacking')
            if headers.get('X-Content-Type-Options') == 'Missing':
                warnings.append('X-Content-Type-Options header missing - MIME type sniffing possible')
            if headers.get('Content-Security-Policy') == 'Missing':
                warnings.append('Content-Security-Policy header missing - XSS prevention limited')
            if headers.get('Strict-Transport-Security') == 'Missing':
                warnings.append('HSTS header missing - no enforcement of HTTPS')
        
        # Email security
        email = security_results.get('email_security', {})
        if email:
            if email.get('SPF') == 'Missing':
                warnings.append('SPF record missing - email spoofing possible')
            if email.get('DMARC') == 'Missing':
                warnings.append('DMARC record missing - email security incomplete')
            if email.get('DKIM') == 'Missing':
                warnings.append('DKIM record missing - email authentication weak')
        
        # Vulnerabilities
        if security_results.get('sql_injection', {}).get('vulnerable', False):
            critical.append('SQL injection vulnerability detected - database at risk')
        if security_results.get('xss', {}).get('vulnerable', False):
            critical.append('XSS vulnerability detected - user data at risk')
        
        # Malware
        if security_results.get('malware_check', {}).get('status') == 'Suspicious':
            critical.append('Potential malware detected on site')
        
        # Blacklist
        if security_results.get('blacklist_check', {}).get('status') == 'Blacklisted':
            critical.append('Site is on security blacklist - reputation at risk')
        
        # Open ports
        open_ports = security_results.get('open_ports', [])
        dangerous_ports = [21, 22, 23, 3306, 3389, 5432]
        dangerous_found = [p for p in open_ports if p in dangerous_ports]
        if dangerous_found:
            critical.append(f'Dangerous open ports detected: {dangerous_found} - server at risk')

        # Sensitive files
        sensitive_files = security_results.get('sensitive_files', [])
        real_files = [f for f in sensitive_files if f.get('likely_real', True)]
        if real_files:
            critical.append(f'{len(real_files)} sensitive file(s)/path(s) appear exposed - possible credential or source leak')

        # Open redirect
        if security_results.get('open_redirect'):
            warnings.append(f'{len(security_results["open_redirect"])} parameter(s) show open-redirect behavior')

        # JWT issues
        jwt_findings = security_results.get('jwt_analysis', [])
        for jf in jwt_findings:
            if jf.get('issues'):
                for issue in jf['issues']:
                    if 'none' in issue.lower():
                        critical.append(f'JWT weakness: {issue}')
                    else:
                        warnings.append(f'JWT weakness: {issue}')
        
        return critical, warnings

    def analyze_website(self, url):
        """Main analysis function with enhanced features"""
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'seo_analysis': {},
            'security_analysis': {},
            'performance_analysis': {},
            'accessibility_analysis': {},
            'ux_analysis': {},
            'cro_analysis': {},
            'competitor_analysis': {},
            'business_impact': {},
            'business_logic': [],
            'misconfigurations': [],
            'advanced_headers': {},
            'cloud_issues': [],
            'exploit_chains': [],
            'js_secrets': [],
            'ssrf_indicators': [],
            'cve_matches': [],
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
            # Extract base domain for recon (remove www.)
            if base_domain.startswith('www.'):
                recon_domain = base_domain[4:]
            else:
                recon_domain = base_domain
            seo['internal_links'] = sum(1 for link in links if base_domain in link['href'])
            seo['external_links'] = sum(1 for link in links if 'http' in link['href'] and base_domain not in link['href'])
            
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            seo['mobile_friendly'] = bool(viewport)
            
            results['seo_analysis'] = seo
            
            # Security Analysis
            security = {}
            security['has_ssl'] = url.startswith('https')
            
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security']
            for header in security_headers:
                security[header] = response.headers.get(header) is not None
            
            results['security_analysis'] = security
            
            # Performance Analysis
            performance = {}
            start_time = time.time()
            requests.get(url, timeout=5)
            load_time = time.time() - start_time
            performance['load_time'] = round(load_time, 2)
            
            performance['page_size_kb'] = round(len(response.content) / 1024, 2)
            performance['compression'] = response.headers.get('Content-Encoding') is not None
            
            results['performance_analysis'] = performance
            
            # NEW: Accessibility Analysis
            results['accessibility_analysis'] = self.analyze_accessibility(soup)
            
            # NEW: UX Analysis
            results['ux_analysis'] = self.analyze_ux(url, soup)
            
            # NEW: CRO Analysis
            results['cro_analysis'] = self.analyze_conversions(soup, url)

            # NEW: Advanced Security Analysis
            results['advanced_security'] = self.analyze_advanced_security(url)

            # NEW: Business Logic Analysis
            results['business_logic'] = self.analyze_business_logic(url, soup)
            
            # NEW: Security Misconfigurations
            results['misconfigurations'] = self.analyze_security_misconfigurations(url)
            
            # NEW: Advanced Headers Analysis
            results['advanced_headers'] = self.analyze_advanced_headers(url)
            
            # NEW: Cloud Misconfigurations
            results['cloud_issues'] = self.analyze_cloud_misconfigurations(url)
            
            # NEW: Business Impact
            results['business_impact'] = self.calculate_business_impact(results)

            # NEW: Bug Bounty Recon
            results['recon'] = self.perform_recon(recon_domain)

            # NEW: JS file secret scanning
            results['js_secrets'] = self.scan_js_secrets(url, soup)

            # NEW: SSRF attack-surface indicators (passive)
            results['ssrf_indicators'] = self.check_ssrf_indicators(soup, url)

            # NEW: CVE lookup for detected technologies (best-effort, rate-limited against NVD)
            results['cve_matches'] = self.lookup_cves(results['recon'].get('technologies', {}))
            
            # NEW: Auto-save report
            self.save_report_automatically(results)
            
            # Calculate scores
            results['scores'] = self.calculate_scores(results)
            
            # Generate enhanced recommendations
            results['recommendations'] = self.generate_recommendations_enhanced(results)
            
            # NEW: Exploit Chains
            results['exploit_chains'] = self.analyze_exploit_chains(results)
            
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

    def generate_recommendations_enhanced(self, results):
        """Generate enhanced recommendations with business impact"""
        recommendations = []
        
        # SEO Recommendations
        seo = results.get('seo_analysis', {})
        if seo.get('title') and 'Missing' in seo['title']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'description': 'Add a title tag to your website - this is crucial for search engines',
                'effort': 'Low',
                'impact': 'High'
            })
        
        if seo.get('meta_description') and 'Missing' in seo['meta_description']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'High',
                'description': 'Add a meta description to improve click-through rates from search results',
                'effort': 'Low',
                'impact': 'High'
            })
        
        if seo.get('h1_count', 0) == 0:
            recommendations.append({
                'category': 'SEO',
                'priority': 'Medium',
                'description': 'Add an H1 heading to help search engines understand your page content',
                'effort': 'Low',
                'impact': 'Medium'
            })
        
        total_images = seo.get('total_images', 0)
        if total_images > 0:
            with_alt = seo.get('images_with_alt', 0)
            without_alt = total_images - with_alt
            if without_alt > 0:
                recommendations.append({
                    'category': 'Accessibility',
                    'priority': 'Medium',
                    'description': f'Add alt text to {without_alt} images for better accessibility and SEO',
                    'effort': 'Medium',
                    'impact': 'Medium'
                })
        
        # Security Recommendations
        security = results.get('security_analysis', {})
        if not security.get('has_ssl'):
            recommendations.append({
                'category': 'Security',
                'priority': 'Critical',
                'description': 'Install an SSL certificate to secure your website and build trust',
                'effort': 'Low',
                'impact': 'Critical'
            })
        
        if not security.get('X-Frame-Options'):
            recommendations.append({
                'category': 'Security',
                'priority': 'High',
                'description': 'Add X-Frame-Options header to prevent clickjacking attacks',
                'effort': 'Low',
                'impact': 'High'
            })
        
        if not security.get('X-Content-Type-Options'):
            recommendations.append({
                'category': 'Security',
                'priority': 'High',
                'description': 'Add X-Content-Type-Options header to prevent MIME type sniffing',
                'effort': 'Low',
                'impact': 'High'
            })
        
        # Performance Recommendations
        performance = results.get('performance_analysis', {})
        if performance.get('load_time', 10) > 3:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'description': f'Your page loads in {performance["load_time"]}s - optimize for faster loading',
                'effort': 'Medium',
                'impact': 'High'
            })
        
        if not performance.get('compression'):
            recommendations.append({
                'category': 'Performance',
                'priority': 'Medium',
                'description': 'Enable GZIP compression to reduce page size and speed up loading',
                'effort': 'Low',
                'impact': 'Medium'
            })
        
        # CRO Recommendations
        cro = results.get('cro_analysis', {})
        if cro:
            for rec in cro.get('recommendations', []):
                recommendations.append({
                    'category': 'CRO',
                    'priority': 'High',
                    'description': rec,
                    'effort': 'Medium',
                    'impact': 'High'
                })
        
        # Accessibility Recommendations
        accessibility = results.get('accessibility_analysis', {})
        if accessibility:
            alt_missing = accessibility.get('alt_text_missing', 0)
            if alt_missing > 0:
                recommendations.append({
                    'category': 'Accessibility',
                    'priority': 'Medium',
                    'description': f'Fix {alt_missing} images missing alt text for ADA compliance',
                    'effort': 'Medium',
                    'impact': 'Medium'
                })
            
            heading_issues = accessibility.get('heading_issues', [])
            for issue in heading_issues:
                recommendations.append({
                    'category': 'Accessibility',
                    'priority': 'Medium',
                    'description': issue,
                    'effort': 'Low',
                    'impact': 'Medium'
                })
        
        # UX Recommendations
        ux = results.get('ux_analysis', {})
        if ux:
            broken_links = ux.get('broken_links', [])
            if broken_links:
                recommendations.append({
                    'category': 'UX',
                    'priority': 'High',
                    'description': f'Fix {len(broken_links)} broken links on your site',
                    'effort': 'Low',
                    'impact': 'High'
                })
            
            mobile_issues = ux.get('mobile_issues', [])
            for issue in mobile_issues:
                recommendations.append({
                    'category': 'UX',
                    'priority': 'High',
                    'description': issue,
                    'effort': 'Low',
                    'impact': 'High'
                })
        
        return recommendations

def generate_html_report(results):
    """Generate a complete professional HTML report with all sections"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Audit Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f0f2f5; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }}
            .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .header p {{ margin: 5px 0; opacity: 0.9; }}
            .score-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
            .score-box {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
            .score-box .number {{ font-size: 32px; font-weight: bold; }}
            .score-box .label {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
            .section h2 {{ color: #333; margin-bottom: 15px; font-size: 22px; }}
            .section h3 {{ color: #555; margin: 15px 0 10px 0; font-size: 18px; }}
            .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
            .grid-4 {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; }}
            .metric {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .metric .value {{ font-size: 24px; font-weight: bold; color: #333; }}
            .metric .label {{ font-size: 12px; color: #888; margin-top: 3px; }}
            .rec {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .rec-critical {{ border-left-color: #dc3545; }}
            .rec-high {{ border-left-color: #fd7e14; }}
            .rec-medium {{ border-left-color: #ffc107; }}
            .rec-low {{ border-left-color: #28a745; }}
            .rec .category {{ font-weight: bold; }}
            .rec .priority {{ font-size: 12px; padding: 2px 8px; border-radius: 10px; }}
            .priority-critical {{ background: #dc3545; color: white; }}
            .priority-high {{ background: #fd7e14; color: white; }}
            .priority-medium {{ background: #ffc107; color: #333; }}
            .priority-low {{ background: #28a745; color: white; }}
            .badge {{ font-size: 12px; padding: 2px 8px; border-radius: 10px; }}
            .badge-success {{ background: #28a745; color: white; }}
            .badge-danger {{ background: #dc3545; color: white; }}
            .badge-warning {{ background: #ffc107; color: #333; }}
            .badge-info {{ background: #17a2b8; color: white; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f1f1f1; font-weight: bold; }}
            .footer {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-top: 30px; }}
            .footer .btn {{ background: white; color: #667eea; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; }}
            .text-success {{ color: #28a745; }}
            .text-danger {{ color: #dc3545; }}
            .text-warning {{ color: #ffc107; }}
            .text-muted {{ color: #888; }}
            @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>🏆 Website Audit Report</h1>
                <p><strong>URL:</strong> {results['url']}</p>
                <p><strong>Date:</strong> {results['timestamp']}</p>
                <p><strong>Overall Score:</strong> {results['scores']['overall']:.1f}/100</p>
            </div>
            
            <!-- Scores -->
            <h2>📊 Scores</h2>
            <div class="score-grid">
                <div class="score-box"><div class="number" style="color: #667eea">{results['scores']['seo']:.1f}</div><div class="label">SEO</div></div>
                <div class="score-box"><div class="number" style="color: #dc3545">{results['scores']['security']:.1f}</div><div class="label">Security</div></div>
                <div class="score-box"><div class="number" style="color: #28a745">{results['scores']['performance']:.1f}</div><div class="label">Performance</div></div>
                <div class="score-box"><div class="number" style="color: #764ba2">{results['scores']['overall']:.1f}</div><div class="label">Overall</div></div>
            </div>
    """
    
    # Business Impact Section
    impact = results.get('business_impact', {})
    if impact:
        html += f"""
            <div class="section">
                <h2>💰 Business Impact Analysis</h2>
                <div class="grid-4">
                    <div class="metric"><div class="value">+{impact.get('traffic_loss', 0)}</div><div class="label">Traffic Potential (month)</div></div>
                    <div class="metric"><div class="value">+{impact.get('conversion_loss', 0)}%</div><div class="label">Conversion Opportunity</div></div>
                    <div class="metric"><div class="value">${impact.get('revenue_loss', 0)}</div><div class="label">Revenue Impact (month)</div></div>
                    <div class="metric"><div class="value">{impact.get('risk_level', 'Unknown')}</div><div class="label">Risk Level</div></div>
                </div>
        """
        opportunities = impact.get('opportunities', [])
        if opportunities:
            html += "<h3>💡 Opportunities</h3><ul style='list-style:none;padding:0;'>"
            for opp in opportunities:
                html += f"<li style='padding:8px 0;border-bottom:1px solid #eee;'>✅ {opp}</li>"
            html += "</ul>"
        html += "</div>"
    
    # CRO Section
    cro = results.get('cro_analysis', {})
    if cro and cro.get('cta_count', 0) > 0:
        html += f"""
            <div class="section">
                <h2>📈 Conversion Rate Optimization</h2>
                <div class="grid-3">
                    <div class="metric"><div class="value">{cro.get('cta_count', 0)}</div><div class="label">Calls to Action</div></div>
                    <div class="metric"><div class="value">{len(cro.get('trust_signals', []))}</div><div class="label">Trust Signals</div></div>
                    <div class="metric"><div class="value">{cro.get('forms', 0)}</div><div class="label">Forms Found</div></div>
                </div>
        """
        if cro.get('cta_texts'):
            html += "<h3>CTA Examples:</h3><ul style='list-style:none;padding:0;'>"
            for cta in cro['cta_texts'][:5]:
                html += f"<li style='padding:5px 0;border-bottom:1px solid #eee;'>• {cta}</li>"
            html += "</ul>"
        html += "</div>"
    
    # Accessibility Section
    accessibility = results.get('accessibility_analysis', {})
    if accessibility:
        html += f"""
            <div class="section">
                <h2>♿ Accessibility Check</h2>
                <div class="metric" style="margin-bottom:15px;"><div class="value">{accessibility.get('score', 0)}/100</div><div class="label">Accessibility Score</div></div>
                <div class="grid-2">
                    <div class="metric"><div class="value">{accessibility.get('alt_text_missing', 0)}</div><div class="label">Images Missing Alt Text</div></div>
                    <div class="metric"><div class="value">{len(accessibility.get('heading_issues', []))}</div><div class="label">Heading Issues</div></div>
                </div>
        """
        if accessibility.get('heading_issues'):
            for issue in accessibility['heading_issues']:
                html += f"<p style='color:#dc3545;'>⚠️ {issue}</p>"
        html += "</div>"
    
    # UX Section
    ux = results.get('ux_analysis', {})
    if ux:
        html += f"""
            <div class="section">
                <h2>📱 User Experience</h2>
                <div class="grid-2">
                    <div class="metric"><div class="value">{len(ux.get('broken_links', []))}</div><div class="label">Broken Links</div></div>
                    <div class="metric"><div class="value">{len(ux.get('mobile_issues', []))}</div><div class="label">Mobile Issues</div></div>
                </div>
        """
        if ux.get('broken_links'):
            html += "<h3>🔗 Broken Links:</h3><ul>"
            for link in ux['broken_links'][:5]:
                html += f"<li>{link.get('url', 'Unknown')} (Status: {link.get('status', 'Unknown')})</li>"
            html += "</ul>"
        if ux.get('mobile_issues'):
            for issue in ux['mobile_issues']:
                html += f"<p style='color:#dc3545;'>📱 {issue}</p>"
        html += "</div>"
    
    # Security Section
    security = results.get('advanced_security', {})
    if security:
        html += f"""
            <div class="section">
                <h2>🔒 Advanced Security Analysis</h2>
        """
        
        # SSL Certificate
        ssl = security.get('ssl_certificate', {})
        if ssl:
            ssl_status = "✅ Valid" if ssl.get('is_valid') else "❌ Invalid"
            html += f"""
                <h3>SSL Certificate</h3>
                <div class="grid-3">
                    <div class="metric"><div class="value">{ssl_status}</div><div class="label">Status</div></div>
                    <div class="metric"><div class="value">{ssl.get('days_remaining', 'N/A')}</div><div class="label">Days Remaining</div></div>
                    <div class="metric"><div class="value">{ssl.get('issued_by', 'Unknown')[:20]}</div><div class="label">Issued By</div></div>
                </div>
            """
        
        # Critical Issues
        critical = security.get('critical_issues', [])
        if critical:
            html += '<div style="background:#f8d7da;padding:15px;border-radius:8px;margin:10px 0;">'
            html += '<h3 style="color:#dc3545;">🚨 CRITICAL SECURITY ISSUES</h3>'
            for issue in critical:
                html += f'<p style="color:#dc3545;">🔴 {issue}</p>'
            html += '</div>'
        
        # Warnings
        warnings = security.get('warnings', [])
        if warnings:
            html += '<div style="background:#fff3cd;padding:15px;border-radius:8px;margin:10px 0;">'
            html += '<h3 style="color:#856404;">⚠️ Security Warnings</h3>'
            for warning in warnings:
                html += f'<p style="color:#856404;">🟡 {warning}</p>'
            html += '</div>'
        
        # Security Headers
        headers = security.get('security_headers', {})
        if headers and 'error' not in headers:
            html += '<h3>Security Headers</h3><table>'
            html += '<tr><th>Status</th><th>Header</th><th>Value</th></tr>'
            for key, value in headers.items():
                status = "✅" if value != 'Missing' else "❌"
                html += f'<tr><td>{status}</td><td>{key}</td><td>{value}</td></tr>'
            html += '</table>'
        
        # Email Security
        email = security.get('email_security', {})
        if email and 'error' not in email:
            html += '<h3>📧 Email Security</h3><div class="grid-3">'
            for key in ['SPF', 'DKIM', 'DMARC']:
                status = email.get(key, 'Unknown')
                icon = "✅" if status == 'Found' else "❌"
                html += f'<div class="metric"><div class="value">{icon} {status}</div><div class="label">{key}</div></div>'
            html += '</div>'
        
        # Vulnerabilities
        html += '<h3>🛡️ Vulnerability Testing</h3><div class="grid-2">'
        sql = security.get('sql_injection', {})
        if sql:
            vuln = sql.get('vulnerable', False)
            status = "❌ Vulnerable" if vuln else "✅ Safe"
            html += f'<div class="metric"><div class="value">{status}</div><div class="label">SQL Injection</div></div>'
        xss = security.get('xss', {})
        if xss:
            vuln = xss.get('vulnerable', False)
            status = "❌ Vulnerable" if vuln else "✅ Safe"
            html += f'<div class="metric"><div class="value">{status}</div><div class="label">XSS</div></div>'
        html += '</div>'
        
        # Open Ports
        ports = security.get('open_ports', [])
        if ports:
            html += f'<p style="color:#dc3545;">🔓 Open Ports Detected: {", ".join(map(str, ports))}</p>'
            html += '<p class="text-muted">These ports are accessible from the internet and could be security risks.</p>'
        
        html += '</div>'
    
    # Recommendations
    html += """
            <h2>🎯 Recommendations</h2>
    """
    for rec in results.get('recommendations', []):
        priority_class = f"rec-{rec['priority'].lower()}"
        html += f"""
            <div class="rec {priority_class}">
                <div class="category">{rec['category']}</div>
                <span class="priority priority-{rec['priority'].lower()}">{rec['priority']} Priority</span>
                <p style="margin:8px 0;">{rec['description']}</p>
                <small>Effort: {rec.get('effort', 'Unknown')} | Business Impact: {rec.get('impact', 'Medium')}</small>
            </div>
        """
    
    # Footer
    html += """
            <div class="footer">
                <h2>🚀 Ready to Fix These Issues?</h2>
                <p>Contact us for a free consultation!</p>
                <a href="#" class="btn">Get a Quote</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html



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


def generate_business_report(results):
    """Generate a business-focused report - no technical jargon, just impact"""
    
    # Extract key data
    url = results.get('url', 'Unknown')
    timestamp = results.get('timestamp', '')
    scores = results.get('scores', {})
    overall = scores.get('overall', 0)
    
    # Business Impact
    impact = results.get('business_impact', {})
    traffic_potential = impact.get('traffic_loss', 0)
    revenue_potential = impact.get('revenue_loss', 0)
    risk_level = impact.get('risk_level', 'Unknown')
    
    # Count issues by category
    recommendations = results.get('recommendations', [])
    critical_count = sum(1 for r in recommendations if r.get('priority') == 'Critical')
    high_count = sum(1 for r in recommendations if r.get('priority') == 'High')
    medium_count = sum(1 for r in recommendations if r.get('priority') == 'Medium')
    
    # Security issues
    security = results.get('advanced_security', {})
    critical_security = security.get('critical_issues', [])
    
    # CRO insights
    cro = results.get('cro_analysis', {})
    cta_count = cro.get('cta_count', 0)
    trust_signals = len(cro.get('trust_signals', []))
    
    # Accessibility
    accessibility = results.get('accessibility_analysis', {})
    alt_missing = accessibility.get('alt_text_missing', 0)
    
    # ============================================
    # BUSINESS IMPACT STATEMENTS (No Jargon)
    # ============================================
    business_impact_statements = []
    
    if critical_count > 0:
        business_impact_statements.append(f"🚨 Your website has {critical_count} critical issues that are actively costing you customers")
    
    if revenue_potential > 0:
        business_impact_statements.append(f"💰 You could be earning an additional ${revenue_potential:.0f} per month")
    
    if traffic_potential > 0:
        business_impact_statements.append(f"📈 Opportunity to attract {traffic_potential} more visitors every month")
    
    if risk_level == 'High':
        business_impact_statements.append("🔴 Customer data may be at risk - this could lead to legal liability and loss of trust")
    
    if alt_missing > 0:
        business_impact_statements.append(f"♿ {alt_missing} images without descriptions - you're excluding potential customers with disabilities")
    
    if cta_count < 3:
        business_impact_statements.append("📢 Visitors don't know what to do next - you're losing potential sales")
    
    if trust_signals < 2:
        business_impact_statements.append("🤝 Visitors may not trust your business - add reviews and guarantees")
    
    if critical_security:
        business_impact_statements.append(f"🔒 {len(critical_security)} security risks that put your business and customers in danger")

    # ============================================
    # HTML REPORT - BUSINESS FOCUSED
    # ============================================
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Business Growth Report - {url}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f0f2f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
            .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
            .header .subtitle {{ font-size: 16px; opacity: 0.8; }}
            .header .website {{ font-size: 20px; font-weight: bold; margin: 10px 0; }}
            .header .date {{ font-size: 14px; opacity: 0.7; }}
            
            .score-ring {{ text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 12px; }}
            .score-ring .big-number {{ font-size: 72px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .score-ring .label {{ font-size: 18px; color: #666; }}
            .score-ring .sub-label {{ font-size: 14px; color: #999; margin-top: 5px; }}
            
            .impact-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }}
            .impact-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
            .impact-card .icon {{ font-size: 30px; }}
            .impact-card .number {{ font-size: 28px; font-weight: bold; color: #1a1a2e; }}
            .impact-card .label {{ font-size: 14px; color: #666; }}
            
            .statements {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #0f3460; }}
            .statements h3 {{ color: #0f3460; margin-bottom: 10px; }}
            .statements li {{ list-style: none; padding: 8px 0; border-bottom: 1px solid #d4e4f0; }}
            .statements li:last-child {{ border-bottom: none; }}
            
            .section {{ margin: 25px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
            .section h2 {{ color: #1a1a2e; margin-bottom: 15px; font-size: 20px; }}
            
            .priority-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
            .priority-item {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .priority-item .count {{ font-size: 36px; font-weight: bold; }}
            .priority-item .label {{ font-size: 14px; color: #666; }}
            .priority-critical .count {{ color: #dc3545; }}
            .priority-high .count {{ color: #fd7e14; }}
            .priority-medium .count {{ color: #ffc107; }}
            
            .issue-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .issue-item .title {{ font-weight: bold; }}
            .issue-item .impact {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .issue-critical {{ border-left-color: #dc3545; }}
            .issue-high {{ border-left-color: #fd7e14; }}
            .issue-medium {{ border-left-color: #ffc107; }}
            
            .opportunity {{ background: #d4edda; padding: 15px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #28a745; }}
            
            .footer {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-top: 30px; }}
            .footer .btn {{ background: white; color: #1a1a2e; padding: 12px 40px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; }}
            .footer p {{ margin: 10px 0; opacity: 0.9; }}
            
            @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; }} }}
            .text-center {{ text-align: center; }}
            .mt-10 {{ margin-top: 10px; }}
            .mb-10 {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <p class="subtitle">📊 BUSINESS GROWTH REPORT</p>
                <h1>How to Grow Your Online Revenue</h1>
                <div class="website">{url}</div>
                <div class="date">Generated: {timestamp[:10] if timestamp else 'Today'}</div>
            </div>
            
            <!-- Overall Score -->
            <div class="score-ring">
                <div class="big-number">{overall:.0f}</div>
                <div class="label">Your Website Performance Score</div>
                <div class="sub-label">Out of 100</div>
            </div>
            
            <!-- Quick Impact Summary -->
            <div class="impact-grid">
                <div class="impact-card">
                    <div class="icon">📈</div>
                    <div class="number">+{traffic_potential}</div>
                    <div class="label">Potential New Visitors (Monthly)</div>
                </div>
                <div class="impact-card">
                    <div class="icon">💰</div>
                    <div class="number">${revenue_potential:.0f}</div>
                    <div class="label">Potential Extra Revenue (Monthly)</div>
                </div>
                <div class="impact-card">
                    <div class="icon">🛡️</div>
                    <div class="number">{risk_level}</div>
                    <div class="label">Business Risk Level</div>
                </div>
            </div>
            
            <!-- Business Impact Statements -->
            <div class="statements">
                <h3>💡 What This Means for Your Business</h3>
                <ul>
    """
    
    if business_impact_statements:
        for statement in business_impact_statements:
            html += f"<li>{statement}</li>"
    else:
        html += "<li>✅ Your website is performing well! Here are some opportunities to grow further.</li>"
    
    html += f"""
                </ul>
            </div>
            
            <!-- Priority Breakdown -->
            <div class="section">
                <h2>📊 What Needs Your Attention</h2>
                <div class="priority-grid">
                    <div class="priority-item priority-critical">
                        <div class="count">{critical_count}</div>
                        <div class="label">🚨 Fix Immediately</div>
                    </div>
                    <div class="priority-item priority-high">
                        <div class="count">{high_count}</div>
                        <div class="label">⚠️ High Priority</div>
                    </div>
                    <div class="priority-item priority-medium">
                        <div class="count">{medium_count}</div>
                        <div class="label">📌 Medium Priority</div>
                    </div>
                </div>
            </div>
    """
    
    # Add top issues with business impact (non-technical)
    if recommendations:
        html += """
            <div class="section">
                <h2>📋 Business Impact Summary</h2>
        """
        for rec in recommendations[:5]:
            priority_class = f"issue-{rec['priority'].lower()}"
            
            # Translate technical issues to business impact (NO JARGON)
            business_impact = {
                'SEO': 'This affects how customers find you on Google',
                'Security': 'This puts your customers and reputation at risk',
                'Performance': 'Slow loading causes visitors to leave before buying',
                'Accessibility': 'This excludes potential customers and has legal implications',
                'CRO': 'This directly affects your sales and conversion rates',
                'UX': 'This frustrates visitors and drives them to competitors'
            }
            
            category = rec.get('category', '')
            business_desc = business_impact.get(category, 'This affects your business performance')
            
            html += f"""
                <div class="issue-item {priority_class}">
                    <div class="title">{rec['description']}</div>
                    <div class="impact">💡 {business_desc}</div>
                </div>
            """
        html += "</div>"
    
    # Key Opportunities
    opportunities = impact.get('opportunities', [])
    if opportunities:
        html += """
            <div class="section" style="background:#d4edda;">
                <h2>🚀 Growth Opportunities</h2>
        """
        for opp in opportunities:
            html += f'<div class="opportunity">✅ {opp}</div>'
        html += "</div>"
    
    # Security Summary (non-technical)
    if critical_security:
        html += f"""
            <div class="section" style="background:#f8d7da;">
                <h2>🔒 Security Risks</h2>
                <p style="margin-bottom:10px;">Your business faces {len(critical_security)} security risks that could:</p>
                <ul style="list-style:none;padding:0;">
        """
        for issue in critical_security[:3]:
            html += f'<li style="padding:5px 0;">🔴 {issue}</li>'
        html += """
                </ul>
                <p style="margin-top:10px;font-weight:bold;">Fixing these protects your customers and your reputation.</p>
            </div>
        """
    
    # CTA Summary (business terms)
    html += f"""
            <div class="section" style="background:#e8f4fd;">
                <h2>📈 Sales & Conversion Summary</h2>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;">
                    <div style="background:white;padding:15px;border-radius:8px;text-align:center;">
                        <div style="font-size:36px;font-weight:bold;">{cta_count}</div>
                        <div style="color:#666;">Ways to take action on your site</div>
                    </div>
                    <div style="background:white;padding:15px;border-radius:8px;text-align:center;">
                        <div style="font-size:36px;font-weight:bold;">{trust_signals}</div>
                        <div style="color:#666;">Trust-building elements found</div>
                    </div>
                </div>
    """
    
    if cta_count < 3:
        html += '<p style="margin-top:10px;">🟡 Consider adding more ways for customers to take action</p>'
    if trust_signals < 2:
        html += '<p style="margin-top:5px;">🟡 Add reviews or guarantees to build customer trust</p>'
    
    html += """
            </div>
            
            <!-- Call to Action -->
            <div class="footer">
                <h2>🚀 Ready to Grow Your Revenue?</h2>
                <p>We can help you fix these issues and unlock your website's full potential.</p>
                <p style="font-size:14px;opacity:0.8;">Schedule a free consultation to discuss your personalized growth plan.</p>
                <br>
                <a href="#" class="btn">📞 Request a Free Consultation</a>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html


def main():
    st.set_page_config(page_title="AI Website Auditor", page_icon="🚀", layout="wide")
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'audit_done' not in st.session_state:
        st.session_state.audit_done = False
    
    st.title("🚀 AI Website Auditor")
    st.markdown("Analyze any website for SEO, security, and performance issues")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    target_url = st.sidebar.text_input("Website URL", placeholder="https://example.com")

    st.sidebar.markdown("---")
    st.sidebar.subheader("✅ Scope Confirmation")
    st.sidebar.caption(
        "This tool performs active checks (path probing, port scans, safe injection tests, "
        "JS/file fetches). Only run it against assets you own or are explicitly authorized "
        "to test (e.g. a program's published scope on HackerOne/Bugcrowd/Intigriti)."
    )
    authorized = st.sidebar.checkbox("I confirm I am authorized to test this target")
    
    if st.sidebar.button("🚀 Start Audit", type="primary"):
        if not target_url:
            st.error("Please enter a website URL")
            return

        if not authorized:
            st.error("Please confirm you are authorized to test this target before scanning.")
            return
        
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url
        
        with st.spinner("🔄 Analyzing website..."):
            auditor = SimpleWebsiteAuditor()
            st.session_state.results = auditor.analyze_website(target_url)
            st.session_state.audit_done = True
    
    # Display results if available
    if st.session_state.audit_done and st.session_state.results:
        results = st.session_state.results
        
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

        # Business Impact
        st.subheader("💰 Business Impact Analysis")
        impact = results.get('business_impact', {})
        if impact:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Traffic Potential", f"+{impact.get('traffic_loss', 0)}/month")
            with col2:
                st.metric("Conversion Opportunity", f"+{impact.get('conversion_loss', 0)}%")
            with col3:
                st.metric("Revenue Impact", f"${impact.get('revenue_loss', 0)}/month")
            with col4:
                risk_color = "🟢" if impact.get('risk_level') == 'Low' else ("🟡" if impact.get('risk_level') == 'Medium' else "🔴")
                st.metric("Risk Level", f"{risk_color} {impact.get('risk_level', 'Unknown')}")
            
            opportunities = impact.get('opportunities', [])
            if opportunities:
                for opp in opportunities:
                    st.success(f"💡 {opp}")
        
        # CRO Analysis
        st.subheader("📈 Conversion Rate Optimization")
        cro = results.get('cro_analysis', {})
        if cro:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Calls to Action", cro.get('cta_count', 0))
            with col2:
                st.metric("Trust Signals", len(cro.get('trust_signals', [])))
            with col3:
                st.metric("Forms Found", cro.get('forms', 0))
            
            if cro.get('cta_texts'):
                st.write("**CTA Examples:**")
                for cta in cro['cta_texts'][:5]:
                    st.code(cta)
        
        # Accessibility
        st.subheader("♿ Accessibility Check")
        accessibility = results.get('accessibility_analysis', {})
        if accessibility:
            st.metric("Accessibility Score", f"{accessibility.get('score', 0)}/100")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Images Missing Alt Text", accessibility.get('alt_text_missing', 0))
            with col2:
                st.metric("Heading Issues", len(accessibility.get('heading_issues', [])))
            
            if accessibility.get('heading_issues'):
                for issue in accessibility['heading_issues']:
                    st.warning(f"⚠️ {issue}")
        
        # UX Analysis
        st.subheader("📱 User Experience")
        ux = results.get('ux_analysis', {})
        if ux:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Broken Links", len(ux.get('broken_links', [])))
            with col2:
                st.metric("Mobile Issues", len(ux.get('mobile_issues', [])))
            
            if ux.get('broken_links'):
                st.warning(f"⚠️ Found {len(ux['broken_links'])} broken links")
                for link in ux['broken_links'][:3]:
                    st.write(f"- {link.get('url', 'Unknown')} (Status: {link.get('status', 'Unknown')})")
            
            if ux.get('mobile_issues'):
                for issue in ux['mobile_issues']:
                    st.warning(f"📱 {issue}")

        # Advanced Security
        st.subheader("🔒 Advanced Security Analysis")
        security = results.get('advanced_security', {})
        if security:
            ssl = security.get('ssl_certificate', {})
            if ssl:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if ssl.get('is_valid'):
                        st.metric("SSL Status", "✅ Valid")
                    else:
                        st.metric("SSL Status", "❌ Invalid")
                with col2:
                    st.metric("Days Remaining", ssl.get('days_remaining', 'N/A'))
                with col3:
                    st.metric("Issued By", ssl.get('issued_by', 'Unknown')[:20])
            
            critical = security.get('critical_issues', [])
            if critical:
                st.error("🚨 CRITICAL SECURITY ISSUES")
                for issue in critical:
                    st.write(f"🔴 {issue}")
            
            warnings = security.get('warnings', [])
            if warnings:
                st.warning("⚠️ Security Warnings")
                for warning in warnings:
                    st.write(f"🟡 {warning}")
            
            headers = security.get('security_headers', {})
            if headers and 'error' not in headers:
                st.subheader("Security Headers")
                header_data = []
                for key, value in headers.items():
                    status = "✅" if value != 'Missing' else "❌"
                    header_data.append([status, key, value])
                st.table(pd.DataFrame(header_data, columns=["Status", "Header", "Value"]))
            
            email = security.get('email_security', {})
            if email and 'error' not in email:
                st.subheader("📧 Email Security")
                col1, col2, col3 = st.columns(3)
                with col1:
                    status = "✅" if email.get('SPF') == 'Found' else "❌"
                    st.metric("SPF", f"{status} {email.get('SPF', 'Unknown')}")
                with col2:
                    status = "✅" if email.get('DKIM') == 'Found' else "❌"
                    st.metric("DKIM", f"{status} {email.get('DKIM', 'Unknown')}")
                with col3:
                    status = "✅" if email.get('DMARC') == 'Found' else "❌"
                    st.metric("DMARC", f"{status} {email.get('DMARC', 'Unknown')}")
            
            st.subheader("🛡️ Vulnerability Testing")
            col1, col2 = st.columns(2)
            with col1:
                sql = security.get('sql_injection', {})
                if sql:
                    vuln = sql.get('vulnerable', False)
                    status = "❌ Vulnerable" if vuln else "✅ Safe"
                    st.metric("SQL Injection", status)
            with col2:
                xss = security.get('xss', {})
                if xss:
                    vuln = xss.get('vulnerable', False)
                    status = "❌ Vulnerable" if vuln else "✅ Safe"
                    st.metric("XSS", status)
            
            ports = security.get('open_ports', [])
            if ports:
                st.warning(f"🔓 Open Ports Detected: {', '.join(map(str, ports))}")
                st.write("These ports are accessible from the internet and could be security risks.")

            # NEW: Sensitive file exposure
            sensitive_files = security.get('sensitive_files', [])
            if sensitive_files:
                st.subheader("📁 Sensitive File / Path Exposure")
                for f in sensitive_files:
                    tag = "🚨 Likely real" if f.get('likely_real') else "🔵 Check manually (may be a catch-all page)"
                    st.write(f"- `{f['path']}` → HTTP {f['status']}, {f['size_bytes']} bytes — {tag}")

            # NEW: Open redirect
            open_redirect = security.get('open_redirect', [])
            if open_redirect:
                st.subheader("↪️ Open Redirect")
                for r in open_redirect:
                    st.warning(f"Parameter `{r['parameter']}` redirected to `{r['redirects_to']}` (HTTP {r['status']})")

            # NEW: JWT analysis
            jwt_findings = security.get('jwt_analysis', [])
            if jwt_findings:
                st.subheader("🔑 JWT Analysis")
                for jf in jwt_findings:
                    st.write(f"Token `{jf['token_preview']}` — claims: {', '.join(jf.get('payload_keys', [])) or 'none decoded'}")
                    for issue in jf.get('issues', []):
                        st.warning(f"⚠️ {issue}")
        else:
            st.info("No security data available")

        # NEW: JS Secrets Scan
        st.subheader("🗝️ JavaScript Secret Exposure")
        js_secrets = results.get('js_secrets', [])
        if js_secrets:
            st.error(f"🚨 {len(js_secrets)} potential secret(s) found in client-side JS")
            for s in js_secrets[:20]:
                st.write(f"- **{s['type']}** in `{s['file']}` → `{s['preview']}`")
            if len(js_secrets) > 20:
                st.write(f"... and {len(js_secrets) - 20} more")
            st.caption("Values are redacted. Verify manually before reporting — some 'secrets' are public/test keys.")
        else:
            st.success("✅ No obvious secrets found in scanned JS files")

        # NEW: SSRF Attack Surface Indicators
        st.subheader("🌐 SSRF Attack-Surface Indicators (passive)")
        ssrf_indicators = results.get('ssrf_indicators', [])
        if ssrf_indicators:
            st.info(f"Found {len(ssrf_indicators)} parameter(s)/input(s) that commonly relate to SSRF — these are leads to manually test, not confirmed vulnerabilities.")
            for ind in ssrf_indicators[:20]:
                st.write(f"- {ind}")
        else:
            st.info("No obvious SSRF-related parameters detected")

        # NEW: CVE Matches for Detected Technologies
        st.subheader("🧬 Known CVEs for Detected Technologies")
        cve_matches = results.get('cve_matches', [])
        if cve_matches:
            for cve in cve_matches:
                score = cve.get('cvss_score')
                score_str = f"CVSS {score}" if score is not None else "CVSS N/A"
                st.write(f"**{cve['cve_id']}** ({cve['technology']}, {score_str})")
                st.caption(cve.get('description', ''))
        else:
            st.info("No CVE matches found (or NVD lookup unavailable) — this is not a guarantee the stack is unaffected")

        # NEW: Bug Bounty Recon Results
        st.subheader("🔍 Bug Bounty Reconnaissance")
        recon = results.get('recon', {})
        if recon:
            # Summary
            summary = recon.get('summary', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Subdomains Found", summary.get('subdomains_found', 0))
            with col2:
                st.metric("URLs Discovered", summary.get('urls_found', 0))
            with col3:
                st.metric("Open Ports", summary.get('open_ports', 0))
            with col4:
                st.metric("Technologies", len(recon.get('technologies', {})))
            
            # Subdomains
            subdomains = recon.get('subdomains', [])
            if subdomains:
                with st.expander(f"🌐 Subdomains ({len(subdomains)})"):
                    for sub in subdomains[:50]:
                        st.write(f"- {sub}")
                    if len(subdomains) > 50:
                        st.write(f"... and {len(subdomains) - 50} more")
            
            # URLs
            urls = recon.get('urls', [])
            if urls:
                with st.expander(f"🔗 URLs Discovered ({len(urls)})"):
                    for url in urls[:20]:
                        st.write(f"- {url}")
                    if len(urls) > 20:
                        st.write(f"... and {len(urls) - 20} more")
            
            # Open Ports
            ports = recon.get('open_ports', [])
            if ports:
                with st.expander(f"🔌 Open Ports ({len(ports)})"):
                    for port in ports:
                        st.write(f"- Port {port.get('port')} ({port.get('service')}) - {port.get('state')}")
            
            # Technologies
            tech = recon.get('technologies', {})
            if tech:
                with st.expander("⚙️ Technologies Detected"):
                    for category, items in tech.items():
                        if items:
                            st.write(f"**{category.title()}:** {', '.join(items)}")
        else:
            st.info("No recon data available")

        # NEW: Business Logic Vulnerabilities
        st.subheader("🧠 Business Logic Vulnerabilities")
        logic = results.get('business_logic', [])
        if logic:
            for issue in logic:
                severity = issue.get('severity', 'Medium')
                if severity == 'Critical':
                    st.error(f"🚨 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'High':
                    st.error(f"🔴 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'Medium':
                    st.warning(f"🟡 {issue.get('category', 'Issue')} - {severity}")
                else:
                    st.info(f"🔵 {issue.get('category', 'Issue')} - {severity}")
                
                st.write(f"**Description:** {issue.get('description', '')}")
                if issue.get('details'):
                    with st.expander("View Details"):
                        st.json(issue.get('details', []))
        else:
            st.success("✅ No business logic vulnerabilities detected")
        
        # NEW: Security Misconfigurations
        st.subheader("⚙️ Security Misconfigurations")
        misconfig = results.get('misconfigurations', [])
        if misconfig:
            for issue in misconfig:
                severity = issue.get('severity', 'Medium')
                if severity == 'Critical':
                    st.error(f"🚨 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'High':
                    st.error(f"🔴 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'Medium':
                    st.warning(f"🟡 {issue.get('category', 'Issue')} - {severity}")
                else:
                    st.info(f"🔵 {issue.get('category', 'Issue')} - {severity}")
                
                st.write(f"**Description:** {issue.get('description', '')}")
                if issue.get('details'):
                    with st.expander("View Details"):
                        st.json(issue.get('details', []))
        else:
            st.success("✅ No security misconfigurations detected")
        
        # NEW: Advanced Headers Analysis
        st.subheader("📋 Advanced Headers Analysis")
        headers = results.get('advanced_headers', {})
        if headers and 'error' not in headers:
            # CSP Analysis
            csp = headers.get('csp', {})
            if csp:
                if csp.get('present'):
                    st.success("✅ Content-Security-Policy is present")
                    if csp.get('weaknesses'):
                        for weakness in csp['weaknesses']:
                            st.warning(f"⚠️ {weakness.get('description', '')}")
                else:
                    st.error("❌ Content-Security-Policy is missing - XSS prevention limited")
            
            # CORS Analysis
            cors = headers.get('cors', {})
            if cors:
                if cors.get('present'):
                    st.info(f"ℹ️ CORS Policy: {cors.get('value', 'Unknown')}")
                    if cors.get('weaknesses'):
                        for weakness in cors['weaknesses']:
                            st.warning(f"⚠️ {weakness.get('description', '')}")
                else:
                    st.info("ℹ️ No CORS headers detected")
            
            # Permissions Policy
            pp = headers.get('permissions_policy', {})
            if pp:
                if pp.get('present'):
                    st.success("✅ Permissions-Policy is present")
                else:
                    st.info("ℹ️ Permissions-Policy not set (optional)")
            
            # Other header issues
            for issue in headers.get('issues', []):
                st.warning(f"⚠️ {issue.get('description', '')}")
        else:
            st.info("No advanced headers data available")

        # NEW: Cloud Misconfigurations
        st.subheader("☁️ Cloud Misconfigurations")
        cloud = results.get('cloud_issues', [])
        if cloud:
            for issue in cloud:
                severity = issue.get('severity', 'Medium')
                if severity == 'Critical':
                    st.error(f"🚨 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'High':
                    st.error(f"🔴 {issue.get('category', 'Issue')} - {severity}")
                elif severity == 'Medium':
                    st.warning(f"🟡 {issue.get('category', 'Issue')} - {severity}")
                else:
                    st.info(f"🔵 {issue.get('category', 'Issue')} - {severity}")
                
                st.write(f"**Description:** {issue.get('description', '')}")
                if issue.get('details'):
                    with st.expander("View Details"):
                        st.json(issue.get('details', []))
        else:
            st.success("✅ No cloud misconfigurations detected")
        
        # NEW: Exploit Chains
        st.subheader("🔗 Exploit Chains (Critical Risk Combinations)")
        chains = results.get('exploit_chains', [])
        if chains:
            for chain in chains:
                severity = chain.get('severity', 'Critical')
                st.error(f"🚨 {chain.get('name', 'Exploit Chain')} - {severity}")
                st.write(f"**Description:** {chain.get('description', '')}")
                st.write(f"**Impact:** {chain.get('impact', 'Unknown')}")
                if chain.get('findings'):
                    with st.expander("Findings in this chain"):
                        for finding in chain['findings']:
                            st.write(f"- {finding}")
        else:
            st.success("✅ No exploit chains detected")

        # Recommendations
        st.subheader("📋 Recommendations")
        auditor_for_cvss = SimpleWebsiteAuditor()
        for rec in results['recommendations']:
            cvss = auditor_for_cvss.estimate_cvss(rec.get('priority', 'Medium'))
            with st.expander(f"🔴 {rec['category']} - {rec['priority']} Priority (indicative CVSS {cvss['range']})"):
                st.write(f"**{rec['description']}**")
                st.write(f"Effort: {rec['effort']}")
                st.caption(f"Indicative CVSS base-score band: {cvss['range']} — score each finding individually with a CVSS calculator before submitting to a program.")
        
        # Report Preview
        html_report = generate_html_report(results)
        st.subheader("📄 Report Preview")
        st.components.v1.html(html_report, height=500, scrolling=True)
        
        st.success("✅ Analysis complete!")
        
        # Download buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.download_button(
                label="📥 Technical Report (HTML)",
                data=html_report,
                file_name=f"technical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                key="tech_report"
            )
        
        with col2:
            business_report = generate_business_report(results)
            st.download_button(
                label="📊 Business Report (HTML)",
                data=business_report,
                file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                key="business_report"
            )

        with col3:
            json_report = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="🧾 Raw Findings (JSON)",
                data=json_report,
                file_name=f"findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="json_report"
            )

        with col4:
            csv_rows = []
            for cat_key, label in [
                ('business_logic', 'Business Logic'),
                ('misconfigurations', 'Misconfiguration'),
                ('cloud_issues', 'Cloud'),
            ]:
                for issue in results.get(cat_key, []):
                    csv_rows.append({
                        'category': label,
                        'finding': issue.get('category', ''),
                        'severity': issue.get('severity', ''),
                        'description': issue.get('description', '')
                    })
            for f in results.get('advanced_security', {}).get('sensitive_files', []):
                csv_rows.append({
                    'category': 'Sensitive File',
                    'finding': f['path'],
                    'severity': 'Critical' if f.get('likely_real') else 'Info',
                    'description': f"HTTP {f['status']}, {f['size_bytes']} bytes"
                })
            for cve in results.get('cve_matches', []):
                csv_rows.append({
                    'category': 'CVE',
                    'finding': cve['cve_id'],
                    'severity': f"CVSS {cve.get('cvss_score', 'N/A')}",
                    'description': cve.get('description', '')
                })
            csv_df = pd.DataFrame(csv_rows) if csv_rows else pd.DataFrame(columns=['category', 'finding', 'severity', 'description'])
            st.download_button(
                label="📑 Findings (CSV)",
                data=csv_df.to_csv(index=False),
                file_name=f"findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="csv_report"
            )

if __name__ == "__main__":
    main()
