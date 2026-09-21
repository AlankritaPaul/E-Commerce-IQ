import os

icons_dir = os.path.join("docs", "images", "icons")
os.makedirs(icons_dir, exist_ok=True)

svgs = {
    "core_concepts.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#1D4ED8"/>
  <path d="M8 10L5 13L8 16M16 10L19 13L16 16M13.5 8L10.5 18" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "capabilities.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#7C3AED"/>
  <path d="M12 4L14.2 9.2L19.5 9.6L15.4 13.2L16.6 18.5L12 15.6L7.4 18.5L8.6 13.2L4.5 9.6L9.8 9.2L12 4Z" fill="white"/>
</svg>""",

    "architecture.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#0D9488"/>
  <rect x="4" y="5" width="16" height="4" rx="1.5" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
  <rect x="4" y="11" width="7" height="8" rx="1.5" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
  <rect x="13" y="11" width="7" height="8" rx="1.5" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
</svg>""",

    "sql_engine.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#2563EB"/>
  <ellipse cx="12" cy="7" rx="6.5" ry="2.5" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
  <path d="M5.5 7V12C5.5 13.4 8.4 14.5 12 14.5C15.6 14.5 18.5 13.4 18.5 12V7" stroke="white" stroke-width="1.6"/>
  <path d="M5.5 12V17C5.5 18.4 8.4 19.5 12 19.5C15.6 19.5 18.5 18.4 18.5 17V12" stroke="white" stroke-width="1.6"/>
</svg>""",

    "tech_stack.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#4F46E5"/>
  <path d="M12 4L4 8L12 12L20 8L12 4Z" stroke="white" stroke-width="1.6" stroke-linejoin="round" fill="rgba(255,255,255,0.2)"/>
  <path d="M4 12L12 16L20 12" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M4 16L12 20L20 16" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "directory.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#D97706"/>
  <path d="M4 7C4 5.9 4.9 5 6 5H9.5L11.5 7.5H18C19.1 7.5 20 8.4 20 9.5V17C20 18.1 19.1 19 18 19H6C4.9 19 4 18.1 4 17V7Z" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
</svg>""",

    "roadmap.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#059669"/>
  <path d="M6 5V19M6 6H16L13.5 10L16 14H6" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="rgba(255,255,255,0.2)"/>
</svg>""",

    "getting_started.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#DB2777"/>
  <circle cx="12" cy="12" r="7.5" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
  <polygon points="10.5,8.5 16,12 10.5,15.5" fill="white"/>
</svg>""",

    "license.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect width="24" height="24" rx="6" fill="#475569"/>
  <path d="M6 6C6 4.9 6.9 4 8 4H16C17.1 4 18 4.9 18 6V18C18 19.1 17.1 20 16 20H8C6.9 20 6 19.1 6 18V6Z" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.2)"/>
  <path d="M9 8H15M9 11H15M9 14H13" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",

    # Subtopics - Capabilities
    "sales_revenue.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#10B981"/>
  <path d="M12 6V18M14.5 9.5C14.5 8.1 13.4 7 12 7H10C8.9 7 8 7.9 8 9C8 10.1 8.9 11 10 11H14C15.1 11 16 11.9 16 13C16 14.1 15.1 15 14 15H10C8.6 15 7.5 13.9 7.5 12.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "products.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#F97316"/>
  <path d="M6.5 8.5L12 5.5L17.5 8.5V15.5L12 18.5L6.5 15.5V8.5Z" stroke="white" stroke-width="1.6" stroke-linejoin="round" fill="rgba(255,255,255,0.25)"/>
  <path d="M6.5 8.5L12 12L17.5 8.5M12 12V18.5" stroke="white" stroke-width="1.6"/>
</svg>""",

    "customers.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#3B82F6"/>
  <circle cx="12" cy="9" r="3" fill="white"/>
  <path d="M6.5 18C6.5 15 8.8 13.5 12 13.5C15.2 13.5 17.5 15 17.5 18" stroke="white" stroke-width="1.8" stroke-linecap="round" fill="rgba(255,255,255,0.25)"/>
</svg>""",

    "reviews_sentiment.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#F59E0B"/>
  <path d="M12 6.5L13.6 9.8L17.2 10.3L14.6 12.8L15.2 16.4L12 14.7L8.8 16.4L9.4 12.8L6.8 10.3L10.4 9.8L12 6.5Z" fill="white"/>
</svg>""",

    "returns_refunds.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#EF4444"/>
  <path d="M8 9H4M4 9V5M4 9L8.5 4.5C10.4 2.6 13.5 2.6 15.4 4.5C17.3 6.4 17.3 9.5 15.4 11.4L13.5 13.3" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M16 15H20M20 15V19M20 15L15.5 19.5C13.6 21.4 10.5 21.4 8.6 19.5C6.7 17.6 6.7 14.5 8.6 12.6L10.5 10.7" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "time_series.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#8B5CF6"/>
  <path d="M6 16L10 11L13.5 14L18 8" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="18" cy="8" r="1.5" fill="white"/>
</svg>""",

    "ai_copilot.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#6366F1"/>
  <path d="M12 6V9M12 15V18M6 12H9M15 12H18M7.8 7.8L9.9 9.9M14.1 14.1L16.2 16.2M7.8 16.2L9.9 14.1M14.1 9.9L16.2 7.8" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
  <circle cx="12" cy="12" r="2.5" fill="white"/>
</svg>""",

    # Subtopics - SQL
    "schema_model.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#0284C7"/>
  <rect x="6" y="6" width="12" height="12" rx="2" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <line x1="6" y1="10" x2="18" y2="10" stroke="white" stroke-width="1.5"/>
  <line x1="11" y1="10" x2="11" y2="18" stroke="white" stroke-width="1.5"/>
</svg>""",

    "query_gateway.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#D97706"/>
  <path d="M13 5L6 14H12L11 19L18 10H12L13 5Z" fill="white"/>
</svg>""",

    "kpis_metrics.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#059669"/>
  <rect x="6" y="13" width="3" height="6" rx="1" fill="white"/>
  <rect x="10.5" y="9" width="3" height="10" rx="1" fill="white"/>
  <rect x="15" y="5" width="3" height="14" rx="1" fill="white"/>
</svg>""",

    "sku_economics.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#EA580C"/>
  <path d="M7 6H11L18 13L14 17L7 10V6Z" stroke="white" stroke-width="1.6" stroke-linejoin="round" fill="rgba(255,255,255,0.2)"/>
  <circle cx="9.5" cy="8.5" r="1" fill="white"/>
</svg>""",

    "customer_rfm.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#7C3AED"/>
  <circle cx="12" cy="12" r="7" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <circle cx="12" cy="12" r="4" stroke="white" stroke-width="1.5"/>
  <circle cx="12" cy="12" r="1.5" fill="white"/>
</svg>""",

    "leakage_tracking.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#DC2626"/>
  <path d="M12 5V15M12 15L9 12M12 15L15 12" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6 18H18" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "text_to_sql.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#4F46E5"/>
  <path d="M6 8C6 6.9 6.9 6 8 6H16C17.1 6 18 6.9 18 8V13C18 14.1 17.1 15 16 15H11L7 18V15H8C6.9 15 6 14.1 6 13V8Z" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <path d="M10 9.5L9 11L10 12.5M14 9.5L15 11L14 12.5" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "security_shield.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#1E3A8A"/>
  <path d="M12 5L6 7.5V12C6 15.5 8.5 18.7 12 19.5C15.5 18.7 18 15.5 18 12V7.5L12 5Z" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.25)"/>
  <path d="M10 12L11.5 13.5L14.5 10.5" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    # Subtopics - Getting Started
    "prerequisites.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#0D9488"/>
  <path d="M9 6H7C6.4 6 6 6.4 6 7V17C6 17.6 6.4 18 7 18H17C17.6 18 18 17.6 18 17V7C18 6.4 17.6 6 17 6H15" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <rect x="9" y="4" width="6" height="3" rx="1" stroke="white" stroke-width="1.5" fill="#0D9488"/>
  <path d="M9 11L11 13L15 9" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "terminal_setup.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#334155"/>
  <rect x="5" y="6" width="14" height="12" rx="2" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <path d="M8 10L10.5 12L8 14M12 14H15" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "config_key.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#CA8A04"/>
  <circle cx="9" cy="12" r="3.5" stroke="white" stroke-width="1.5" fill="rgba(255,255,255,0.2)"/>
  <path d="M12.5 12H18.5M16 12V14.5M18.5 12V14.5" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",

    "play_run.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
  <circle cx="12" cy="12" r="10" fill="#16A34A"/>
  <polygon points="10,8 16,12 10,16" fill="white"/>
</svg>"""
}

for name, content in svgs.items():
    filepath = os.path.join(icons_dir, name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully wrote {len(svgs)} SVG icons to {icons_dir}")
