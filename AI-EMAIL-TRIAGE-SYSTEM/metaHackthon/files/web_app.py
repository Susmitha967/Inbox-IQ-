"""
web_app.py — Anyone can connect their Gmail and use your agent
"""

from flask import Flask, redirect, request, session, url_for, render_template_string
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os, json, base64, re
from datetime import datetime
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "change-this-to-random-string-123"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
CLIENT_SECRETS_FILE = "credentials.json"

# ── Pages ──────────────────────────────────────────────────

HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aura — AI Email Intelligence</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --gold: #C9A96E;
            --gold-light: #E8D5B0;
            --gold-dim: #8A6D42;
            --ink: #0A0A0A;
            --ink-2: #111111;
            --ink-3: #1A1A1A;
            --surface: #141414;
            --surface-2: #1E1E1E;
            --surface-3: #252525;
            --border: rgba(201,169,110,0.15);
            --border-strong: rgba(201,169,110,0.35);
            --text-primary: #F0EDE8;
            --text-secondary: #9A9189;
            --text-muted: #5C5650;
            --radius: 2px;
        }

        html { scroll-behavior: smooth; }

        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--ink);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ── Noise texture overlay ── */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
            opacity: 0.4;
        }

        /* ── Ambient glow ── */
        .ambient {
            position: fixed;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            filter: blur(120px);
            pointer-events: none;
            z-index: 0;
        }
        .ambient-1 {
            top: -200px; left: 50%;
            transform: translateX(-50%);
            background: radial-gradient(circle, rgba(201,169,110,0.07) 0%, transparent 70%);
        }
        .ambient-2 {
            bottom: -100px; right: -100px;
            width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(201,169,110,0.04) 0%, transparent 70%);
        }

        /* ── Navigation ── */
        nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 100;
            padding: 24px 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(201,169,110,0.08);
            backdrop-filter: blur(20px);
            background: rgba(10,10,10,0.6);
        }

        .nav-logo {
            font-family: 'Cormorant Garamond', serif;
            font-size: 22px;
            font-weight: 500;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            text-decoration: none;
        }
        .nav-logo span {
            color: var(--gold);
        }

        .nav-pill {
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--text-muted);
            padding: 6px 14px;
            border: 1px solid var(--border);
            border-radius: 40px;
        }

        /* ── Hero ── */
        .hero {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 120px 40px 80px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: var(--gold);
            margin-bottom: 40px;
            opacity: 0;
            animation: fadeUp 0.8s ease 0.2s forwards;
        }
        .eyebrow::before, .eyebrow::after {
            content: '';
            display: block;
            width: 24px;
            height: 1px;
            background: var(--gold-dim);
        }

        .hero-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(52px, 8vw, 96px);
            font-weight: 300;
            line-height: 1.05;
            letter-spacing: -0.01em;
            color: var(--text-primary);
            margin-bottom: 28px;
            opacity: 0;
            animation: fadeUp 0.9s ease 0.35s forwards;
        }
        .hero-title em {
            font-style: italic;
            color: var(--gold);
        }

        .hero-subtitle {
            font-size: 16px;
            font-weight: 300;
            line-height: 1.7;
            color: var(--text-secondary);
            max-width: 520px;
            margin-bottom: 60px;
            opacity: 0;
            animation: fadeUp 0.9s ease 0.5s forwards;
        }

        /* ── CTA Button ── */
        .cta-wrap {
            display: flex;
            align-items: center;
            gap: 20px;
            opacity: 0;
            animation: fadeUp 0.9s ease 0.65s forwards;
        }

        .btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--gold);
            color: var(--ink);
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.06em;
            padding: 16px 36px;
            border-radius: var(--radius);
            text-decoration: none;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .btn-primary:hover {
            background: var(--gold-light);
            transform: translateY(-1px);
            box-shadow: 0 12px 40px rgba(201,169,110,0.25);
        }
        .btn-primary:active { transform: translateY(0); }

        .btn-secondary {
            font-size: 13px;
            font-weight: 400;
            color: var(--text-secondary);
            text-decoration: none;
            letter-spacing: 0.04em;
            transition: color 0.2s;
        }
        .btn-secondary:hover { color: var(--text-primary); }

        /* ── Divider ── */
        .divider-line {
            width: 1px;
            height: 40px;
            background: linear-gradient(to bottom, transparent, var(--border), transparent);
            margin: 80px auto 0;
            opacity: 0;
            animation: fadeUp 1s ease 0.9s forwards;
        }

        /* ── Features Section ── */
        .features {
            position: relative;
            z-index: 1;
            padding: 100px 60px;
            max-width: 1100px;
            margin: 0 auto;
        }

        .section-label {
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: var(--gold-dim);
            text-align: center;
            margin-bottom: 64px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: var(--border);
            border: 1px solid var(--border);
        }

        .feature-card {
            background: var(--ink-2);
            padding: 48px 36px;
            transition: background 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--gold-dim), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .feature-card:hover { background: var(--surface); }
        .feature-card:hover::before { opacity: 1; }

        .feature-icon {
            width: 36px;
            height: 36px;
            border: 1px solid var(--border);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 28px;
            font-size: 14px;
            background: var(--surface-2);
        }

        .feature-num {
            font-family: 'Cormorant Garamond', serif;
            font-size: 11px;
            letter-spacing: 0.14em;
            color: var(--gold-dim);
            margin-bottom: 14px;
        }

        .feature-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 22px;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 12px;
            line-height: 1.2;
        }

        .feature-desc {
            font-size: 13px;
            font-weight: 300;
            line-height: 1.7;
            color: var(--text-muted);
        }

        /* ── Footer ── */
        footer {
            position: relative;
            z-index: 1;
            text-align: center;
            padding: 40px;
            border-top: 1px solid var(--border);
            font-size: 12px;
            color: var(--text-muted);
            letter-spacing: 0.05em;
        }

        /* ── Animations ── */
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            nav { padding: 20px 24px; }
            .features { padding: 60px 24px; }
            .features-grid { grid-template-columns: 1fr 1fr; }
            .hero-title { font-size: 48px; }
        }
        @media (max-width: 480px) {
            .features-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="ambient ambient-1"></div>
    <div class="ambient ambient-2"></div>

    <nav>
        <a href="/" class="nav-logo">AI Gmail Triage System (AI-GTS)</a>
        <span class="nav-pill">Stop worrying about your Email replys</span>
    </nav>

    <section class="hero">
        <div class="eyebrow">AI-Powered Email Assistant</div>
        <h1 class="hero-title">
            Your inbox,<br><em>reimagined</em>
        </h1>
        <p class="hero-subtitle">
            Connect Gmail. Let AI-GTS read, classify, prioritize, and reply to your emails — so you focus only on what matters.
        </p>
        <div class="cta-wrap">
            <a href="/connect" class="btn-primary">
                Connect Gmail &rarr;
            </a>
            <a href="#features" class="btn-secondary">See how it works</a>
        </div>
        <div class="divider-line"></div>
    </section>

    <section class="features" id="features">
        <p class="section-label">Capabilities</p>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">✦</div>
                <div class="feature-num">01</div>
                <h3 class="feature-title">Reads Emails</h3>
                <p class="feature-desc">Fetches your real inbox automatically and extracts context intelligently.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">◈</div>
                <div class="feature-num">02</div>
                <h3 class="feature-title">AI Classifies</h3>
                <p class="feature-desc">Distinguishes spam, important, and normal emails with precision.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">◎</div>
                <div class="feature-num">03</div>
                <h3 class="feature-title">Sets Priority</h3>
                <p class="feature-desc">Surfaces high-priority messages so nothing critical is missed.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⟡</div>
                <div class="feature-num">04</div>
                <h3 class="feature-title">Auto Replies</h3>
                <p class="feature-desc">Sends thoughtful replies only to real humans — never bots or spam.</p>
            </div>
        </div>
    </section>

    <footer>
        &copy; 2025 Aura &nbsp;&middot;&nbsp; AI Email Intelligence
    </footer>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard — Aura</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --gold: #C9A96E;
            --gold-light: #E8D5B0;
            --gold-dim: #8A6D42;
            --ink: #0A0A0A;
            --ink-2: #111111;
            --surface: #141414;
            --surface-2: #1E1E1E;
            --surface-3: #252525;
            --border: rgba(201,169,110,0.12);
            --border-strong: rgba(201,169,110,0.3);
            --text-primary: #F0EDE8;
            --text-secondary: #9A9189;
            --text-muted: #5C5650;
            --green: #4ADE80;
            --red: #F87171;
            --amber: #FBBF24;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--ink);
            color: var(--text-primary);
            min-height: 100vh;
        }

        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
            opacity: 0.4;
        }

        /* ── Layout ── */
        .layout {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: 260px 1fr;
            min-height: 100vh;
        }

        /* ── Sidebar ── */
        .sidebar {
            border-right: 1px solid var(--border);
            padding: 40px 32px;
            display: flex;
            flex-direction: column;
            background: var(--ink-2);
        }

        .logo {
            font-family: 'Cormorant Garamond', serif;
            font-size: 24px;
            font-weight: 500;
            letter-spacing: 0.06em;
            margin-bottom: 48px;
            color: var(--text-primary);
        }
        .logo span { color: var(--gold); }

        .sidebar-label {
            font-size: 9px;
            font-weight: 500;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 16px;
        }

        .sidebar-nav {
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-bottom: 40px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 400;
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.2s;
            cursor: pointer;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
        }
        .nav-item:hover { background: var(--surface-2); color: var(--text-primary); }
        .nav-item.active {
            background: rgba(201,169,110,0.1);
            color: var(--gold);
            border: 1px solid rgba(201,169,110,0.15);
        }
        .nav-item-icon {
            width: 16px;
            text-align: center;
            font-size: 12px;
            opacity: 0.7;
        }

        .sidebar-spacer { flex: 1; }

        .sidebar-user {
            padding: 16px;
            border: 1px solid var(--border);
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(201,169,110,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            color: var(--gold);
            font-weight: 500;
            flex-shrink: 0;
        }
        .user-info { flex: 1; min-width: 0; }
        .user-name {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .user-status {
            font-size: 11px;
            color: var(--green);
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .user-status::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--green);
            display: inline-block;
        }

        .disconnect-btn {
            font-size: 11px;
            color: var(--text-muted);
            text-decoration: none;
            padding: 4px 8px;
            border-radius: 3px;
            transition: all 0.2s;
        }
        .disconnect-btn:hover { color: var(--red); background: rgba(248,113,113,0.08); }

        /* ── Main ── */
        .main {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .topbar {
            padding: 28px 48px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .page-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 28px;
            font-weight: 400;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }

        .run-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--gold);
            color: var(--ink);
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.04em;
            padding: 12px 28px;
            border-radius: 2px;
            border: none;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .run-btn:hover {
            background: var(--gold-light);
            box-shadow: 0 8px 30px rgba(201,169,110,0.2);
            transform: translateY(-1px);
        }
        .run-btn:active { transform: translateY(0); }
        .run-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* ── Content ── */
        .content {
            flex: 1;
            padding: 40px 48px;
            overflow-y: auto;
        }

        /* ── Stats bar ── */
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: var(--border);
            border: 1px solid var(--border);
            margin-bottom: 40px;
        }

        .stat-cell {
            background: var(--ink-2);
            padding: 24px 28px;
        }

        .stat-label {
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        .stat-value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 32px;
            font-weight: 400;
            color: var(--text-primary);
            line-height: 1;
        }
        .stat-value.gold { color: var(--gold); }
        .stat-sub {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* ── Empty / Output ── */
        .output-area {
            border: 1px solid var(--border);
        }

        .output-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--surface);
        }
        .output-header-title {
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-muted);
        }
        .output-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--text-muted);
        }
        .output-dot.live { background: var(--green); }

        .output-empty {
            padding: 80px 40px;
            text-align: center;
        }
        .output-empty-icon {
            font-size: 32px;
            margin-bottom: 20px;
            opacity: 0.3;
        }
        .output-empty-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 22px;
            font-weight: 400;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        .output-empty-sub {
            font-size: 13px;
            color: var(--text-muted);
        }

        /* ── Email rows ── */
        .email-list { display: flex; flex-direction: column; }

        .email-row {
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: start;
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            gap: 20px;
            transition: background 0.15s;
        }
        .email-row:last-child { border-bottom: none; }
        .email-row:hover { background: rgba(255,255,255,0.02); }

        .email-index {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            color: var(--text-muted);
            min-width: 20px;
        }
        .email-meta { flex: 1; min-width: 0; }
        .email-subject {
            font-size: 14px;
            font-weight: 500;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 4px;
        }
        .email-sender {
            font-size: 12px;
            color: var(--text-muted);
            font-family: 'DM Mono', monospace;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .email-left {
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }

        .email-badges {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
        }

        .badge {
            font-size: 9px;
            font-weight: 500;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 1px;
        }

        .badge-spam { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.2); }
        .badge-important { background: rgba(251,191,36,0.12); color: #FBBF24; border: 1px solid rgba(251,191,36,0.2); }
        .badge-normal { background: rgba(74,222,128,0.08); color: #4ADE80; border: 1px solid rgba(74,222,128,0.15); }
        .badge-high { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.2); }
        .badge-medium { background: rgba(201,169,110,0.12); color: #C9A96E; border: 1px solid rgba(201,169,110,0.2); }
        .badge-low { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px solid var(--border); }
        .badge-reply { background: rgba(74,222,128,0.08); color: #4ADE80; border: 1px solid rgba(74,222,128,0.15); }

        /* ── Processing state ── */
        .processing-state {
            padding: 60px 40px;
            text-align: center;
            display: none;
        }
        .processing-state.visible { display: block; }

        .pulse-ring {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: 1px solid var(--gold-dim);
            margin: 0 auto 20px;
            position: relative;
            animation: pulse 2s ease infinite;
        }
        .pulse-ring::after {
            content: '';
            position: absolute;
            inset: 8px;
            border-radius: 50%;
            background: rgba(201,169,110,0.2);
            animation: pulse 2s ease 0.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.7; }
            50% { transform: scale(1.1); opacity: 1; }
        }

        .processing-text {
            font-family: 'Cormorant Garamond', serif;
            font-size: 20px;
            font-weight: 400;
            color: var(--text-secondary);
        }
        .processing-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 8px;
            font-family: 'DM Mono', monospace;
        }

        @media (max-width: 900px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .topbar, .content { padding: 24px; }
            .stats-bar { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo">A<span>u</span>ra</div>

            <p class="sidebar-label">Navigation</p>
            <nav class="sidebar-nav">
                <button class="nav-item active">
                    <span class="nav-item-icon">◈</span>
                    Dashboard
                </button>
                <button class="nav-item" onclick="runAgent()">
                    <span class="nav-item-icon">▶</span>
                    Run Agent
                </button>
            </nav>

            <div class="sidebar-spacer"></div>

            <div class="sidebar-user">
                <div class="user-avatar">G</div>
                <div class="user-info">
                    <div class="user-name">Gmail Account</div>
                    <div class="user-status">Connected</div>
                </div>
                <a href="/disconnect" class="disconnect-btn" title="Disconnect">✕</a>
            </div>
        </aside>

        <!-- Main Content -->
        <div class="main">
            <div class="topbar">
                <h1 class="page-title">Inbox Intelligence</h1>
                <button class="run-btn" id="runBtn" onclick="runAgent()">
                    ▶&ensp;Run Agent
                </button>
            </div>

            <div class="content">
                <!-- Stats -->
                <div class="stats-bar" id="statsBar">
                    <div class="stat-cell">
                        <div class="stat-label">Processed</div>
                        <div class="stat-value gold" id="statTotal">—</div>
                        <div class="stat-sub">emails</div>
                    </div>
                    <div class="stat-cell">
                        <div class="stat-label">Replies Sent</div>
                        <div class="stat-value" id="statReplies">—</div>
                        <div class="stat-sub">automated</div>
                    </div>
                    <div class="stat-cell">
                        <div class="stat-label">Priority</div>
                        <div class="stat-value" id="statPriority">—</div>
                        <div class="stat-sub">high-priority</div>
                    </div>
                    <div class="stat-cell">
                        <div class="stat-label">Score</div>
                        <div class="stat-value" id="statScore">—</div>
                        <div class="stat-sub">agent score</div>
                    </div>
                </div>

                <!-- Output -->
                <div class="output-area">
                    <div class="output-header">
                        <div class="output-dot" id="outputDot"></div>
                        <span class="output-header-title" id="outputHeaderTitle">Awaiting Run</span>
                    </div>

                    <!-- Empty state -->
                    <div class="output-empty" id="emptyState">
                        <div class="output-empty-icon">✦</div>
                        <div class="output-empty-title">No emails processed yet</div>
                        <div class="output-empty-sub">Click "Run Agent" to analyze your inbox</div>
                    </div>

                    <!-- Processing state -->
                    <div class="processing-state" id="processingState">
                        <div class="pulse-ring"></div>
                        <div class="processing-text">Analyzing your inbox&hellip;</div>
                        <div class="processing-sub" id="processingStep">Connecting to Gmail</div>
                    </div>

                    <!-- Email list -->
                    <div class="email-list" id="emailList" style="display:none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const processingSteps = [
            'Connecting to Gmail',
            'Fetching messages',
            'Running AI classification',
            'Evaluating priorities',
            'Composing replies',
            'Finalizing results'
        ];
        let stepIdx = 0, stepTimer = null;

        function startProcessingAnimation() {
            stepIdx = 0;
            document.getElementById('processingStep').textContent = processingSteps[0];
            stepTimer = setInterval(() => {
                stepIdx = (stepIdx + 1) % processingSteps.length;
                document.getElementById('processingStep').textContent = processingSteps[stepIdx];
            }, 1800);
        }

        function stopProcessingAnimation() {
            clearInterval(stepTimer);
        }

        async function runAgent() {
            const btn = document.getElementById('runBtn');
            btn.disabled = true;

            // Show processing
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('emailList').style.display = 'none';
            document.getElementById('processingState').classList.add('visible');
            document.getElementById('outputDot').classList.add('live');
            document.getElementById('outputHeaderTitle').textContent = 'Processing';
            startProcessingAnimation();

            try {
                const res = await fetch('/run');
                const data = await res.json();

                stopProcessingAnimation();
                document.getElementById('processingState').classList.remove('visible');

                if (data.error) {
                    document.getElementById('emptyState').style.display = 'block';
                    document.getElementById('emptyState').innerHTML = `
                        <div class="output-empty-icon" style="color:#F87171">✕</div>
                        <div class="output-empty-title">Something went wrong</div>
                        <div class="output-empty-sub" style="color:#F87171">${data.error}</div>
                    `;
                    document.getElementById('outputHeaderTitle').textContent = 'Error';
                    document.getElementById('outputDot').classList.remove('live');
                    document.getElementById('outputDot').style.background = '#F87171';
                    return;
                }

                // Update stats
                const replies = data.emails.filter(e => e.reply_sent).length;
                const highPriority = data.emails.filter(e => e.priority === 'high').length;
                document.getElementById('statTotal').textContent = data.total;
                document.getElementById('statReplies').textContent = replies;
                document.getElementById('statPriority').textContent = highPriority;
                document.getElementById('statScore').textContent = data.score;

                // Build email rows
                const list = document.getElementById('emailList');
                list.innerHTML = '';
                data.emails.forEach((e, i) => {
                    const row = document.createElement('div');
                    row.className = 'email-row';
                    row.innerHTML = `
                        <div class="email-left">
                            <span class="email-index">${String(i+1).padStart(2,'0')}</span>
                            <div class="email-meta">
                                <div class="email-subject">${escHtml(e.subject)}</div>
                                <div class="email-sender">${escHtml(e.sender)}</div>
                            </div>
                        </div>
                        <div class="email-badges">
                            <span class="badge badge-${e.classification}">${e.classification}</span>
                            <span class="badge badge-${e.priority}">${e.priority}</span>
                            ${e.reply_sent ? '<span class="badge badge-reply">replied</span>' : ''}
                        </div>
                    `;
                    list.appendChild(row);
                });

                list.style.display = 'flex';
                document.getElementById('outputHeaderTitle').textContent = `${data.total} Emails Processed`;
                document.getElementById('outputDot').classList.remove('live');
                document.getElementById('outputDot').style.background = '#4ADE80';

            } catch(err) {
                stopProcessingAnimation();
                document.getElementById('processingState').classList.remove('visible');
                document.getElementById('emptyState').style.display = 'block';
                document.getElementById('emptyState').innerHTML = `
                    <div class="output-empty-icon" style="color:#F87171">✕</div>
                    <div class="output-empty-title">Connection failed</div>
                    <div class="output-empty-sub">Please try again</div>
                `;
            } finally {
                btn.disabled = false;
            }
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }
    </script>
</body>
</html>
"""

# ── Routes ─────────────────────────────────────────────────

@app.route("/")
def index():
    return HOME_PAGE


@app.route("/connect")
def connect():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(auth_url)


@app.route("/callback")
def callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session['state'],
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes)
    }
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
def dashboard():
    if 'credentials' not in session:
        return redirect(url_for('index'))
    return DASHBOARD_PAGE


@app.route("/run")
def run_agent():
    if 'credentials' not in session:
        return {"error": "Not connected"}, 401

    try:
        creds = Credentials(**session['credentials'])
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(
            userId='me', q='label:INBOX', maxResults=5
        ).execute()
        messages = results.get('messages', [])

        NO_REPLY_PATTERNS = [
            "no-reply", "noreply", "mailer-daemon", "do-not-reply",
            "accounts.google.com", "notifications@", "alert@", "alerts@",
            "automated@", "internshala", "linkedin", "newsletter",
            "security@", "update@", "team@"
        ]

        processed = []

        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()

            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'unknown')
            message_id_header = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
            thread_id = msg_data.get('threadId', msg['id'])

            subject_lower = subject.lower()
            sender_lower = sender.lower()
            is_automated = any(p in sender_lower for p in NO_REPLY_PATTERNS)

            if any(w in subject_lower for w in ['alert', 'security', 'verify', 'password', 'spam', 'win', 'prize', 'offer']):
                classification = "spam"
                priority = "low"
            elif any(w in subject_lower for w in ['urgent', 'important', 'asap', 'deadline', 'meeting', 'interview']):
                classification = "important"
                priority = "high"
            else:
                classification = "normal"
                priority = "medium"

            reply_sent = False
            if not is_automated and classification != "spam":
                reply_text = f"Thank you for your email regarding '{subject}'. I have received your message and will get back to you shortly.\n\nBest regards"
                try:
                    reply_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
                    message = MIMEText(reply_text)
                    message['to'] = sender
                    message['subject'] = reply_subject
                    if message_id_header:
                        message['In-Reply-To'] = message_id_header
                        message['References'] = message_id_header
                    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                    service.users().messages().send(
                        userId='me',
                        body={'raw': raw, 'threadId': thread_id}
                    ).execute()
                    reply_sent = True
                except:
                    reply_sent = False

            processed.append({
                "subject": subject[:60],
                "sender": sender[:50],
                "classification": classification,
                "priority": priority,
                "reply_sent": reply_sent
            })

        return {
            "status": "success",
            "total": len(processed),
            "score": round(len(processed) * 0.8, 2),
            "emails": processed
        }

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/disconnect")
def disconnect():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)