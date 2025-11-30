"""Base styles shared across all email templates."""


def get_base_styles() -> str:
    """Return shared base styles for all email templates."""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            background-color: #f8fafc;
            -webkit-font-smoothing: antialiased;
        }
        .wrapper {
            width: 100%;
            background-color: #f8fafc;
            padding: 40px 20px;
        }
        .container {
            max-width: 560px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            padding: 32px 40px;
            text-align: center;
        }
        .header h1 {
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header .icon {
            font-size: 48px;
            margin-bottom: 12px;
        }
        .content {
            padding: 40px;
        }
        .content h2 {
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 16px;
        }
        .content p {
            color: #4a5568;
            font-size: 15px;
            margin-bottom: 16px;
        }
        .code-box {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 2px solid #0ea5e9;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin: 24px 0;
        }
        .code-box .code {
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #0369a1;
            letter-spacing: 8px;
        }
        .id-box {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 24px 0;
            word-break: break-all;
        }
        .id-box .id {
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 16px;
            font-weight: 600;
            color: #334155;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: #ffffff !important;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 15px;
            transition: transform 0.2s;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4);
        }
        .button:hover {
            transform: translateY(-1px);
        }
        .button-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            box-shadow: 0 4px 14px 0 rgba(239, 68, 68, 0.4);
        }
        .button-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.4);
        }
        .alert {
            padding: 16px 20px;
            border-radius: 10px;
            margin: 20px 0;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .alert-warning {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
        }
        .alert-warning p {
            color: #92400e;
            margin: 0;
        }
        .alert-success {
            background: #d1fae5;
            border-left: 4px solid #10b981;
        }
        .alert-success p {
            color: #065f46;
            margin: 0;
        }
        .alert-danger {
            background: #fee2e2;
            border-left: 4px solid #ef4444;
        }
        .alert-danger p {
            color: #991b1b;
            margin: 0;
        }
        .alert-info {
            background: #e0f2fe;
            border-left: 4px solid #0ea5e9;
        }
        .alert-info p {
            color: #0c4a6e;
            margin: 0;
        }
        .expiry-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #fef3c7;
            color: #92400e;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin: 16px 0;
        }
        .link-box {
            background: #f1f5f9;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            word-break: break-all;
        }
        .link-box code {
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 12px;
            color: #475569;
        }
        .list {
            margin: 20px 0;
            padding-left: 0;
            list-style: none;
        }
        .list li {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 10px 0;
            color: #4a5568;
            font-size: 15px;
        }
        .list li .check {
            width: 20px;
            height: 20px;
            background: #d1fae5;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            color: #10b981;
            font-size: 12px;
        }
        .divider {
            height: 1px;
            background: #e2e8f0;
            margin: 24px 0;
        }
        .footer {
            background: #f8fafc;
            padding: 24px 40px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }
        .footer p {
            color: #94a3b8;
            font-size: 13px;
            margin: 4px 0;
        }
        .footer .brand {
            font-weight: 600;
            color: #64748b;
        }
        .social-links {
            margin: 16px 0;
        }
        .social-links a {
            display: inline-block;
            margin: 0 8px;
            color: #94a3b8;
            text-decoration: none;
        }
        @media only screen and (max-width: 600px) {
            .wrapper {
                padding: 20px 12px;
            }
            .header {
                padding: 24px 20px;
            }
            .content {
                padding: 24px 20px;
            }
            .footer {
                padding: 20px;
            }
            .code-box .code {
                font-size: 24px;
                letter-spacing: 4px;
            }
        }
    """
