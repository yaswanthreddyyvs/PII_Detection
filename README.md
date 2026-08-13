# PII Redaction Tool

## Overview

A document-level PII detection and redaction system that
identifies sensitive information in a Red Herring Prospectus
and replaces it with synthetic values.

## Supported PII

- Person names
- Email addresses
- Phone numbers
- Company names
- Physical addresses
- SSNs
- Credit card numbers
- Dates of birth
- IP addresses

## Architecture

DOCX
 ↓
Document Reader
 ↓
Presidio + Custom Regex
 ↓
Detection Merge
 ↓
Synthetic Replacement
 ↓
DOCX Writer
 ↓
Redacted DOCX

## Technologies

- Python
- python-docx
- Microsoft Presidio
- spaCy
- Faker
- Regular Expressions

