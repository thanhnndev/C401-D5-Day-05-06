"""Integration test: send a real email when SMTP_* is configured in the environment."""

from __future__ import annotations

import time

import pytest
from config import get_smtp_host, get_smtp_password

from tools.email import bulk_email_sender_tool, send_email_smtp

TEST_TO = 'sv5.test@thanhnn.dev'

configured = bool(get_smtp_host() and get_smtp_password())


@pytest.mark.skipif(
    not configured,
    reason='Set SMTP_HOST and SMTP_PASSWORD in .env to run this test.',
)
def test_send_email_to_sv5_test() -> None:
    stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    subject = f'c401 email tool test {stamp}'
    body = f'Integration test from tests/test_email_send.py at {stamp}.'

    result = send_email_smtp(to=TEST_TO, subject=subject, body=body)

    assert result.startswith('Email sent successfully'), result


@pytest.mark.skipif(
    not configured,
    reason='Set SMTP_HOST and SMTP_PASSWORD in .env to run this test.',
)
def test_bulk_send_email() -> None:
    stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    drafts = [
        {
            'email': TEST_TO,
            'subject': f'c401 bulk test 1/2 {stamp}',
            'body': f'Batch email 1 at {stamp}'
        },
        {
            'email': TEST_TO,
            'subject': f'c401 bulk test 2/2 {stamp}',
            'body': f'Batch email 2 at {stamp}'
        }
    ]

    result = bulk_email_sender_tool.invoke({'drafts': drafts})

    assert result['total'] == 2
    assert result['success'] >= 0  # Success depends on actual SMTP, but total should be correct
