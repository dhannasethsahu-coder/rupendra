#!/bin/bash
cd /home/rupendra/ai-website-auditor
source venv/bin/activate
export PATH=$PATH:/home/rupendra/go/bin
streamlit run app.py
