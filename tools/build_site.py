#!/usr/bin/env python3
"""Generate the Country Roads Cleaning Solutions static site.

Re-run from the repo root:

    python3 tools/build_site.py

HTML under the site root is overwritten. CNAME is never touched.
"""

from __future__ import annotations

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://countryroadscleaningsolutions.com"
PHONE = "(304) 710-5430"
TEL = "tel:+13047105430"
EMAIL = "countryroadscleaningsolutions@gmail.com"
QUOTE_PATH = "/quote/"
BUSINESS_ID = f"{BASE}/#business"
WEBSITE_ID = f"{BASE}/#website"
GSC = "MBFMHKZPEH1q2RIueenmKA9H5wVpUnKhdF_wFM3hnpw"
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'

# Description A, with the sentence that names an owner removed.
ABOUT = (
    "Country Roads Cleaning Solutions is a locally owned house cleaning service based in Kenova, WV, "
    "cleaning homes in Kenova, Ceredo, Huntington and across the Tri-State. We offer standard house cleaning, "
    "deep cleaning and move-in/move-out cleaning, one time or on a weekly, every-two-weeks or monthly schedule. "
    "Kitchens, bathrooms, floors, dusting and the buildup that keeps coming back are all covered, and we're pet friendly. "
    "We also clean offices and small businesses. We're licensed and insured. Our team has years of experience cleaning "
    "homes in the area. Tell us about your home or business and how often you'd like help, and we'll recommend a "
    "cleaning plan and send a free quote."
)

TOWNS = [
    ("Huntington", "WV", "West Virginia"),
    ("Ashland", "KY", "Kentucky"),
    ("Kenova", "WV", "West Virginia"),
    ("Ironton", "OH", "Ohio"),
    ("Flatwoods", "KY", "Kentucky"),
    ("Barboursville", "WV", "West Virginia"),
    ("South Point", "OH", "Ohio"),
    ("Russell", "KY", "Kentucky"),
    ("Ceredo", "WV", "West Virginia"),
    ("Catlettsburg", "KY", "Kentucky"),
    ("Milton", "WV", "West Virginia"),
    ("Grayson", "KY", "Kentucky"),
    ("Raceland", "KY", "Kentucky"),
    ("Coal Grove", "OH", "Ohio"),
    ("Lavalette", "WV", "West Virginia"),
    ("Wayne", "WV", "West Virginia"),
    ("Chesapeake", "OH", "Ohio"),
    ("Proctorville", "OH", "Ohio"),
    ("Burlington", "OH", "Ohio"),
    ("Greenup", "KY", "Kentucky"),
]

TOWN_LINKS = {
    "Huntington": "/huntington-wv-house-cleaning/",
    "Ashland": "/ashland-ky-house-cleaning/",
    "Ironton": "/ironton-oh-house-cleaning/",
    "Kenova": "/kenova-ceredo-house-cleaning/",
    "Ceredo": "/kenova-ceredo-house-cleaning/",
    "Barboursville": "/barboursville-wv-house-cleaning/",
    "Milton": "/barboursville-wv-house-cleaning/#milton",
    "Lavalette": "/barboursville-wv-house-cleaning/#lavalette",
}

SERVICES = [
    {
        "id": "standard",
        "name": "Standard House Cleaning",
        "page": "/house-cleaning/",
        "description": "Regular house cleaning for homes in Kenova, Huntington and the Tri-State. We clean kitchens and bathrooms, dust, vacuum and mop floors, and take care of the everyday buildup so the house stays under control. Available one time or weekly, every two weeks or monthly.",
    },
    {
        "id": "deep",
        "name": "Deep Cleaning",
        "page": "/deep-cleaning/",
        "description": "A top-to-bottom clean for homes that have fallen behind or need a reset: built-up grime in kitchens and bathrooms, baseboards, hard-to-reach spots, pet hair and dust. A good first visit before recurring service. Serving Kenova, Ceredo, Huntington and nearby Tri-State towns.",
    },
    {
        "id": "movein",
        "name": "Move-In Cleaning",
        "page": "/move-in-move-out-cleaning/",
        "description": "Start fresh in your new place. We clean the home before you unpack: kitchen, cabinets, bathrooms, floors and the corners the last owners missed. Serving Kenova, Huntington and the Tri-State. Tell us the move date when you request your quote.",
    },
    {
        "id": "moveout",
        "name": "Move-Out Cleaning",
        "page": "/move-in-move-out-cleaning/",
        "description": "Leaving a rental or selling a home? We clean it top to bottom after the boxes are out so it is ready for the walkthrough, the landlord or the next owner. Serving Kenova, Ceredo, Huntington and nearby West Virginia, Kentucky and Ohio towns.",
    },
    {
        "id": "recurring",
        "name": "Recurring House Cleaning (Weekly, Biweekly, Monthly)",
        "page": "/house-cleaning/",
        "description": "Stay caught up instead of catching up. Pick weekly, every-two-weeks or monthly visits and we keep your kitchen, bathrooms, floors and dusting on track. A popular choice for busy families in Kenova, Huntington and the Tri-State who want their weekends back.",
    },
    {
        "id": "onetime",
        "name": "One-Time House Cleaning",
        "page": "/house-cleaning/",
        "description": "Need help just once? Before guests, after a busy stretch, or ahead of a holiday, we'll clean the areas that need it most. No ongoing commitment required. Serving homes in Kenova, Ceredo, Huntington and the Tri-State area.",
    },
    {
        "id": "pets",
        "name": "Pet-Friendly House Cleaning",
        "page": "/house-cleaning/",
        "description": "We work around dogs and cats and pay extra attention to pet hair, nose prints on glass and dusty corners. Tell us about your pets and any areas that need extra attention when you request a quote. Serving Kenova, Huntington and the Tri-State.",
    },
    {
        "id": "apartment",
        "name": "Apartment & Condo Cleaning",
        "page": "/apartment-condo-cleaning/",
        "description": "Cleaning for apartments, condos and smaller homes in Huntington, Kenova and Ceredo, one time or on a recurring schedule. Kitchens, bathrooms, floors and dusting, sized to your space. Pricing depends on size and condition, so call for a quote.",
    },
    {
        "id": "holiday",
        "name": "Holiday & Guest-Ready Cleaning",
        "page": "/holiday-cleaning/",
        "description": "Hosting Thanksgiving, Christmas or family visiting? We get the kitchen, bathrooms, guest rooms and living areas ready before company arrives, and can come back after. Serving Kenova, Huntington and the Tri-State. Pricing varies by home, so call for a quote.",
    },
    {
        "id": "airbnb",
        "name": "Rental & Airbnb Turnover Cleaning",
        "page": "/airbnb-turnover-cleaning/",
        "description": "Turnover cleaning between guests or tenants for short-term rentals and rental homes in Huntington, Kenova and the Tri-State. Kitchens, bathrooms, floors and a full reset for the next check-in. Pricing depends on the property and schedule, so call for a quote.",
    },
    {
        "id": "laundry",
        "name": "Laundry & Linen Change Add-On",
        "page": "/house-cleaning/#laundry",
        "description": "Add laundry or a bed linen change to your house cleaning visit. We wash, dry and fold a load, or strip and remake beds, so you come home to a fresh bedroom. Available in Kenova, Huntington and the Tri-State. Pricing varies, so call for a quote.",
    },
    {
        "id": "commercial",
        "name": "Commercial & Office Cleaning",
        "page": "/commercial-cleaning/",
        "description": "Commercial cleaning for offices, storefronts and small businesses in Kenova, Ceredo, Huntington and the Tri-State: restrooms, break rooms, floors, dusting and trash, on a schedule that works around your hours. Every space is different, so call for a quote.",
    },
]
SERVICE_BY_ID = {item["id"]: item for item in SERVICES}

FAQ_HOME = [
    (
        "What areas do you serve?",
        "We're based in Kenova, WV and clean homes and businesses within about 25 miles, including Huntington, Ceredo, Barboursville, Wayne and Milton in West Virginia; Ashland, Catlettsburg, Russell, Flatwoods and Grayson in Kentucky; and Ironton, South Point, Chesapeake and Proctorville in Ohio. Not sure if you're in our area? Call or text (304) 710-5430 or send us your ZIP code on our quote form.",
    ),
    (
        "What types of cleaning do you offer?",
        "Standard house cleaning, deep cleaning, and move-in/move-out cleaning, one time or weekly, every two weeks or monthly. We also do apartment and condo cleaning, holiday and guest-ready cleaning, rental and Airbnb turnovers, laundry and linen add-ons, and commercial cleaning for offices and small businesses. Call for a quote on those.",
    ),
    (
        "How do I get a price?",
        "Request a quote with your ZIP code, number of bedrooms and bathrooms, and the type of cleaning you need, and we'll get back to you with a recommendation and a quote. You can also call or text (304) 710-5430.",
    ),
    (
        "Are you pet friendly?",
        "Yes! Let us know about your pets and any areas that need extra attention when you request your quote.",
    ),
    (
        "Do I need to be home during the cleaning?",
        "We work directly with each customer to arrange keys or home access. Please don't send door codes through the website form; call or text (304) 710-5430 and we'll set it up with you.",
    ),
    (
        "Do you bring your own supplies?",
        "Yes, we bring our own supplies and equipment. If you'd like us to use a specific product in your home, just let us know.",
    ),
    (
        "Are you licensed and insured?",
        "Yes, Country Roads Cleaning Solutions is licensed and insured.",
    ),
    (
        "Do you clean offices or businesses?",
        "Yes, we offer commercial cleaning for offices, storefronts and small businesses in Kenova, Ceredo, Huntington and the Tri-State. Every space is different, so call or text (304) 710-5430 for a quote.",
    ),
    (
        "What forms of payment do you accept?",
        "We accept all forms of payment. Just let us know what works best for you when we confirm your cleaning.",
    ),
    (
        "What are your hours?",
        "Monday through Friday, 8 AM to 5 PM. We're closed Saturday and Sunday.",
    ),
]

NAV = [
    ("/house-cleaning/", "House cleaning"),
    ("/deep-cleaning/", "Deep cleaning"),
    ("/move-in-move-out-cleaning/", "Move-in / out"),
    ("/airbnb-turnover-cleaning/", "Airbnb turnover"),
    ("/apartment-condo-cleaning/", "Apartments"),
    ("/commercial-cleaning/", "Commercial"),
    ("/office-cleaning-huntington-wv/", "Huntington offices"),
    ("/holiday-cleaning/", "Holiday"),
    ("/huntington-wv-house-cleaning/", "Huntington"),
    ("/barboursville-wv-house-cleaning/", "Barboursville"),
    ("/ashland-ky-house-cleaning/", "Ashland"),
    ("/ironton-oh-house-cleaning/", "Ironton"),
    ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"),
]

REVIEWS = [
    ("Missy", "Facebook recommendation", "Excellent service. Easy to work with. Very pet friendly."),
    (
        "Ryen",
        "Customer review",
        "Very professional, dependable, and paid attention to every little detail. Also friendly, efficient, and clearly takes pride in their work. If you're looking for someone you can trust to do an incredible job, this is the company to call. I'll definitely be using them again! 10/10 from me!",
    ),
    ("Lela", "Customer review", "Friendly and professional. Always goes above and beyond. Reasonable prices."),
    (
        "Jessica",
        "Customer review",
        "I own a cleaning company myself, so I know how important it is to find a team that's reliable and does quality work. This company is efficient, dependable, and always goes above and beyond. Whenever my schedule is completely booked, I confidently recommend them to my clients because I know they'll be in great hands. Highly recommend!",
    ),
    (
        "Telisha",
        "Customer review",
        "I had a wonderful experience with the Housing Cleaning and Laundry team. They consistently went above and beyond to keep everything clean, organized, and welcoming. Their attention to detail, professionalism, and hard work did not go unnoticed. They were always friendly, dependable, and took pride in what they do. Their efforts truly made a positive difference, and I appreciate everything they did. Thank you for providing such excellent service!",
    ),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def linkify(value: str) -> str:
    text = esc(value)
    text = text.replace(PHONE, f'<a href="{TEL}">{PHONE}</a>')
    text = text.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
    return text


def official(service_id: str) -> str:
    service = SERVICE_BY_ID[service_id]
    return f'<p class="official">{esc(service["description"])}</p>'


def fill_tokens(body: str) -> str:
    for service_id in SERVICE_BY_ID:
        body = body.replace(f"@@{service_id}@@", official(service_id))
    return body


def how_we_work() -> str:
    return f"""
    <h2>How a visit works</h2>
    <p>We're licensed and insured, and we bring our own supplies and equipment. If you want a particular product used in your home, tell us when you request the quote. We accept all forms of payment. Say what you prefer when we confirm the cleaning.</p>
    <p>You don't have to be home. We arrange keys or other access with you directly. Please don't put a door code in the website form. Call or text <a href="{TEL}">{PHONE}</a> and we'll set it up with you.</p>
    <p>Country Roads Cleaning Solutions is women-owned and based in Kenova, West Virginia. You can reach us Monday through Friday, 8:00 AM to 5:00 PM. We're closed Saturday and Sunday.</p>
    """


def related(links: list[tuple[str, str]]) -> str:
    items = "".join(f'<a href="{href}">{esc(label)}</a>' for href, label in links)
    return f'<h2>Related pages</h2><div class="related">{items}</div>'


FAQ_CHEVRON = '<svg class="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6"/></svg>'


def faq_html(faqs: list[tuple[str, str]], heading: str) -> str:
    items = []
    for question, answer in faqs:
        items.append(
            f'<details class="faq-item"><summary><h3>{esc(question)}</h3>{FAQ_CHEVRON}</summary><p>{linkify(answer)}</p></details>'
        )
    return (
        f'<section class="faq-section" id="faq"><div class="wrap prose"><h2>{esc(heading)}</h2>'
        + "".join(items)
        + "</div></section>"
    )


def photo(name: str, widths: list[int], size: tuple[int, int], alt: str, sizes: str, lazy: bool = True, *, priority: bool = True) -> str:
    srcset = ", ".join(f"/assets/photos/{name}-{width}.webp {width}w" for width in widths)
    if lazy:
        loading = 'loading="lazy" decoding="async"'
    elif priority:
        loading = 'fetchpriority="high" decoding="async"'
    else:
        loading = 'decoding="async"'
    width, height = size
    return (
        f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
        f'<img src="/assets/photos/{name}-{widths[-1]}.jpg" width="{width}" height="{height}" alt="{esc(alt)}" {loading}></picture>'
    )


def area_served_nodes() -> list[dict]:
    nodes = []
    for name, _region, state in TOWNS:
        nodes.append({
            "@type": "City",
            "name": name,
            "containedInPlace": {"@type": "State", "name": state},
        })
    return nodes


def business_node() -> dict:
    return {
        "@type": ["HouseCleaner", "LocalBusiness"],
        "sameAs": [GBP_URL],
        "@id": BUSINESS_ID,
        "name": "Country Roads Cleaning Solutions",
        "legalName": "Country Roads Cleaning Solutions, LLC",
        "description": ABOUT,
        "url": f"{BASE}/",
        "telephone": "+1-304-710-5430",
        "email": EMAIL,
        "image": {
            "@type": "ImageObject",
            "url": f"{BASE}/assets/photos/living-room-960.webp",
            "width": 960,
            "height": 1280,
        },
        "logo": {
            "@type": "ImageObject",
            "url": f"{BASE}/assets/brand/logo.webp",
            "width": 300,
            "height": 300,
        },
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Kenova",
            "addressRegion": "WV",
            "postalCode": "25530",
            "addressCountry": "US",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 38.4022,
            "longitude": -82.5821,
        },
        "areaServed": area_served_nodes(),
        "openingHours": "Mo-Fr 08:00-17:00",
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "08:00",
            "closes": "17:00",
        }],
        "currenciesAccepted": "USD",
        "paymentAccepted": "All forms of payment",
        "foundingDate": "2026-09",
        "slogan": "A little less on your to-do list.",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Cleaning services",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": service["name"],
                        "description": service["description"],
                        "url": BASE + service["page"],
                        "provider": {"@id": BUSINESS_ID},
                    },
                }
                for service in SERVICES
            ],
        },
    }


def graph_for(page: dict) -> dict:
    canonical = BASE + page["path"]
    graph = [
        business_node(),
        {
            "@type": "WebSite",
            "@id": WEBSITE_ID,
            "url": f"{BASE}/",
            "name": "Country Roads Cleaning Solutions",
            "publisher": {"@id": BUSINESS_ID},
        },
        {
            "@type": "WebPage",
            "@id": canonical + "#webpage",
            "url": canonical,
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": WEBSITE_ID},
            "about": {"@id": BUSINESS_ID},
            "inLanguage": "en-US",
        },
    ]
    if page["path"] != "/":
        crumbs = [("Home", "/")] + page.get("crumbs", [])
        graph.append({
            "@type": "BreadcrumbList",
            "@id": canonical + "#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "name": label,
                    "item": BASE + href,
                }
                for index, (label, href) in enumerate(crumbs)
            ],
        })
    for service_id in page.get("service_ids", []):
        service = SERVICE_BY_ID[service_id]
        graph.append({
            "@type": "Service",
            "@id": canonical + f"#{service_id}",
            "name": service["name"],
            "serviceType": service["name"],
            "description": service["description"],
            "url": BASE + service["page"].split("#")[0],
            "provider": {"@id": BUSINESS_ID},
            "areaServed": area_served_nodes(),
        })
    if page.get("service_sentence"):
        graph.append({
            "@type": "Service",
            "@id": canonical + "#local-service",
            "name": page["service_name"],
            "serviceType": page.get("service_type", "House cleaning"),
            "description": page["service_sentence"],
            "url": canonical,
            "provider": {"@id": BUSINESS_ID},
            "areaServed": page["area_served"],
        })
    if page.get("faqs"):
        graph.append({
            "@type": "FAQPage",
            "@id": canonical + "#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in page["faqs"]
            ],
        })
    return {"@context": "https://schema.org", "@graph": graph}


GBP_URL = "https://www.google.com/maps?cid=7570965002888918614"
REVIEW_URL = "https://g.page/r/CVa2G7SOeBFpEBM/review"


def json_ld(page: dict) -> str:
    payload = json.dumps(graph_for(page), ensure_ascii=False, indent=2)
    return (
        "<!-- TODO(owner): add the Facebook page to sameAs after it is renamed to Country Roads Cleaning Solutions:\n"
        "     https://www.facebook.com/profile.php?id=61592053743546 -->\n"
        f'<script type="application/ld+json">\n{payload}\n</script>'
    )


def head(page: dict) -> str:
    canonical = BASE + page["path"]
    robots = '<meta name="robots" content="noindex">' if page.get("noindex") else ""
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#214A3C">
  <meta name="google-site-verification" content="{GSC}" />
  <title>{esc(page["title"])}</title>
  <meta name="description" content="{esc(page["description"])}">
  <link rel="canonical" href="{canonical}">
  {robots}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Country Roads Cleaning Solutions">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{esc(page["title"])}">
  <meta property="og:description" content="{esc(page["description"])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE}/assets/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Country Roads Cleaning Solutions logo. House cleaning in Kenova, Huntington, and the Tri-State.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(page["title"])}">
  <meta name="twitter:description" content="{esc(page["description"])}">
  <meta name="twitter:image" content="{BASE}/assets/og.jpg">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Source+Sans+3:wght@400;600;700&display=swap">
  <link rel="stylesheet" href="/css/site.css">
  {json_ld(page)}
</head>"""


def header(current: str) -> str:
    links = []
    for href, label in NAV:
        current_attr = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{href}"{current_attr}>{esc(label)}</a>')
    return f"""
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/">
        <picture>
          <source type="image/webp" srcset="/assets/brand/logo.webp">
          <img src="/assets/brand/logo.png" width="300" height="300" alt="Country Roads Cleaning Solutions logo">
        </picture>
        <span class="brand-name">Country Roads <small>Cleaning Solutions</small></span>
      </a>
      <div class="header-actions">
        <a class="header-phone" href="{TEL}"><span class="sr-only">Call </span>{PHONE}</a>
        <a class="button small" href="{QUOTE_PATH}">Get a quote {ARROW}</a>
      </div>
      <nav class="primary-nav" aria-label="Primary">{''.join(links)}</nav>
    </div>
  </header>"""


def footer(include_about: bool) -> str:
    service_links = [
        '<li><a href="/house-cleaning/">Standard and recurring house cleaning</a></li>',
        '<li><a href="/deep-cleaning/">Deep cleaning</a></li>',
        '<li><a href="/move-in-move-out-cleaning/">Move-in and move-out cleaning</a></li>',
        '<li><a href="/airbnb-turnover-cleaning/">Airbnb and rental turnover</a></li>',
        '<li><a href="/apartment-condo-cleaning/">Apartment and condo cleaning</a></li>',
        '<li><a href="/commercial-cleaning/">Commercial and office cleaning</a></li>',
        '<li><a href="/office-cleaning-huntington-wv/">Office cleaning in Huntington</a></li>',
        '<li><a href="/holiday-cleaning/">Holiday and guest-ready cleaning</a></li>',
        '<li><a href="/house-cleaning/#laundry">Laundry and linen add-on</a></li>',
    ]
    area_links = [
        '<li><a href="/huntington-wv-house-cleaning/">Huntington, WV</a></li>',
        '<li><a href="/barboursville-wv-house-cleaning/">Barboursville, WV</a></li>',
        '<li><a href="/ashland-ky-house-cleaning/">Ashland, KY</a></li>',
        '<li><a href="/ironton-oh-house-cleaning/">Ironton, OH</a></li>',
        '<li><a href="/kenova-ceredo-house-cleaning/">Kenova &amp; Ceredo, WV</a></li>',
        "<li>And Wayne, <a href=\"/barboursville-wv-house-cleaning/#milton\">Milton</a>, <a href=\"/barboursville-wv-house-cleaning/#lavalette\">Lavalette</a>, Flatwoods, Russell, Catlettsburg, Grayson, Raceland, Greenup, South Point, Coal Grove, Chesapeake, Proctorville, and Burlington.</li>",
    ]
    about = f'<p class="footer-about">{linkify(ABOUT)}</p>' if include_about else ""
    return f"""
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div class="footer-about-col">
        <p class="footer-brand">Country Roads Cleaning Solutions</p>
        {about}
        <p class="footer-meta">Women-owned house cleaning based in Kenova, WV 25530. Serving the Huntington Tri-State — not the Morgantown company with a similar name.</p>
        <p class="footer-meta"><a href="{TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p class="footer-meta">Monday–Friday, 8:00 AM–5:00 PM. Closed Saturday and Sunday.</p>
      </div>
      <div>
        <p class="footer-heading">Services</p>
        <ul>{''.join(service_links)}</ul>
      </div>
      <div>
        <p class="footer-heading">Service area</p>
        <ul>{''.join(area_links)}</ul>
      </div>
    </div>
    <div class="wrap footer-links">
      <button id="privacy-open" type="button">Privacy</button>
      <a href="{QUOTE_PATH}">Request a quote</a>
      <a href="{GBP_URL}" target="_blank" rel="noopener noreferrer">Google reviews</a>
      <a href="{REVIEW_URL}" target="_blank" rel="noopener noreferrer">Leave a review</a>
      <a href="https://www.facebook.com/profile.php?id=61592053743546" target="_blank" rel="noopener noreferrer">Facebook</a>
      <a href="#top">Back to top</a>
      <span>© <span id="copyright-year">2026</span> Country Roads Cleaning Solutions</span>
    </div>
  </footer>"""


def privacy_dialog() -> str:
    return f"""
  <dialog class="privacy-dialog" id="privacy-dialog" aria-labelledby="privacy-title">
    <button class="dialog-close" type="button" aria-label="Close privacy notice" data-close="privacy-dialog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg></button>
    <h2 id="privacy-title">Your quote request and privacy</h2>
    <p>When you request a quote, you share your name, ZIP code, home details, cleaning preferences, contact details, and any note you choose to include. Country Roads Cleaning Solutions uses these details to respond to your inquiry and discuss cleaning services with you.</p>
    <p>The quote form is delivered through FormSubmit, a third-party form service. It processes form information and spam verification according to its <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">privacy policy</a>. If campaign details are in the page address, they are included with your inquiry so we can see how you found us.</p>
    <p>Please leave out sensitive information such as payment details, alarm codes, and door codes. Call or text <a href="{TEL}">{PHONE}</a> if we need to arrange a key or other access.</p>
  </dialog>"""


def quote_home_fields(prefix: str = "") -> str:
    """Home-detail fields shared by the site quote form and /quote/. Keep labels, names, and options identical."""
    html_ = f"""
                <div class="field"><label for="zip">What's your ZIP code?</label><input id="zip" name="ZIP code" autocomplete="postal-code" inputmode="numeric" placeholder="e.g. 25530" pattern="[0-9]{{5}}(-[0-9]{{4}})?" maxlength="10" title="Enter a 5-digit ZIP code" required></div>
                <div class="field"><label for="bedrooms">How many bedrooms?</label><select id="bedrooms" name="Bedrooms" required><option value="">Choose an option</option><option>0 / Studio</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5+</option><option>Not a home (office or other)</option></select></div>
                <div class="field"><label for="bathrooms">How many bathrooms?</label><select id="bathrooms" name="Bathrooms" required><option value="">Choose an option</option><option>1</option><option>1.5</option><option>2</option><option>2.5</option><option>3</option><option>3.5</option><option>4+</option><option>Not a home (office or other)</option></select></div>
                <div class="field"><label for="square-feet">About how big is the home or space?</label><select id="square-feet" name="Approximate square footage" required><option value="">Choose an option</option><option>Under 1,000 sq ft</option><option>1,000–1,499 sq ft</option><option>1,500–1,999 sq ft</option><option>2,000–2,499 sq ft</option><option>2,500–2,999 sq ft</option><option>3,000–3,999 sq ft</option><option>4,000+ sq ft</option><option>I'm not sure</option></select></div>
                <div class="field"><label for="service-type">What kind of cleaning do you need?</label><select id="service-type" name="Cleaning type" required><option value="">Choose an option</option><option>Standard cleaning</option><option>Deep cleaning</option><option>Move-in / move-out cleaning</option><option>Apartment or condo cleaning</option><option>Rental or Airbnb turnover</option><option>Holiday or guest-ready cleaning</option><option>Commercial or office cleaning</option><option>Help me choose</option></select></div>
                <div class="field"><label for="frequency">How often would you like help?</label><select id="frequency" name="Preferred frequency" required><option value="">Choose an option</option><option>Just once</option><option>Every week</option><option>Every two weeks</option><option>Every month</option><option>I'm not sure yet</option></select></div>"""
    return _prefix_ids(html_.strip("\n"), prefix, ["zip", "bedrooms", "bathrooms", "square-feet", "service-type", "frequency"])


def quote_contact_fields(prefix: str = "") -> str:
    """Contact fields shared by the site quote form and /quote/."""
    html_ = f"""
                <div class="field"><label for="full-name">Your name</label><input id="full-name" name="name" autocomplete="name" placeholder="Your name" required maxlength="100"></div>
                <div class="form-row">
                  <div class="field"><label for="phone">Phone <span class="optional">(or email)</span></label><input id="phone" type="tel" name="phone" autocomplete="tel" placeholder="Your phone number" maxlength="30" aria-describedby="contact-help"></div>
                  <div class="field"><label for="email">Email <span class="optional">(or phone)</span></label><input id="email" type="email" name="email" autocomplete="email" placeholder="Your email address" maxlength="254" aria-describedby="contact-help"></div>
                </div>
                <p class="contact-help" id="contact-help">Add a phone number or email so we can get back to you.</p>
                <div class="field"><label for="cleaning-note">Pets, laundry, or areas needing extra attention? <span class="optional">(optional)</span></label><textarea id="cleaning-note" name="Additional notes" placeholder="For example: two dogs, a linen change, or extra attention in the kitchen." rows="3" maxlength="3000"></textarea></div>"""
    return _prefix_ids(html_.strip("\n"), prefix, ["full-name", "phone", "email", "contact-help", "cleaning-note"])


def _prefix_ids(markup: str, prefix: str, ids: list[str]) -> str:
    if not prefix:
        return markup
    for id_ in ids:
        markup = markup.replace(f'id="{id_}"', f'id="{prefix}{id_}"').replace(f'for="{id_}"', f'for="{prefix}{id_}"').replace(f'aria-describedby="{id_}"', f'aria-describedby="{prefix}{id_}"')
    return markup


def team_figure() -> str:
    return f"""
        <figure class="owner">
          <figcaption>
            <strong>The team behind Country Roads.</strong>
            <span>Years of experience cleaning homes across the Tri-State, from our base in Kenova, West Virginia.</span>
          </figcaption>
          {photo("team", [400], (400, 513), "A member of the Country Roads Cleaning Solutions team", "(max-width: 760px) 92vw, 460px", lazy=True)}
        </figure>"""


def home_carousel() -> str:
    """Photo carousel that replaces the homepage quote form. Not a lightbox trigger."""
    photos = [
        ("carousel-bedroom", (960, 715), "A tidy bedroom with a wooden house-frame bed, hardwood floors, and gray curtains", True),
        ("carousel-bathroom", (960, 1280), "A freshly cleaned bathroom with a navy vanity, patterned tile floor, and a bright window", False),
        ("carousel-hallway", (960, 1286), "A clean hallway with a wood console table, lamp, framed art, and a potted plant", False),
        ("carousel-kitchen", (960, 1280), "A stainless gas range set into a white marble kitchen island", False),
    ]
    total = len(photos)
    prev_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>'
    next_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'
    pause_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5v14M15 5v14"/></svg>'
    slides = []
    dots = []
    for index, (name, size, alt, wide) in enumerate(photos):
        hidden = "" if index == 0 else " hidden"
        wide_class = " is-wide" if wide else ""
        current = ' aria-current="true"' if index == 0 else ""
        slides.append(
            f'<div class="photo-carousel-slide{wide_class}" role="group" aria-roledescription="slide" aria-label="Photo {index + 1} of {total}"{hidden}>'
            + photo(name, [640, 960], size, alt, "(max-width: 760px) 92vw, 540px", lazy=index != 0, priority=False)
            + "</div>"
        )
        dots.append(
            f'<button class="photo-dot" type="button" data-photo-index="{index}" aria-label="Show photo {index + 1} of {total}"{current}></button>'
        )
    return f"""
        <div class="photo-carousel" id="home-carousel" role="region" aria-roledescription="carousel" aria-label="Photos of homes cleaned by Country Roads" tabindex="0">
          <div class="photo-carousel-frame">{''.join(slides)}</div>
          <div class="photo-carousel-bar">
            <button class="review-pause" id="home-carousel-pause" type="button" aria-label="Pause automatic photos">{pause_icon}</button>
            <button class="icon-button" id="home-carousel-prev" type="button" aria-label="Previous home photo">{prev_icon}</button>
            <div class="photo-dots" role="group" aria-label="Choose a photo">{''.join(dots)}</div>
            <span class="review-count" id="home-carousel-count" aria-hidden="true">1 / {total}</span>
            <button class="icon-button" id="home-carousel-next" type="button" aria-label="Next home photo">{next_icon}</button>
          </div>
          <p class="sr-only" id="home-carousel-announcement" aria-live="polite"></p>
        </div>"""


def homepage_quote() -> str:
    """Homepage #quote story. The form lives on /quote/; this side is copy plus photos."""
    return f"""
    <section class="quote-section" id="quote" aria-labelledby="quote-heading">
      <div class="wrap quote-grid">
        <div class="quote-story">
          <p class="eyebrow">Kenova, West Virginia</p>
          <h2 id="quote-heading">Your next free Saturday could look different.</h2>
          <p>You already have plenty on your plate. Let us help with the cleaning.</p>
          <p>Call or text <a href="{TEL}">{PHONE}</a> and tell us a little about the home or business. Then our team can get you a personalized quote.</p>
          <p>Monday–Friday, 8:00 AM–5:00 PM. We serve homes and businesses within about 25 miles of Kenova.</p>
          <div class="quote-cta"><a class="button" href="{QUOTE_PATH}">Get my cleaning quote {ARROW}</a></div>
          {team_figure()}
        </div>
        {home_carousel()}
      </div>
    </section>"""


def quote_form(include_owner: bool) -> str:
    owner = team_figure() if include_owner else ""
    return f"""
    <section class="quote-section" id="quote" aria-labelledby="quote-heading">
      <div class="wrap quote-grid">
        <div class="quote-story">
          <p class="eyebrow">Kenova, West Virginia</p>
          <h2 id="quote-heading">Your next free Saturday could look different.</h2>
          <p>You already have plenty on your plate. Let us help with the cleaning.</p>
          <p>Call or text <a href="{TEL}">{PHONE}</a>, or tell us a little about the home or business. You don't have to figure out the whole plan before asking for a quote.</p>
          <p>Monday–Friday, 8:00 AM–5:00 PM. We serve homes and businesses within about 25 miles of Kenova.</p>
          {owner}
        </div>
        <div class="form-card">
          <div id="form-content">
            <div class="form-label">Let's take cleaning off your plate</div>
            <h3>Get your personalized cleaning quote</h3>
            <p class="form-intro">Answer a few easy questions so we can recommend the right cleaning. Specialty work is quoted by the job. We don't list prices on the site.</p>
            <form class="quote-form" id="quote-form" method="POST" action="#quote" novalidate>
              <p class="quote-progress" id="quote-progress" aria-live="polite">Step 1 of 2 · Your home</p>
              <fieldset class="quote-step" id="home-step">
                <legend>A few quick details about the space</legend>
{quote_home_fields()}
                <button class="button submit-button" id="quote-continue" type="button">Continue to my quote →</button>
              </fieldset>
              <fieldset class="quote-step" id="contact-step" hidden>
                <legend>Where should we send your quote?</legend>
{quote_contact_fields()}
                <div class="honeypot" aria-hidden="true"><label for="website">Leave this field empty</label><input id="website" name="_honey" tabindex="-1" autocomplete="off"></div>
                <input type="hidden" name="_subject" value="New cleaning quote request | Country Roads Cleaning Solutions">
                <input type="hidden" name="_template" value="table">
                <input type="hidden" name="_next" id="form-next" value="">
                <p class="form-status" id="form-status" role="alert" hidden></p>
                <button class="button submit-button" id="form-submit" type="submit" disabled>Request My Cleaning Quote {ARROW}</button>
                <noscript><p class="form-status">Please enable JavaScript to request a quote through this form, or call {PHONE}.</p></noscript>
                <p class="form-footnote">We'll use your contact details only to follow up about this cleaning quote.</p>
                <button class="quote-back" id="quote-back" type="button">← Back to home details</button>
              </fieldset>
            </form>
          </div>
          <div class="form-success" id="form-success" role="status" hidden>
            <div class="success-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg></div>
            <div class="form-label">One step closer to a cleaner home</div>
            <h3>Thank you for reaching out.</h3>
            <p>Your cleaning quote request has been submitted. We'll use the contact details you provided to follow up about what you need.</p>
            <button type="button" id="new-request">Request another quote</button>
          </div>
        </div>
      </div>
    </section>"""


def mobile_cta() -> str:
    return f'<div class="mobile-cta" id="mobile-cta"><a class="button" href="{QUOTE_PATH}">Get my cleaning quote {ARROW}</a></div>'


def photo_dialog() -> str:
    return """
  <dialog class="photo-dialog" id="photo-dialog" aria-label="Home photo viewer">
    <div class="photo-dialog-inner">
      <button class="dialog-close" type="button" aria-label="Close photo viewer" data-close="photo-dialog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg></button>
      <img id="lightbox-image" alt="">
      <div class="photo-dialog-footer"><span id="lightbox-caption"></span><div class="review-controls"><button class="icon-button" type="button" id="photo-prev" aria-label="Previous home photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg></button><button class="icon-button" type="button" id="photo-next" aria-label="Next home photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button></div></div>
    </div>
  </dialog>"""


def crumbs_html(crumbs: list[tuple[str, str]]) -> str:
    parts = ['<a href="/">Home</a>']
    for label, href in crumbs[:-1]:
        parts.append(f'<a href="{href}">{esc(label)}</a>')
    if crumbs:
        parts.append(esc(crumbs[-1][0]))
    return '<p class="crumbs">' + " / ".join(parts) + "</p>"


def page_hero(page: dict) -> str:
    buttons = f"""
      <div class="hero-cta" id="hero-cta">
        <a class="button" href="{TEL}">Call {PHONE}</a>
        <a class="button ghost" href="{QUOTE_PATH}">Request a quote {ARROW}</a>
      </div>
      <p class="cta-note">Monday–Friday, 8:00 AM–5:00 PM. Women-owned, licensed, and insured. Based in Kenova, WV.</p>"""
    return f"""
    <section class="page-hero">
      <div class="wrap prose">
        {crumbs_html(page.get("crumbs", []))}
        <p class="eyebrow">{esc(page["eyebrow"])}</p>
        <h1>{esc(page["h1"])}</h1>
        <p class="lede">{page["lede"]}</p>
        {buttons}
      </div>
    </section>"""


def document(page: dict, main: str, include_about_in_footer: bool, dialogs: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en" id="top">
{head(page)}
<body>
{header(page["path"] if not page["path"].endswith(".html") else "/")}
<main id="main">
{main}
</main>
{footer(include_about_in_footer)}
{mobile_cta()}
{dialogs}
<script src="/js/site.js" defer></script>
</body>
</html>
"""


def reviews_html() -> str:
    slides = []
    for index, (name, source, text) in enumerate(REVIEWS):
        hidden = "" if index == 0 else " hidden"
        slides.append(
            f'<div class="review-slide" data-name="{esc(name)}" data-source="{esc(source)}" role="group" aria-roledescription="slide" aria-label="Review {index + 1} of {len(REVIEWS)}"{hidden}>'
            f'<blockquote class="review-body">“{esc(text)}”</blockquote></div>'
        )
    return f"""
    <div class="reviews" id="review-carousel" role="region" aria-roledescription="carousel" aria-label="Customer reviews" tabindex="0">
      <div class="review-top"><span class="stars" aria-hidden="true">★★★★★</span><span class="review-label">What our customers say</span></div>
      <div id="review-slides">{''.join(slides)}</div>
      <div class="review-bottom">
        <div>
          <div class="review-person"><strong id="review-name">Missy</strong><span class="review-source" id="review-source">Facebook recommendation</span></div>
          <button class="review-expand" id="review-expand" type="button" aria-expanded="false" aria-controls="review-slides" hidden>Read full review</button>
        </div>
        <div class="review-controls">
          <button class="review-pause" id="review-pause" type="button" aria-label="Pause automatic reviews"></button>
          <button class="icon-button" id="review-prev" type="button" aria-label="Previous customer review"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg></button>
          <span class="review-count" id="review-count" aria-hidden="true">1 / {len(REVIEWS)}</span>
          <button class="icon-button" id="review-next" type="button" aria-label="Next customer review"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button>
        </div>
      </div>
      <p class="sr-only" id="review-announcement" aria-live="polite"></p>
      <p class="review-cta"><a class="button small" href="{REVIEW_URL}" target="_blank" rel="noopener noreferrer">Leave us a Google review {ARROW}</a></p>
    </div>"""


def town_list() -> str:
    groups = {"West Virginia": [], "Kentucky": [], "Ohio": []}
    for name, _code, state in TOWNS:
        href = TOWN_LINKS.get(name)
        label = f"{name}"
        if href:
            groups[state].append(f'<li><a href="{href}">{esc(label)}</a></li>')
        else:
            groups[state].append(f"<li>{esc(label)}</li>")
    columns = []
    for state, items in groups.items():
        columns.append(f"<div><h3>{esc(state)}</h3><ul>{''.join(items)}</ul></div>")
    return f'<div class="town-columns">{"".join(columns)}</div>'


def service_cards() -> str:
    cards = [
        ("/house-cleaning/", "Standard and recurring house cleaning", "Kitchens, bathrooms, dusting, and floors, one time or on a schedule. Pet-friendly, with a laundry add-on if you want it."),
        ("/deep-cleaning/", "Deep cleaning", "A top-to-bottom reset when the house has fallen behind, and a good first visit before recurring service."),
        ("/move-in-move-out-cleaning/", "Move-in and move-out cleaning", "A clean start before you unpack, or a walkthrough-ready home after the boxes are out."),
        ("/airbnb-turnover-cleaning/", "Airbnb and rental turnover", "A full reset between guests or tenants. Kitchens, bathrooms, floors, and the next check-in."),
        ("/apartment-condo-cleaning/", "Apartment and condo cleaning", "Sized to smaller homes in Huntington, Kenova, and Ceredo. The price depends on the space."),
        ("/commercial-cleaning/", "Commercial and office cleaning", "Restrooms, break rooms, floors, dusting, and trash for offices, storefronts, and small businesses."),
        ("/holiday-cleaning/", "Holiday and guest-ready cleaning", "Kitchens, bathrooms, guest rooms, and living areas before company arrives, or a reset after."),
    ]
    html_cards = []
    for href, title, text in cards:
        html_cards.append(
            f'<a class="service-card" href="{href}"><h3>{esc(title)}</h3><p>{esc(text)}</p><span class="more">See what’s included</span></a>'
        )
    return f'<div class="card-grid">{"".join(html_cards)}</div>'


def homepage() -> dict:
    return {
        "path": "/",
        "file": ROOT / "index.html",
        "title": "House Cleaning in Kenova & Huntington, WV | Country Roads",
        "description": "Women-owned house cleaning based in Kenova, WV for Huntington, Ashland, Ironton, and the Tri-State. Licensed and insured. Call (304) 710-5430.",
        "h1": "Get Your Evenings and Weekends Back Without Letting the House Fall Behind",
        "faqs": FAQ_HOME,
        "service_ids": [],
        "crumbs": [],
    }


def homepage_main() -> str:
    living = photo(
        "living-room",
        [640, 960],
        (960, 1280),
        "A freshly cleaned living room with warm hardwood floors, comfortable seating, and natural light",
        "(max-width: 760px) 92vw, 480px",
        lazy=False,
    )
    gallery = [
        ("bedroom", [480, 800], (800, 1067), "A clean bedroom with freshly vacuumed carpet and a neatly made bed", "01", "A room to unwind in."),
        ("bathroom", [480, 800], (800, 1067), "A freshly cleaned bathroom with a white bathtub, tiled walls, and a large mirror", "02", "One less thing to scrub."),
        ("nursery", [480, 800], (800, 600), "A clean nursery with a white crib, tidy furniture, and freshly vacuumed carpet", "03", "More room for family time."),
    ]
    figures = []
    for name, widths, size, alt, number, caption in gallery:
        figures.append(
            "<figure><button class=\"photo-button\" type=\"button\">"
            + photo(name, widths, size, alt, "(max-width: 760px) 92vw, 360px")
            + '<span class="zoom" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="m20 20-3.5-3.5"/></svg></span></button>'
            + f'<figcaption><span class="number">{number}</span> {esc(caption)}</figcaption></figure>'
        )
    return f"""
    <section class="hero" aria-labelledby="page-title">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">House cleaning in Kenova, Huntington &amp; the Tri-State</p>
          <h1 id="page-title">Get Your Evenings and Weekends Back Without Letting the House Fall Behind</h1>
          <p class="subhead">Women-owned and local. Country Roads Cleaning Solutions cleans homes and small businesses from our base in Kenova.</p>
          <div class="trust-row">
            <span>Mon–Fri, 8:00 AM–5:00 PM</span>
            <span>Licensed and insured</span>
            <span>Supplies included</span>
            <span>All forms of payment</span>
          </div>
          {reviews_html()}
          <div class="hero-cta" id="hero-cta">
            <a class="button" href="{QUOTE_PATH}">Get my cleaning quote {ARROW}</a>
            <a class="button ghost" href="{TEL}">Call {PHONE}</a>
          </div>
          <p class="cta-note">Tell us about your home. We’ll take it from there.</p>
        </div>
        <figure class="hero-visual">
          <div class="hero-image-frame">
            {living}
            <div class="photo-note"><span class="tiny">Country Roads Cleaning Solutions</span><p>A home you can enjoy. A weekend you can keep.</p></div>
          </div>
          <figcaption class="hero-caption"><span>A home cleaned by our team.</span><span>Real home. Real life.</span></figcaption>
        </figure>
      </div>
    </section>
    {homepage_quote()}
    <section class="gallery-section" aria-label="Homes cleaned by Country Roads">
      <div class="wrap">
        <div class="gallery-heading">
          <h2>A little less on your to-do list.</h2>
          <span>Real homes cleaned by our team. Tap a photo to see it larger.</span>
        </div>
        <div class="photo-grid">{''.join(figures)}</div>
        <div class="gallery-cta">
          <a class="button" href="{QUOTE_PATH}">Get my cleaning quote {ARROW}</a>
          <p>Find the right cleaning plan for your home.</p>
        </div>
      </div>
    </section>
    <article class="article">
      <div class="article-inner">
        <div class="section-label">A little help with the house</div>
        <p class="opening">You keep telling yourself you’ll catch up this weekend.</p>
        <p>Then work runs late. The kids need something. The floors fall behind again.</p>
        <p>Before you know it, Saturday has turned into another workday.</p>
        <p>That’s where Country Roads Cleaning Solutions comes in. We’re based in Kenova, West Virginia, and we clean homes in Huntington, Ceredo, Ashland, Ironton, and the rest of the Tri-State within about 25 miles.</p>
        <p>We help take the cleaning off your plate, from the bathrooms and kitchen to the floors and dust that keep piling up.</p>
        <p class="takeaway">You get help with the house. You get more of your free time back.</p>
        <h2>Get caught up. Make it easier to stay that way.</h2>
        <p>The goal is to get ahead of the buildup and make those repeat chores easier to keep up with.</p>
        <p>Start with the areas that need attention now. Then find a cleaning plan that fits your home and how much help you want. A deep clean is a sensible first visit. After that, weekly, every two weeks, or monthly keeps the house from sliding back.</p>
        <p>{esc(ABOUT)}</p>
        <p class="last-paragraph">Less of your Saturday spent scrubbing. Fewer evenings looking around at everything you still need to clean. More time to sit down, have someone over, or say yes to plans without thinking you need to clean first.</p>
      </div>
    </article>
    <section class="section" id="services" aria-labelledby="services-heading">
      <div class="wrap">
        <p class="section-label">What we clean</p>
        <h2 id="services-heading">House cleaning, and the jobs that come with it</h2>
        <p class="subhead">Twelve services, grouped so you can find the one that matches the house. Pricing is a quote, not a number on this page. Call or text {PHONE} or <a href="{QUOTE_PATH}">request a quote</a>.</p>
        {service_cards()}
      </div>
    </section>
    <section class="section" id="service-area" aria-labelledby="area-heading">
      <div class="wrap">
        <p class="section-label">About 25 miles from Kenova</p>
        <h2 id="area-heading">Towns we serve in West Virginia, Kentucky, and Ohio</h2>
        <div class="area-copy">
          <p>Country Roads Cleaning Solutions is the Kenova company. We clean homes and small businesses in these towns. A different business uses a similar name in Morgantown. That is not us. If you want a cleaner in Kenova, Huntington, Ashland, or Ironton, you are in the right place.</p>
          <p>We opened in September 2026. We don’t publish a street address because customers don’t come to an office. We come to you. Put your ZIP code on the <a href="{QUOTE_PATH}">quote form</a> if you aren’t sure you’re inside the area.</p>
          <p>Hours are Monday through Friday, 8:00 AM to 5:00 PM. Closed Saturday and Sunday. Call or text <a href="{TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
        </div>
        {town_list()}
      </div>
    </section>
    {faq_html(FAQ_HOME, "Questions we hear before a first cleaning")}
    """


PRICE = FAQ_HOME[2]
SUPPLIES = FAQ_HOME[5]
ACCESS = FAQ_HOME[4]
HOURS = FAQ_HOME[9]
AREAS = FAQ_HOME[0]
PETS = FAQ_HOME[3]
OFFICES = FAQ_HOME[7]
PAYMENTS = FAQ_HOME[8]


def office_huntington_page() -> dict:
    """Huntington-only office page. /commercial-cleaning/ stays the Tri-State hub."""
    sentence = "Country Roads Cleaning Solutions cleans offices, storefronts, and small businesses in Huntington, WV, from our base in nearby Kenova."
    lede = (
        f"{esc(sentence)} A typical visit covers restrooms, the break room, floors, dusting, and trash on a schedule "
        f"built around your hours. We’re women-owned, licensed, and insured. Call <a href=\"{TEL}\">{PHONE}</a> for a quote."
    )
    faqs = [
        ("How often should a small office be cleaned?", "It depends on how many people use the space and how hard the restrooms and break room get used. A busy storefront needs more frequent visits than a quiet office. Tell us your headcount, foot traffic, and when the space is empty, and we'll recommend a schedule that keeps it presentable without paying for visits you don't need."),
        ("How much does office cleaning cost in Huntington?", "We don't publish a rate card, because a small office and a busy storefront are different jobs. The quote depends on the size of the space, the number of restrooms, how often you want visits, and what needs attention. Call (304) 710-5430 or use the quote form with \"Not a home (office or other)\" selected."),
        ("Can you clean before or after business hours?", "Our phone hours are Monday through Friday, 8:00 AM to 5:00 PM. Call then and tell us when the space is empty enough to clean, and we'll confirm a schedule that works around your customers and staff. We don't promise nights or weekends up front, but ask and we'll tell you honestly whether we can."),
        ("What kinds of businesses do you clean?", "We clean offices, storefronts, and other small businesses. We don't take on hospitals, factories, or whole school buildings. If your space has something unusual, like a showroom, a back office, or a treatment room, describe it on the quote form or call (304) 710-5430, and we'll tell you whether it fits."),
        ("Do you only clean in Huntington?", "No. Huntington is the largest city we serve, but we're based in Kenova and cover businesses within about 25 miles, including Ceredo, Barboursville, Ashland, and Ironton. An office near Pullman Square in Huntington and a storefront on Winchester Avenue in Ashland are both ordinary drives for us. Send your ZIP code if you're near the edge."),
        ("Are you insured, and do you bring supplies?", "Yes. Country Roads Cleaning Solutions is licensed and insured, and we bring our own supplies and equipment. If your building requires a specific product, tell us and we'll use it. We're women-owned and based in Kenova. Keys or alarm access are arranged by phone, so please don't send door codes through the website form."),
    ]
    return {
        "path": "/office-cleaning-huntington-wv/",
        "title": "Office Cleaning in Huntington, WV | Country Roads",
        "description": "Office and storefront cleaning in Huntington, WV from a Kenova team. Restrooms, break rooms, floors, dusting, trash. Call (304) 710-5430 for a quote.",
        "h1": "Office and small-business cleaning in Huntington, West Virginia",
        "eyebrow": "Huntington · offices and storefronts",
        "lede": lede,
        "crumbs": [("Commercial cleaning", "/commercial-cleaning/"), ("Huntington, WV", "/office-cleaning-huntington-wv/")],
        "service_ids": [],
        "service_sentence": sentence,
        "service_name": "Office cleaning in Huntington, West Virginia",
        "service_type": "Office cleaning",
        "area_served": {"@type": "City", "name": "Huntington", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
        "faqs": faqs,
        "body": f"""
        <h2>What does office cleaning include?</h2>
        <p>A typical office visit covers restrooms, the break room, floors, dusting, and emptying trash. We bring our own supplies unless your building specifies a product. If you have something beyond that, like a showroom, a back office, or a treatment room, describe it when you ask for a quote and we’ll tell you honestly whether it fits.</p>
        <ul>
          <li>Restrooms</li>
          <li>The break room</li>
          <li>Floors</li>
          <li>Dusting</li>
          <li>Emptying trash</li>
        </ul>
        <p>This page is about Huntington. For Kenova, Ashland, Ironton, and the other river towns, see <a href="/commercial-cleaning/">commercial cleaning across the Tri-State</a>. If you also want help at home, we do <a href="/huntington-wv-house-cleaning/">house cleaning in Huntington</a> too.</p>
        <h2>Which parts of Huntington do you cover?</h2>
        <p>We clean offices and storefronts across Huntington: downtown around Pullman Square, near Marshall University, in the West End toward Ceredo and Kenova, and on the east side in Highlawn and Guyandotte. Barboursville, including the area around the Huntington Mall, is on the same schedule, so you don’t need a Huntington street address to ask for a quote.</p>
        <p>Huntington sits well inside the area we cover from Kenova. A business in <a href="/ashland-ky-house-cleaning/">Ashland</a> or <a href="/ironton-oh-house-cleaning/">Ironton</a> works the same way. If you’re not sure the drive works, put your ZIP code on the quote form and we’ll confirm.</p>
        <h2>What should I tell you when I ask for a quote?</h2>
        <p>Tell us what kind of business it is, roughly how big the space is, how many restrooms it has, and when it’s empty enough to clean. Mention how often you’d like visits and anything unusual, like a showroom floor or a back office. On the quote form, choose “Not a home (office or other)” for bedrooms and bathrooms.</p>
        <p>For the cleaning type, pick “Commercial or office cleaning.” Please don’t send door codes, alarm codes, or key details through the form. Call or text <a href="{TEL}">{PHONE}</a> Monday through Friday, 8:00 AM to 5:00 PM, and we’ll arrange access with you by phone.</p>
        {related([("/commercial-cleaning/", "Commercial cleaning across the Tri-State"), ("/huntington-wv-house-cleaning/", "House cleaning in Huntington"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton")])}
        """,
    }


def service_pages() -> list[dict]:
    common_related = [
        ("/house-cleaning/", "House cleaning"),
        ("/deep-cleaning/", "Deep cleaning"),
        ("/move-in-move-out-cleaning/", "Move-in / out"),
        ("/huntington-wv-house-cleaning/", "Huntington"),
        ("/ashland-ky-house-cleaning/", "Ashland"),
        ("/ironton-oh-house-cleaning/", "Ironton"),
        ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"),
    ]
    pages = []

    pages.append({
        "path": "/house-cleaning/",
        "title": "Standard House Cleaning in Kenova & Huntington | Country Roads",
        "description": "Standard and recurring house cleaning in Kenova, Huntington, and the Tri-State. Weekly, every two weeks, or monthly. Call (304) 710-5430.",
        "h1": "Standard and recurring house cleaning in Kenova and Huntington",
        "eyebrow": "House cleaning",
        "lede": "The regular clean: kitchens, bathrooms, dusting, and floors, on the schedule that keeps the house from getting ahead of you.",
        "crumbs": [("House cleaning", "/house-cleaning/")],
        "service_ids": ["standard", "recurring", "onetime", "pets", "laundry"],
        "faqs": [
            ("How often can I book house cleaning?", "Standard house cleaning is available one time or weekly, every two weeks, or monthly. Recurring visits keep the kitchen, bathrooms, floors, and dusting on track."),
            PETS,
            SUPPLIES,
        ],
        "body": f"""
        <h2>Standard house cleaning</h2>
        @@standard@@
        <p>This is the visit most families book once the house is already in decent shape. We clean kitchens and bathrooms, dust, vacuum, and mop. It is meant to handle the everyday buildup, not to strip a neglected bathroom back to the tile. If the house has gotten away from you, start with a <a href="/deep-cleaning/">deep clean</a> and then settle into a recurring visit.</p>
        <p>Homes in Kenova, Ceredo, and Huntington are the heart of the schedule, and we drive the same service out to Ashland, Ironton, and the other towns on our <a href="/#service-area">service area list</a>.</p>
        <h2>Recurring cleaning</h2>
        @@recurring@@
        <p>Weekly tends to fit a busy house with kids or pets, where the kitchen and floors don’t stay done for long. Every two weeks is a steady way to keep a home under control between your own tidying. Monthly is a reset if you keep up with the daily mess and want a deeper pass on a set day. We’ll recommend one of those when you tell us about the house. You can also start with a single visit and decide later.</p>
        <h2>One-time cleaning</h2>
        @@onetime@@
        <p>A one-time clean is the right call before guests, after a stretch of overtime, or ahead of a holiday. There’s no contract. If you already know company is coming, the <a href="/holiday-cleaning/">holiday and guest-ready clean</a> is the more specific version of this.</p>
        <h2>Pet-friendly cleaning</h2>
        @@pets@@
        <p>Tell us about the animals when you request a quote: how many, whether they’re crate-shy, and which door or corner collects the hair. We’ll work around them and spend extra time on pet hair, nose prints, and the dusty spot behind a food bowl. You don’t need to board them for us to come.</p>
        <h2 id="laundry">Laundry and linen add-on</h2>
        @@laundry@@
        <p>This is an add-on to a house cleaning visit, not a drop-off laundry service. We can wash, dry, and fold a load, or strip and remake beds. It pairs well with a regular clean and with <a href="/airbnb-turnover-cleaning/">rental turnovers</a>. The price depends on the load, so ask for it in the quote notes or by phone.</p>
        <h2>A simple way to choose</h2>
        <p>If you’re behind, book the deep clean first. If you’re mostly keeping up and want the weekends back, book standard cleaning on a repeat schedule. If you only need help once, say so. Apartments and condos use the same tasks, scaled to the space, on the <a href="/apartment-condo-cleaning/">apartment and condo page</a>.</p>
        {how_we_work()}
        {related([item for item in common_related if item[0] != "/house-cleaning/"] + [("/holiday-cleaning/", "Holiday cleaning"), ("/airbnb-turnover-cleaning/", "Airbnb turnover")])}
        """,
    })

    pages.append({
        "path": "/deep-cleaning/",
        "title": "Deep Cleaning in Huntington & the Tri-State | Country Roads",
        "description": "Deep house cleaning in Kenova, Ceredo, Huntington, and nearby Tri-State towns. A top-to-bottom reset before recurring visits. Call (304) 710-5430.",
        "h1": "Deep cleaning in Kenova, Huntington, and the Tri-State",
        "eyebrow": "Deep cleaning",
        "lede": "A reset for a home that has fallen behind: kitchens, bathrooms, baseboards, pet hair, and the spots a quick tidy never reaches.",
        "crumbs": [("Deep cleaning", "/deep-cleaning/")],
        "service_ids": ["deep"],
        "faqs": [
            ("Is a deep clean a good first visit?", "Yes. Deep cleaning is a top-to-bottom reset for a home that has fallen behind, and it is a good first visit before recurring service."),
            AREAS,
            PRICE,
        ],
        "body": f"""
        <h2>What a deep clean covers</h2>
        @@deep@@
        <p>Standard cleaning keeps a maintained house under control. A deep clean is for the house that needs a restart: grease and grime that have sat in the kitchen, soap buildup in the bathroom, dust on baseboards, and hair worked into corners. We still don’t publish a room-by-room price. The condition of the home changes the time, so the quote asks for bedrooms, bathrooms, size, and a note about what has been waiting.</p>
        <p>People book this before they start <a href="/house-cleaning/">recurring cleaning</a>, before out-of-town family arrives, and when a <a href="/move-in-move-out-cleaning/">move-out</a> needs more than a surface wipe. If the visit is specifically for Thanksgiving, Christmas, or houseguests, see <a href="/holiday-cleaning/">holiday and guest-ready cleaning</a>.</p>
        <h2>What we don’t do on a deep clean</h2>
        <p>We don’t shampoo carpets, wash exterior windows, or pressure-wash siding or decks. Those aren’t services we sell. If that’s the main job, you’ll want a specialist. If the job is the inside of the house — kitchens, bathrooms, floors, dust, and the built-up corners — that’s us.</p>
        <h2>Where we do this work</h2>
        <p>Kenova and Ceredo are home base. Huntington is the largest city on the schedule. We also deep clean in Ashland, Ironton, and the other towns within about 25 miles of Kenova, including <a href="/barboursville-wv-house-cleaning/">Barboursville</a>, Wayne, Catlettsburg, Russell, Flatwoods, and South Point. Send the ZIP if you live on the edge of that circle.</p>
        {how_we_work()}
        {related([("/house-cleaning/", "Recurring house cleaning"), ("/holiday-cleaning/", "Holiday cleaning"), ("/move-in-move-out-cleaning/", "Move-in / out"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/barboursville-wv-house-cleaning/", "Barboursville")])}
        """,
    })

    pages.append({
        "path": "/move-in-move-out-cleaning/",
        "title": "Move-In and Move-Out Cleaning in the Tri-State | Country Roads",
        "description": "Move-in and move-out cleaning in Kenova, Huntington, Ceredo, and nearby Ohio and Kentucky towns. Tell us the move date. Call (304) 710-5430.",
        "h1": "Move-in and move-out cleaning in the Tri-State",
        "eyebrow": "Moving",
        "lede": "Two different jobs. Move-in cleaning happens before you unpack. Move-out cleaning happens after the boxes are gone, for a landlord, a buyer, or the next resident.",
        "crumbs": [("Move-in and move-out", "/move-in-move-out-cleaning/")],
        "service_ids": ["movein", "moveout"],
        "faqs": [
            ("What is the difference between move-in and move-out cleaning?", "Move-in cleaning is done before you unpack, including the kitchen, cabinets, bathrooms, floors, and corners the last occupants missed. Move-out cleaning is done after the boxes are out so the home is ready for a walkthrough, a landlord, or the next owner."),
            ACCESS,
            ("How do I get a price for a move clean?", "Request a quote with your ZIP code, bedrooms, bathrooms, and the move date. You can also call or text (304) 710-5430."),
        ],
        "body": f"""
        <h2>Move-in cleaning</h2>
        @@movein@@
        <p>The useful time for this visit is after the previous people are out and before your furniture fills the rooms. Empty cabinets, an empty fridge, and open floors let us reach the corners that disappear once you unpack. Tell us the date you get the keys, not just the date the truck arrives. If the place is an apartment or condo in Huntington, Kenova, or Ceredo, the <a href="/apartment-condo-cleaning/">apartment page</a> describes how we scale the same work to a smaller home.</p>
        <h2>Move-out cleaning</h2>
        @@moveout@@
        <p>This is the clean for a walkthrough. We come after the boxes are out, not while a household is still packing around us. Landlords and buyers are looking at kitchens, bathrooms, floors, and the marks left where furniture stood. If the home has sat vacant and gathered dust, say so. That is closer to a <a href="/deep-cleaning/">deep clean</a>, and we’ll quote it that way.</p>
        <p>Moves around here often cross the river: Huntington to Ashland, Kenova to South Point, Ironton to Russell. We cover those towns. Put the address ZIP on the form so we can confirm the drive from Kenova before we promise the day.</p>
        <h2>What to tell us</h2>
        <p>We need the move date, whether the home will be empty, how many bedrooms and bathrooms it has, and whether pets will still be there. We don’t need door codes in the form. If the realtor or landlord wants a key handoff, call or text <a href="{TEL}">{PHONE}</a> and we’ll arrange it with you.</p>
        {how_we_work()}
        {related([("/deep-cleaning/", "Deep cleaning"), ("/apartment-condo-cleaning/", "Apartments and condos"), ("/airbnb-turnover-cleaning/", "Rental turnover"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton")])}
        """,
    })

    pages.append({
        "path": "/airbnb-turnover-cleaning/",
        "title": "Airbnb Turnover Cleaning in Huntington & Kenova | Country Roads",
        "description": "Turnover cleaning for short-term rentals and rental homes in Huntington, Kenova, and the Tri-State. Kitchens, bathrooms, and floors. Call (304) 710-5430.",
        "h1": "Airbnb and rental turnover cleaning in the Tri-State",
        "eyebrow": "Short-term rentals",
        "lede": "A reset between guests or tenants: kitchen, bathrooms, floors, and the rest of the place ready for the next check-in.",
        "crumbs": [("Airbnb and rental turnover", "/airbnb-turnover-cleaning/")],
        "service_ids": ["airbnb"],
        "faqs": [
            ("Do you clean short-term rentals?", "Yes. We do turnover cleaning between guests or tenants for short-term rentals and rental homes in Huntington, Kenova, and the Tri-State. The price depends on the property and the schedule, so call for a quote."),
            ("Can you change the linens?", "Yes, as an add-on. We can wash, dry, and fold a load or strip and remake beds during a house cleaning visit. Pricing varies, so call (304) 710-5430 or note it on the quote form."),
            AREAS,
        ],
        "body": f"""
        <h2>Turnover cleaning</h2>
        @@airbnb@@
        <p>A turnover is a full reset, not a maintenance tidy of a home someone lives in full time. Guests leave the kitchen, bathrooms, and floors in different condition every time, so we quote from the property and the schedule rather than a flat “per stay” number posted online. Tell us how many bedrooms and bathrooms the rental has, where it sits, and how often it turns.</p>
        <p>Huntington has the most short-term rentals we get asked about, including places near downtown and Marshall University. We also turn rentals in Kenova, Ceredo, and the other Tri-State towns on our list. If the property is over the river in Ashland or Ironton, you’re still in the area as long as you’re within about 25 miles of Kenova.</p>
        <h2>Linens and laundry</h2>
        <p>Bed linen changes and a load of laundry can be added to the visit. That work is described on the <a href="/house-cleaning/#laundry">house cleaning page</a>. Ask for it when you book. We don’t promise a same-day flip, and we don’t promise a checkout window until we’ve agreed to the schedule by phone. Send the checkout time with the quote and we’ll tell you whether we can make it.</p>
        <h2>What we need from a host</h2>
        <p>The ZIP code, the size, how many guests the place sleeps, whether there’s a washer and dryer, and where supplies live if you want us to use yours. Otherwise we bring our own. Access is arranged by phone, the same way we do it for a family home. Don’t put a lockbox code in the form.</p>
        {how_we_work()}
        {related([("/house-cleaning/#laundry", "Laundry add-on"), ("/apartment-condo-cleaning/", "Apartments and condos"), ("/move-in-move-out-cleaning/", "Move-out cleaning"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo")])}
        """,
    })

    pages.append({
        "path": "/apartment-condo-cleaning/",
        "title": "Apartment and Condo Cleaning in Huntington, WV | Country Roads",
        "description": "Apartment and condo cleaning in Huntington, Kenova, and Ceredo. One time or recurring. Price depends on size and condition. Call (304) 710-5430.",
        "h1": "Apartment and condo cleaning in Huntington, Kenova, and Ceredo",
        "eyebrow": "Smaller homes",
        "lede": "The same kitchens, bathrooms, floors, and dusting, scaled to a studio, a one-bedroom, or a condo that doesn’t need a whole-house crew.",
        "crumbs": [("Apartments and condos", "/apartment-condo-cleaning/")],
        "service_ids": ["apartment"],
        "faqs": [
            ("Do you clean apartments and condos?", "Yes. We clean apartments, condos, and smaller homes in Huntington, Kenova, and Ceredo, one time or on a recurring schedule. Pricing depends on size and condition, so call for a quote."),
            PRICE,
            SUPPLIES,
        ],
        "body": f"""
        <h2>Cleaning sized to the space</h2>
        @@apartment@@
        <p>A studio near Marshall University and a three-bedroom house in Kenova are not the same job, which is why we don’t print a price. The quote form has a “0 / Studio” choice and a size range for a reason. Tell us the bathroom count too. A one-bath condo is a different afternoon from a place with two full baths.</p>
        <p>We clean apartments in Huntington most often: downtown, the South Side near Ritter Park, the West End, and buildings around the university. Kenova and Ceredo apartments are a short drive from where we’re based. If you’re in Ashland or Ironton in a smaller home rather than a house, say so on the form and we’ll quote it the same way.</p>
        <h2>One time, or on a schedule</h2>
        <p>Renters book us once before they get a deposit walkthrough, which overlaps with <a href="/move-in-move-out-cleaning/">move-out cleaning</a>. Others want someone in every two weeks because the apartment is small and the week is full. Both are fine. A deep clean is the better first visit if the place has been let go. After that, a standard recurring visit is usually enough.</p>
        <p>Parking and building access vary. Tell us if there’s a code for a lobby, a freight elevator, or a tight lot. We’ll confirm the details by phone rather than through the form.</p>
        {how_we_work()}
        {related([("/house-cleaning/", "Standard house cleaning"), ("/move-in-move-out-cleaning/", "Move-out cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo")])}
        """,
    })

    pages.append({
        "path": "/commercial-cleaning/",
        "title": "Office Cleaning in the Tri-State | Country Roads",
        "description": "Commercial cleaning for offices, storefronts, and small businesses in Kenova, Ceredo, Huntington, and the Tri-State. Call (304) 710-5430 for a quote.",
        "h1": "Commercial and office cleaning in the Tri-State",
        "eyebrow": "Offices and small businesses",
        "lede": "Restrooms, break rooms, floors, dusting, and trash for offices, storefronts, and other small businesses. Every space is quoted on its own.",
        "crumbs": [("Commercial cleaning", "/commercial-cleaning/")],
        "service_ids": ["commercial"],
        "faqs": [
            OFFICES,
            HOURS,
            PAYMENTS,
        ],
        "body": f"""
        <h2>What commercial cleaning includes</h2>
        @@commercial@@
        <p>This is for offices, storefronts, and small businesses, not for hospitals, factories, or a whole school. A typical visit covers restrooms, the break room, floors, dusting, and trash. If you need something beyond that — a showroom, a back office, a treatment room — describe it on the quote. We’ll say whether it fits.</p>
        <p>We’re based in Kenova and regularly cover Ceredo and Huntington. Ashland, Ironton, Barboursville, and the other towns within about 25 miles are in the same service area. A storefront on Winchester Avenue in Ashland and an office near Pullman Square in Huntington are both ordinary drives for us.</p>
        <h2>Scheduling around the business</h2>
        <p>Our phone hours are Monday through Friday, 8:00 AM to 5:00 PM. Call then and tell us when the space is empty enough to clean. We’ll confirm a schedule that works around customers and staff. We don’t promise nights or weekends on this page. If you need a time outside those phone hours, ask when you call and we’ll tell you honestly whether we can do it.</p>
        <p>We’re licensed and insured. We bring supplies unless you need a product your building already specifies. Payment can be whatever form you already use. There’s no rate card, because a two-room office and a busy storefront are different jobs.</p>
        {how_we_work()}
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/office-cleaning-huntington-wv/", "Office cleaning in Huntington"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo")])}
        """,
    })

    pages.append(office_huntington_page())

    holiday_faqs = [
        ("Can you clean my house before Thanksgiving or Christmas?", "Yes. We get the kitchen, bathrooms, guest rooms, and living areas ready before company arrives, and we can come back after. The weeks of Thanksgiving and Christmas are our busiest, so book early. Call or text (304) 710-5430 to check dates. Pricing varies by home, so you'll get a quote, not a package price."),
        ("How far ahead should I book a cleaning before Thanksgiving?", "As early as you can. Thanksgiving week is one of our busiest, and we don't hold dates on the website or promise a day until we've talked. Call or text (304) 710-5430 and ask what's still open. If we're booked, we'll say so. The earlier you ask, the more dates there are to choose from."),
        ("Do you clean on Thanksgiving Day, Christmas Day, or New Year's Day?", "Usually not on the holiday itself. We prefer not to schedule cleanings on Thanksgiving Day, Christmas Day, or New Year's Day. We do take holiday and event cleanings in the days around them, before guests arrive or after they leave. Call or text (304) 710-5430 to ask what's still open."),
        ("Should I book a deep clean or a standard clean before the holidays?", "If the house is already in good shape, a standard one-time cleaning finishes the main rooms before guests arrive. If the year has piled up, with dusty baseboards and fans or a bathroom that needs a real scrub, book a deep clean instead. Not sure? Choose \"Help me choose\" on the quote form and we'll recommend one."),
        ("What does a guest-ready clean include?", "A guest-ready clean covers the kitchen, bathrooms, guest rooms, and living areas, the rooms company actually uses. It doesn't include decorating, cooking, or watching the house. If the home has fallen behind, a deep clean is the better fit. Tell us which rooms matter most and how many people are staying when you request a quote."),
        ("Do you clean the oven or fridge before Thanksgiving?", "Only if you ask. Cleaning inside the oven or fridge isn't part of a standard holiday clean, but we can add it as an extra. Mention it on the quote form or when you call or text (304) 710-5430, so we can plan the time and include it in your quote."),
        ("Can you clean after Thanksgiving dinner or after guests leave?", "Yes. After the meal, a visit can reset the kitchen and bathrooms once everyone has gone. You can book it on its own or pair it with a clean before guests arrive. Call or text (304) 710-5430 with the dates you have in mind, and we'll tell you honestly what's open that week."),
        ("Can you change the sheets in the guest room?", "Yes, with our laundry and linen add-on. We can strip and remake beds, or wash, dry, and fold a load, as part of a house cleaning visit. It isn't a drop-off laundry service. Mention the guest beds in your quote notes or when you call, and we'll include it in your quote."),
        ("How much does holiday cleaning cost?", "We don't publish a holiday package price, because every home and guest list is different. Your quote depends on the home's size, bathrooms, condition, and whether you want a standard or deep clean, before or after guests. Request a free quote on our form or call or text (304) 710-5430. There's no contract for a one-time clean."),
        ("Do you do holiday cleaning outside Kenova?", "Yes. We're based in Kenova, WV, and do holiday and guest-ready cleaning within about 25 miles, including Huntington, Ceredo, Barboursville, and Milton in West Virginia; Ashland and Russell in Kentucky; and Ironton and South Point in Ohio. Put your ZIP code on the quote form if you're not sure you're inside the area."),
        ACCESS,
        ("Are you pet friendly when we have family visiting?", "Yes. We're pet friendly and work around dogs and cats, so you don't need to board them for us to come. Tell us how many pets you have, whether they're crate-shy, and where the hair collects. Before guests arrive, we'll spend extra time on pet hair, nose prints on glass, and dusty corners."),
    ]
    pages.append({
        "path": "/holiday-cleaning/",
        "title": "Holiday & Thanksgiving House Cleaning | Country Roads",
        "description": "Cleaning before Thanksgiving or Christmas in Kenova, Huntington, Ashland & Ironton. Kitchens, baths, guest rooms. Book early: call or text (304) 710-5430.",
        "h1": "Holiday and guest-ready cleaning before company arrives",
        "eyebrow": "Thanksgiving, Christmas, and houseguests",
        "lede": "We get the kitchen, bathrooms, guest rooms, and living areas ready before family arrives, and we can come back after. The week matters, so call to check dates.",
        "crumbs": [("Holiday cleaning", "/holiday-cleaning/")],
        "service_ids": ["holiday"],
        "faqs": holiday_faqs,
        "body": f"""
        <h2>Getting the house ready for company</h2>
        @@holiday@@
        <p>In the Tri-State, holiday weeks mean people driving between Huntington, Ashland, Ironton, and the smaller river towns. Guest rooms get used, the kitchen takes a beating, and the bathroom everyone shares shows it. A guest-ready clean puts those rooms first. It is not a promise to decorate, cook, or watch the house while you’re out.</p>
        <p>If the rest of the year has piled up too, book a <a href="/deep-cleaning/">deep clean</a> instead of a light once-over. Baseboards, the dusty fan, and the bathroom that hasn’t had a real scrub are what guests notice, and they’re part of a deep clean. A standard <a href="/house-cleaning/">one-time house cleaning</a> is enough when the home is already in good shape and you only need the main rooms finished.</p>
        <h2>Dates fill up, and we won’t guess</h2>
        <p>The week of Thanksgiving and the week of Christmas are the busy ones. We don’t hold dates on the website, and we don’t promise a specific day until we’ve talked. Call or text <a href="{TEL}">{PHONE}</a> and ask what’s still open. If we’re booked, we’ll say so. After the meal, the same visit can be a reset of the kitchen and bathrooms once everyone has gone.</p>
        <p>Tell us how many people are staying, which rooms they’ll use, and whether you want us before they arrive, after they leave, or both. Pricing depends on the home, so it comes back as a quote, not a package price.</p>
        <h2>Cleaning before Thanksgiving in the Tri-State</h2>
        <p>Country Roads Cleaning Solutions cleans homes before Thanksgiving across Kenova, Huntington, Ashland, Ironton, and nearby Tri-State towns. We focus on the kitchen, bathrooms, guest rooms, and living areas your family will actually use. Thanksgiving week is one of our busiest, so book early. Call or text <a href="{TEL}">{PHONE}</a> to check which dates are still open.</p>
        <p>Tell us the day guests arrive and which rooms they’ll use. Cleaning inside the oven or fridge isn’t part of the standard holiday clean, but we can add it as an extra if you ask when you call.</p>
        <h2>Cleaning before Christmas and New Year’s guests</h2>
        <p>Yes, we also clean before Christmas and New Year’s visitors. The week of Christmas fills up like Thanksgiving week, so it helps to ask early. Tell us how many people are staying, which rooms they’ll use, and whether you want us before they arrive, after they leave, or both.</p>
        <p>We prefer not to schedule cleanings on Thanksgiving Day, Christmas Day, or New Year’s Day themselves. We’re glad to take holiday and event cleanings in the days around them, so ask about the dates before and after.</p>
        <h2>Before the guests, after the meal, or both</h2>
        <p>You can book a guest-ready clean before company arrives, a reset after everyone leaves, or both. Before the visit, we put the kitchen, bathrooms, guest rooms, and living areas first. After the meal, the same kind of visit resets the kitchen and bathrooms. Tell us which you want when you <a href="{QUOTE_PATH}">request a quote</a>.</p>
        <p>Hosting guests in a rental instead of your own home? The <a href="/airbnb-turnover-cleaning/">rental turnover</a> page covers resets between check-ins.</p>
        <h2>What we put first in a holiday clean</h2>
        <p>Guests notice the rooms they use. A guest-ready clean puts the kitchen, the shared bathroom, guest rooms, and living areas first. If the house has fallen behind, book a <a href="/deep-cleaning/">deep clean before the holidays</a> so baseboards, the dusty fan, and built-up bathroom grime get attention too. Tell us which rooms matter most.</p>
        <h3>Holiday cleaning checklist: what we cover</h3>
        <ul>
          <li>Kitchen: counters, surfaces, and the everyday buildup.</li>
          <li>Bathrooms, especially the one everyone shares.</li>
          <li>Guest rooms. Add a bed linen change with the <a href="/house-cleaning/#laundry">laundry and linen add-on</a> if you want one.</li>
          <li>Living areas: dusting and floors, vacuumed and mopped.</li>
          <li>A deep clean adds baseboards, ceiling fans, built-up kitchen grease and bathroom soap scum, and pet hair.</li>
          <li>Extras, only if you ask: inside the oven and inside the fridge.</li>
          <li>Not included: decorating, cooking, house-sitting, carpet shampooing, exterior windows, or pressure washing.</li>
        </ul>
        {how_we_work()}
        {related([("/deep-cleaning/", "Deep cleaning"), ("/house-cleaning/", "One-time house cleaning"), ("/airbnb-turnover-cleaning/", "Rental turnover"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/barboursville-wv-house-cleaning/", "Barboursville"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton")])}
        """,
    })
    return pages


def city_pages() -> list[dict]:
    base_faqs_tail = [PRICE, ACCESS]
    pages = []

    huntington_sentence = "House cleaning for homes in Huntington, West Virginia, by Country Roads Cleaning Solutions in Kenova."
    pages.append({
        "path": "/huntington-wv-house-cleaning/",
        "title": "House Cleaning in Huntington, WV | Country Roads",
        "description": "House cleaning in Huntington, WV from a Kenova company. Homes near Marshall, Ritter Park, the West End, Highlawn, and Guyandotte. Call (304) 710-5430.",
        "h1": "House cleaning in Huntington, West Virginia",
        "eyebrow": "Huntington · about a short trip upriver from Kenova",
        "lede": "Huntington is the largest city we serve. We clean houses, apartments, and small businesses here, and in the neighborhoods just outside the city limits that still sit inside our drive from Kenova.",
        "crumbs": [("Huntington, WV", "/huntington-wv-house-cleaning/")],
        "service_ids": [],
        "service_sentence": huntington_sentence,
        "service_name": "House cleaning in Huntington, West Virginia",
        "area_served": {"@type": "City", "name": "Huntington", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
        "faqs": [
            ("Do you clean homes in Huntington, WV?", "Yes. Huntington is in our service area. We're based in Kenova and clean houses, apartments, and small businesses in Huntington. Call or text (304) 710-5430, or send your ZIP code on the quote form, and we'll confirm."),
            *base_faqs_tail,
        ],
        "body": f"""
        <p>{esc(huntington_sentence)} We also clean in the neighborhoods people actually name when they call: downtown, the area around Marshall University, Ritter Park and the South Side, the West End, Highlawn, and Guyandotte.</p>
        <h2>Getting around Huntington</h2>
        <p>Downtown is the Pullman Square and Heritage Station end of the city, close to campus. South of the tracks, Ritter Park is the long green space the South Side is built around. The West End, also called West Huntington, runs toward the river and Route 60 in the direction of Ceredo and Kenova. Highlawn and Guyandotte are on the east side, toward Barboursville.</p>
        <p>If you’re just outside Huntington in <a href="/barboursville-wv-house-cleaning/">Barboursville</a>, including the area around the Huntington Mall and Pea Ridge, you’re still on our list. Same for <a href="/barboursville-wv-house-cleaning/#lavalette">Lavalette</a> and <a href="/barboursville-wv-house-cleaning/#milton">Milton</a>. You don’t need a Huntington street address for us to come. You need a ZIP we can reach from Kenova, which is about a 25-mile radius.</p>
        <h2>What Huntington customers usually book</h2>
        <p><a href="/house-cleaning/">Standard and recurring cleaning</a> is the ongoing visit: kitchens, bathrooms, dusting, and floors, weekly, every two weeks, or monthly. A <a href="/deep-cleaning/">deep clean</a> is the right first visit when an older house has buildup in the kitchen and bathroom. <a href="/move-in-move-out-cleaning/">Move-in and move-out cleaning</a> is common around campus and in rentals downtown, between leases. Apartments and condos are quoted on the <a href="/apartment-condo-cleaning/">apartment page</a>, and short-term rentals on the <a href="/airbnb-turnover-cleaning/">turnover page</a>.</p>
        <p><a href="/office-cleaning-huntington-wv/">Small offices and storefronts downtown</a> or along the main roads can use <a href="/commercial-cleaning/">commercial cleaning</a>. Describe the space. We don’t assume every business wants the same checklist.</p>
        <h2>Practical notes for a Huntington home</h2>
        <p>A lot of the houses south of downtown and in Guyandotte are older, with trim, stairs, and bathrooms that take longer than a new build of the same square footage. Tell us the age and the condition in the notes if you know it. That keeps the quote closer to the real job. We bring supplies, we’re pet friendly, and we’re licensed and insured.</p>
        <p>We’re women-owned and based in Kenova, not in Morgantown. Phone hours are Monday through Friday, 8:00 AM to 5:00 PM. Call or text <a href="{TEL}">{PHONE}</a>.</p>
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/apartment-condo-cleaning/", "Apartments"), ("/commercial-cleaning/", "Office cleaning"), ("/office-cleaning-huntington-wv/", "Office cleaning in Huntington"), ("/holiday-cleaning/", "Holiday cleaning"), ("/barboursville-wv-house-cleaning/", "Barboursville"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton")])}
        """,
    })

    barboursville_sentence = "House cleaning for homes in Barboursville, Milton, and Lavalette, West Virginia, by Country Roads Cleaning Solutions in Kenova."
    pages.append({
        "path": "/barboursville-wv-house-cleaning/",
        "title": "House Cleaning in Barboursville, WV | Country Roads",
        "description": "House cleaning in Barboursville, Milton & Lavalette, WV from a women-owned Kenova team. Standard, deep & move-out cleaning. Call (304) 710-5430.",
        "h1": "House cleaning in Barboursville, West Virginia",
        "eyebrow": "Barboursville · Milton · Lavalette",
        "lede": "Yes, we clean in Barboursville, including the area around the Huntington Mall and Pea Ridge, and in nearby Milton and Lavalette. We come from our base in Kenova. Call or text, or send your ZIP code on the quote form.",
        "crumbs": [("Barboursville, WV", "/barboursville-wv-house-cleaning/")],
        "service_ids": [],
        "service_sentence": barboursville_sentence,
        "service_name": "House cleaning in Barboursville, West Virginia",
        "area_served": [
            {"@type": "City", "name": "Barboursville", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
            {"@type": "City", "name": "Milton", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
            {"@type": "City", "name": "Lavalette", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
        ],
        "faqs": [
            ("Do you offer house cleaning in Barboursville, WV?", "Yes. Country Roads Cleaning Solutions cleans homes in Barboursville, WV, including the area around the Huntington Mall and Pea Ridge, from our base in Kenova. We offer standard and recurring cleaning, deep cleaning, and move-in/move-out cleaning. Call or text (304) 710-5430, or send your ZIP code on the quote form."),
            ("Do you clean in Milton, WV?", "Yes. Milton is on our service list, inside our roughly 25-mile drive from Kenova. We clean houses and apartments there the same way we do in Barboursville and Huntington. Send your ZIP code on the quote form, or call or text (304) 710-5430 to confirm."),
            ("Do you clean in Lavalette, WV?", "Yes. Lavalette is on our service list, along with Wayne and the rest of the area within about 25 miles of Kenova. You don't need a Huntington address for us to come. You need a ZIP we can reach. Put yours on the quote form or call (304) 710-5430."),
            ("How much does house cleaning cost in Barboursville?", "We don't publish prices, because homes of the same size can be very different jobs. Your free quote depends on bedrooms, bathrooms, square footage, the home's condition, the type of cleaning, and how often you want help. Fill out the quote form with those details or call or text (304) 710-5430, and we'll send a recommendation and quote."),
            ("Do I need to be home, and do you bring supplies?", "You don't have to be home. We arrange keys or other access with you directly, so please don't put a door code in the website form. We bring our own supplies and equipment. If you want a specific product used, tell us. We're licensed, insured, and pet friendly, and we accept all forms of payment."),
            ("Are you the same company as Country Roads Cleaning in Morgantown?", "No. Country Roads Cleaning Solutions is the Kenova, WV company serving Barboursville, Huntington, and the Tri-State. A different business with a similar name operates in Morgantown, and we're not connected to it. If you want indoor house cleaning in Barboursville, Milton, or Lavalette, you're in the right place."),
        ],
        "body": f"""
        <p>{esc(barboursville_sentence)} Standard and recurring cleaning, deep cleaning, and move-in and move-out cleaning are all available here, one time or on a schedule.</p>
        <h2>Where we clean around Barboursville</h2>
        <p>Barboursville is on our list, including the homes around the Huntington Mall and Pea Ridge. Highlawn and Guyandotte sit on Huntington’s east side, toward Barboursville, so east-end Huntington and Barboursville are part of the same drive for us. You don’t need a Huntington address. You need a ZIP we can reach within about 25 miles of Kenova.</p>
        <p>Not sure whether your street counts? Put the ZIP code on the <a href="{QUOTE_PATH}">quote form</a> or call or text <a href="{TEL}">{PHONE}</a>. If the drive doesn’t work, we’ll tell you instead of guessing. If you live closer in, see <a href="/huntington-wv-house-cleaning/">house cleaning in Huntington</a>.</p>
        <h2 id="milton">House cleaning in Milton</h2>
        <p>Milton is on our service list too. It sits east of Barboursville and is still inside the area we cover from Kenova. We clean houses and apartments there the same way we do in Barboursville and Huntington: kitchens, bathrooms, dusting, and floors, once or on a schedule. Send your ZIP code on the quote form, or call or text to confirm before you book.</p>
        <h2 id="lavalette">House cleaning in Lavalette</h2>
        <p>Lavalette is on the list as well. Barboursville and Milton are in Cabell County, while Lavalette is in Wayne County, the same county as <a href="/kenova-ceredo-house-cleaning/">our Kenova home base</a>. County lines don’t change anything for us. If the house is within about 25 miles of Kenova, we can quote it. Wayne is on the same list if you’re farther south.</p>
        <h2>What Barboursville homeowners can book</h2>
        <p><a href="/house-cleaning/">Standard and recurring house cleaning</a>, one time or weekly, every two weeks, or monthly; a <a href="/deep-cleaning/">deep clean</a>; <a href="/move-in-move-out-cleaning/">move-in and move-out cleaning</a>; <a href="/apartment-condo-cleaning/">apartment and condo cleaning</a>; <a href="/holiday-cleaning/">holiday and guest-ready cleaning</a>; <a href="/airbnb-turnover-cleaning/">rental and Airbnb turnovers</a>; and a <a href="/house-cleaning/#laundry">laundry and linen add-on</a>. We also clean <a href="/commercial-cleaning/">offices and small businesses</a>. If you’re not sure which fits, choose “Help me choose” on the quote form.</p>
        <p>We’re pet friendly, so you don’t need to board the dog or cat. We don’t do carpet shampooing, exterior windows, or pressure washing. If that’s the job, we’re not the right call, and we’d rather say so up front.</p>
        <h2>Deep clean or regular cleaning?</h2>
        <p>If the house has fallen behind, start with a deep clean. It handles built-up kitchen grease, bathroom soap scum, baseboards, and pet hair. After that, a standard recurring visit keeps things under control. If you’re mostly keeping up, standard cleaning weekly, every two weeks, or monthly is the usual fit.</p>
        <h2>How pricing works</h2>
        <p>There’s no rate card on this site. Two houses with the same square footage can be very different jobs, so the quote comes from what you tell us: bedrooms, bathrooms, size, condition, the type of cleaning, and how often you want help. Supplies come with the visit, and a one-time clean has no contract. Fill out the quote form and we’ll send a recommendation with the quote.</p>
        {how_we_work()}
        <h2>The Kenova company, not the Morgantown one</h2>
        <p>Country Roads Cleaning Solutions is the women-owned company based in Kenova, WV. A different business uses a similar name in Morgantown. That is not us. We don’t have a Barboursville office. We drive over from Kenova and come to the house.</p>
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/move-in-move-out-cleaning/", "Move-in / out"), ("/holiday-cleaning/", "Holiday cleaning"), ("/apartment-condo-cleaning/", "Apartments"), ("/commercial-cleaning/", "Office cleaning"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo")])}
        """,
    })

    ashland_sentence = "House cleaning for homes in Ashland, Kentucky, by Country Roads Cleaning Solutions in Kenova, West Virginia."
    pages.append({
        "path": "/ashland-ky-house-cleaning/",
        "title": "House Cleaning in Ashland, KY | Country Roads",
        "description": "House cleaning in Ashland, KY, plus Catlettsburg, Russell, Flatwoods, and Raceland. Based in Kenova, WV. Call (304) 710-5430.",
        "h1": "House cleaning in Ashland, Kentucky",
        "eyebrow": "Ashland · across the river from Kenova",
        "lede": "Ashland is the largest Kentucky city we serve. We clean homes and small businesses in town and in the nearby Kentucky communities on our list.",
        "crumbs": [("Ashland, KY", "/ashland-ky-house-cleaning/")],
        "service_ids": [],
        "service_sentence": ashland_sentence,
        "service_name": "House cleaning in Ashland, Kentucky",
        "area_served": {"@type": "City", "name": "Ashland", "containedInPlace": {"@type": "State", "name": "Kentucky"}},
        "faqs": [
            ("Do you clean homes in Ashland, KY?", "Yes. Ashland is in our service area, along with Catlettsburg, Russell, Flatwoods, Raceland, and Greenup. We're based in Kenova, WV. Call or text (304) 710-5430 or send your ZIP code if you want us to confirm the drive."),
            *base_faqs_tail,
        ],
        "body": f"""
        <p>{esc(ashland_sentence)} Downtown runs along Winchester Avenue, where the Paramount Arts Center sits. Central Park, on Central Avenue, is the big public green space families use when the weather allows. Homes around downtown, along the river, and south of Winchester Avenue are ordinary stops for us.</p>
        <h2>Nearby Kentucky towns we also clean</h2>
        <p>Catlettsburg is just downriver, almost next to Kenova. Russell is across the bridge area from Ironton and a short drive from Ashland. Flatwoods, Raceland, and Greenup are farther out and still inside the area we cover from Kenova. If you live in one of those towns, you don’t need a separate cleaner. Put the ZIP on the quote and we’ll confirm.</p>
        <p>Westwood is its own city next to Ashland. It isn’t on our published 20-town list. If you’re there, send the ZIP anyway and we’ll tell you whether the drive works. We’d rather say no than guess.</p>
        <h2>Services that fit Ashland homes</h2>
        <p>River-town houses often need more time in the kitchen and on the floors than a newer house of the same size. A <a href="/deep-cleaning/">deep clean</a> is a good first visit. <a href="/house-cleaning/">Recurring cleaning</a> keeps it that way. <a href="/move-in-move-out-cleaning/">Move-out cleaning</a> is the visit to book when you’re handing a rental back or selling. Offices and storefronts on Winchester Avenue can use <a href="/commercial-cleaning/">commercial cleaning</a>.</p>
        <p>Ashland and the nearby Kentucky towns are inside our service area. The quote depends on size and condition. We’re licensed and insured, we bring supplies, and we accept all forms of payment. Call or text <a href="{TEL}">{PHONE}</a> Monday through Friday, 8:00 AM to 5:00 PM.</p>
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/commercial-cleaning/", "Office cleaning"), ("/holiday-cleaning/", "Holiday cleaning"), ("/ironton-oh-house-cleaning/", "Ironton"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/huntington-wv-house-cleaning/", "Huntington")])}
        """,
    })

    ironton_sentence = "House cleaning for homes in Ironton, Ohio, by Country Roads Cleaning Solutions in Kenova, West Virginia."
    pages.append({
        "path": "/ironton-oh-house-cleaning/",
        "title": "House Cleaning in Ironton, OH | Country Roads",
        "description": "House cleaning in Ironton, OH and nearby Ohio river towns, including Coal Grove and South Point. Based in Kenova, WV. Call (304) 710-5430.",
        "h1": "House cleaning in Ironton, Ohio",
        "eyebrow": "Ironton · Lawrence County",
        "lede": "Ironton is the largest Ohio city we serve. We clean homes and small businesses in town and in the Ohio river communities between Ironton and Kenova.",
        "crumbs": [("Ironton, OH", "/ironton-oh-house-cleaning/")],
        "service_ids": [],
        "service_sentence": ironton_sentence,
        "service_name": "House cleaning in Ironton, Ohio",
        "area_served": {"@type": "City", "name": "Ironton", "containedInPlace": {"@type": "State", "name": "Ohio"}},
        "faqs": [
            ("Do you clean homes in Ironton, OH?", "Yes. Ironton is in our service area, along with Coal Grove, South Point, Chesapeake, Proctorville, and Burlington. We're based in Kenova, WV. Call or text (304) 710-5430 or send your ZIP code to confirm."),
            *base_faqs_tail,
        ],
        "body": f"""
        <p>{esc(ironton_sentence)} Ironton is the Lawrence County seat, on the Ohio River. The bridge to Russell, Kentucky, ties it to another town we serve. Ohio University Southern’s campus is on Liberty Avenue in town, which is a useful landmark when you’re describing where a house sits.</p>
        <h2>The Ohio towns between Ironton and Kenova</h2>
        <p>Coal Grove is just up against Ironton. South Point and Burlington are close to Kenova, across the river from our base. Chesapeake sits across from Huntington, and Proctorville is farther up the river. All of them are on the service list. If your house is in one of those towns, you’re not “out of the way” for a Kenova cleaner. You’re in the area we already drive.</p>
        <h2>Older houses, honest quotes</h2>
        <p>A lot of homes near downtown Ironton were built when the railroad and the mills were the reason the town was here. Smaller rooms, original trim, and bathrooms that need a real scrub are normal. Tell us that on the quote. A <a href="/deep-cleaning/">deep clean</a> is usually the right first visit. Afterward, <a href="/house-cleaning/">weekly, every-two-weeks, or monthly cleaning</a> keeps the kitchen and bathrooms from sliding.</p>
        <p>Move-out cleans are common when a house sells or a tenant leaves. Use the <a href="/move-in-move-out-cleaning/">move-in and move-out page</a> and include the date. Small offices can be quoted through <a href="/commercial-cleaning/">commercial cleaning</a>. Ironton and the nearby Ohio towns are inside our service area. Call or text <a href="{TEL}">{PHONE}</a> during Monday–Friday, 8:00 AM–5:00 PM.</p>
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/move-in-move-out-cleaning/", "Move-out cleaning"), ("/holiday-cleaning/", "Holiday cleaning"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/kenova-ceredo-house-cleaning/", "Kenova & Ceredo"), ("/huntington-wv-house-cleaning/", "Huntington")])}
        """,
    })

    kenova_sentence = "House cleaning for homes in Kenova and Ceredo, West Virginia, where Country Roads Cleaning Solutions is based."
    pages.append({
        "path": "/kenova-ceredo-house-cleaning/",
        "title": "House Cleaning in Kenova & Ceredo, WV | Country Roads",
        "description": "House cleaning in Kenova and Ceredo, WV. Women-owned, based in Kenova 25530, serving the Huntington Tri-State. Call (304) 710-5430.",
        "h1": "House cleaning in Kenova and Ceredo, West Virginia",
        "eyebrow": "Home base · Wayne County",
        "lede": "This is where we’re from. Kenova and Ceredo sit side by side on U.S. 60, at the western tip of West Virginia, and they’re the first towns on our schedule.",
        "crumbs": [("Kenova and Ceredo", "/kenova-ceredo-house-cleaning/")],
        "service_ids": [],
        "service_sentence": kenova_sentence,
        "service_name": "House cleaning in Kenova and Ceredo, West Virginia",
        "area_served": [
            {"@type": "City", "name": "Kenova", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
            {"@type": "City", "name": "Ceredo", "containedInPlace": {"@type": "State", "name": "West Virginia"}},
        ],
        "faqs": [
            ("Do you clean homes in Kenova and Ceredo?", "Yes. We're based in Kenova, WV 25530, and Ceredo is the next town along U.S. 60. Call or text (304) 710-5430 or send your ZIP code on the quote form."),
            ("Are you the Country Roads cleaning company in Morgantown?", "No. Country Roads Cleaning Solutions is based in Kenova, WV, and serves the Huntington Tri-State, including nearby towns in West Virginia, Kentucky, and Ohio. The Morgantown company is a different business."),
            SUPPLIES,
        ],
        "body": f"""
        <p>{esc(kenova_sentence)} Kenova sits where the Big Sandy River meets the Ohio. The name is built from Kentucky, Ohio, and Virginia, which is the same three-state corner we drive. Ceredo is the next town east. On U.S. 60 the two run together so closely that you can cross from one into the other without a landmark announcing it.</p>
        <h2>Who’s across the river</h2>
        <p>Catlettsburg, Kentucky, is just over the Big Sandy. South Point and Burlington, Ohio, are just over the Ohio. Huntington is upriver on Route 60. All of those are on our service list, along with Ashland and Ironton a bit farther on. If you live in Kenova or Ceredo, you are not at the edge of our map. You are at the center of it. The full list is on the <a href="/#service-area">homepage service area</a>.</p>
        <h2>What we clean here</h2>
        <p><a href="/house-cleaning/">Standard cleaning</a> covers kitchens, bathrooms, dusting, and floors, once or on a weekly, every-two-weeks, or monthly visit. A <a href="/deep-cleaning/">deep clean</a> is the first visit when the house has fallen behind. <a href="/move-in-move-out-cleaning/">Move-in and move-out cleaning</a> is for a sale or a rental handoff. Small offices and storefronts in either town can be quoted as <a href="/commercial-cleaning/">commercial cleaning</a>.</p>
        <p>We don’t publish a street address. Customers don’t visit an office. We come to the house, and we arrange keys with you by phone. Please don’t send a door code through the form. We’re women-owned, licensed, and insured, we bring supplies, and we accept all forms of payment. We opened in September 2026.</p>
        <p>Call or text <a href="{TEL}">{PHONE}</a> Monday through Friday, 8:00 AM to 5:00 PM, or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
        {related([("/house-cleaning/", "House cleaning"), ("/deep-cleaning/", "Deep cleaning"), ("/move-in-move-out-cleaning/", "Move-in / out"), ("/commercial-cleaning/", "Commercial cleaning"), ("/holiday-cleaning/", "Holiday cleaning"), ("/huntington-wv-house-cleaning/", "Huntington"), ("/barboursville-wv-house-cleaning/", "Barboursville"), ("/ashland-ky-house-cleaning/", "Ashland"), ("/ironton-oh-house-cleaning/", "Ironton")])}
        """,
    })
    return pages


def render_inner(page: dict) -> str:
    body = fill_tokens(page["body"])
    main = page_hero(page) + f'<article class="article"><div class="article-inner prose">{body}</div></article>' + faq_html(page["faqs"], "Questions") + quote_form(False)
    dialogs = privacy_dialog()
    return document(page, main, include_about_in_footer=True, dialogs=dialogs)


def render_home() -> str:
    page = homepage()
    dialogs = photo_dialog() + privacy_dialog()
    return document(page, homepage_main(), include_about_in_footer=False, dialogs=dialogs)


def render_404() -> str:
    page = {
        "path": "/404.html",
        "title": "Page not found | Country Roads Cleaning Solutions",
        "description": "That page isn’t on the Country Roads Cleaning Solutions site. Call (304) 710-5430 or go back to house cleaning in Kenova and Huntington.",
        "h1": "We can’t find that page",
        "eyebrow": "404",
        "lede": "The link may be old. The cleaning company is still here, in Kenova, serving Huntington and the Tri-State.",
        "crumbs": [("Page not found", "/404.html")],
        "faqs": [],
        "service_ids": [],
        "noindex": True,
        "body": """
        <p>Try one of these, or call us and we’ll point you to the right service.</p>
        """,
    }
    # The 404 page still includes a quote form. Hero and other CTAs go to /quote/.
    main = page_hero(page) + f"""
    <article class="article"><div class="article-inner prose">
      <p>Country Roads Cleaning Solutions is the Kenova, West Virginia house cleaning company. These are the pages that are actually on the site.</p>
      {related(NAV)}
      <p>Or call <a href="{TEL}">{PHONE}</a> Monday through Friday, 8:00 AM to 5:00 PM.</p>
    </div></article>
    {quote_form(False)}
    """
    return document(page, main, include_about_in_footer=True, dialogs=privacy_dialog())


def render_apply() -> str:
    page = {
        "path": "/apply/",
        "title": "Apply to Clean With Us | Country Roads Cleaning Solutions",
        "description": "Apply to join Country Roads Cleaning Solutions, a women-owned cleaning company in Kenova, WV. Part-time and full-time cleaning work in the Tri-State.",
        "noindex": True,
    }
    def radios(name: str, options: list[str]) -> str:
        return "".join(
            f'<label class="choice"><input type="radio" name="{esc(name)}" value="{esc(o)}" required> {esc(o)}</label>'
            for o in options
        )
    def text(id_: str, label: str, name: str, kind: str = "text", extra: str = "", required: bool = True) -> str:
        req = " required" if required else ""
        return f'<div class="field"><label for="{id_}">{label}</label><input id="{id_}" type="{kind}" name="{esc(name)}"{extra}{req}></div>'
    def area(id_: str, label: str, name: str, hint: str = "", required: bool = True) -> str:
        req = " required" if required else ""
        return f'<div class="field"><label for="{id_}">{label}</label><textarea id="{id_}" name="{esc(name)}" rows="3" maxlength="3000" placeholder="{esc(hint)}"{req}></textarea></div>'
    def group(label: str, name: str, options: list[str]) -> str:
        return f'<fieldset class="field choice-group"><legend>{label}</legend>{radios(name, options)}</fieldset>'
    fields = "".join([
        text("a-name", "Full name", "Full name", extra=' autocomplete="name" maxlength="100"'),
        text("a-phone", "Phone number", "Phone", kind="tel", extra=' autocomplete="tel" maxlength="30"'),
        text("a-email", "Email address", "email", kind="email", extra=' autocomplete="email" maxlength="254"'),
        text("a-city", "What city and state do you live in?", "City and state", extra=' autocomplete="address-level2" maxlength="100" placeholder="e.g. Huntington, WV"'),
        group("Are you looking for part-time or full-time work?", "Part-time or full-time", ["Part-time", "Full-time", "Open to either"]),
        text("a-hours", "How many hours per week would you like to work?", "Hours per week wanted", extra=' maxlength="50"'),
        group("Do you have reliable transportation to and from cleaning jobs?", "Reliable transportation", ["Yes", "No"]),
        area("a-exp", "What cleaning experience do you have?", "Cleaning experience", "Briefly describe any house cleaning, commercial cleaning, housekeeping, or other relevant experience."),
        area("a-job", "Briefly describe your current or most recent job and how long you worked there.", "Current or most recent job"),
        group("Are you comfortable cleaning homes where pets are present?", "Comfortable with pets", ["Yes", "No"]),
        text("a-start", "When would you be available to start?", "Available to start", extra=' maxlength="100"'),
        area("a-why", "Why are you interested in working with Country Roads Cleaning Solutions?", "Why Country Roads"),
        area("a-else", 'Is there anything else you’d like us to know? <span class="optional">(optional)</span>', "Anything else", required=False),
    ])
    main = f"""
    <section class="page-hero">
      <div class="wrap prose">
        <p class="eyebrow">We’re hiring</p>
        <h1>Apply to clean with Country Roads</h1>
        <p class="lede">We’re a women-owned cleaning company in Kenova, WV, growing our team for homes and businesses across the Tri-State. Fill this out and we’ll be in touch.</p>
      </div>
    </section>
    <section class="article"><div class="article-inner">
      <div class="form-card apply-card">
        <p class="form-status apply-thanks" id="apply-thanks" hidden>Thanks for applying! We got your application and will reach out soon.</p>
        <form class="apply-form" id="apply-form" method="POST" action="https://formsubmit.co/{EMAIL}">
          {fields}
          <div class="honeypot" aria-hidden="true"><label for="a-website">Leave this field empty</label><input id="a-website" name="_honey" tabindex="-1" autocomplete="off"></div>
          <input type="hidden" name="_subject" value="New job application | Country Roads Cleaning Solutions">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_next" value="{BASE}/apply/?sent=1">
          <button class="button submit-button" type="submit">Submit my application {ARROW}</button>
          <p class="form-footnote">We’ll use your details only to follow up about this application.</p>
        </form>
      </div>
    </div></section>
    <script>if(new URLSearchParams(location.search).has("sent")){{document.getElementById("apply-thanks").hidden=false;document.getElementById("apply-form").hidden=true;}}</script>
    """
    return document(page, main, include_about_in_footer=True, dialogs=privacy_dialog()).replace(mobile_cta(), "")


def _plain_label(field_html: str) -> str:
    match = re.search(r"<label\b[^>]*>(.*?)</label>", field_html, re.S)
    if not match:
        return "Question"
    text = re.sub(r"<[^>]+>", "", match.group(1))
    return " ".join(html.unescape(text).split())


def _contact_quiz_parts() -> tuple[str, str, str]:
    """Name, phone/email block, and notes from the shared contact fields, in quiz order."""
    lines = [line.strip() for line in quote_contact_fields("q-").splitlines() if line.strip()]
    if len(lines) != 7:
        raise RuntimeError(f"quote contact fields layout changed ({len(lines)} lines)")
    return lines[0], "\n".join(lines[1:6]), lines[6]


def quote_quiz_steps() -> tuple[str, int]:
    """One shared field per screen: six home questions, name, contact, then notes."""
    home = [line.strip() for line in quote_home_fields("q-").splitlines() if line.strip()]
    if len(home) != 6:
        raise RuntimeError(f"quote home fields layout changed ({len(home)} lines)")
    name, contact, notes = _contact_quiz_parts()
    steps = [("field", item) for item in home]
    steps.append(("field", name))
    steps.append(("contact", contact))
    steps.append(("notes", notes))
    parts = []
    for index, (kind, body) in enumerate(steps):
        current = " is-current" if index == 0 else ""
        if kind == "contact":
            legend = "<legend>Where should we send your quote?</legend>"
        else:
            legend = f'<legend class="sr-only">{esc(_plain_label(body))}</legend>'
        parts.append(f'<fieldset class="quiz-step quiz-step-{kind}{current}">{legend}{body}</fieldset>')
    return "\n".join(parts), len(steps)


def render_quote() -> str:
    page = {
        "path": "/quote/",
        "title": "Request a Cleaning Quote | Country Roads Cleaning Solutions",
        "description": "Request a free house or office cleaning quote from Country Roads Cleaning Solutions, a women-owned cleaning company in Kenova, WV.",
        "noindex": True,
    }
    steps_html, total = quote_quiz_steps()
    meter = f"{100 / total:.3f}"
    main = f"""
    <section class="page-hero">
      <div class="wrap prose">
        <p class="eyebrow">Free quote</p>
        <h1>Request a cleaning quote</h1>
        <p class="lede">We’re a women-owned, licensed, and insured cleaning company based in Kenova, WV. We bring our own supplies and serve homes and businesses within about 25 miles. Tell us about your space and we’ll follow up with a personalized quote.</p>
        <p class="cta-note">Prefer to talk? Call or text <a href="{TEL}">{PHONE}</a>, Monday–Friday, 8:00 AM–5:00 PM.</p>
      </div>
    </section>
    <section class="article" id="quote-quiz" aria-labelledby="quote-quiz-heading">
      <div class="article-inner">
        <div class="form-card quote-quiz-card" id="q-card">
          <div id="q-form-wrap">
            <p class="form-label" id="quote-quiz-heading">One question at a time</p>
            <form class="quote-quiz" id="q-form" method="POST" action="https://formsubmit.co/{EMAIL}" novalidate>
              <noscript>
                <style>
                  #q-form .quiz-step {{ display: block !important; }}
                  #q-next, #q-back {{ display: none !important; }}
                  #q-submit {{ display: inline-flex !important; }}
                </style>
                <p class="form-footnote">JavaScript walks through one question at a time. All of the questions are listed below so you can still send a request. Please include a phone number or an email address.</p>
              </noscript>
              <p class="quote-progress" id="q-progress" aria-live="polite">Question 1 of {total}</p>
              <div class="quiz-meter" aria-hidden="true"><span id="q-meter" style="width:{meter}%"></span></div>
{steps_html}
              <div class="honeypot" aria-hidden="true"><label for="q-website">Leave this field empty</label><input id="q-website" name="_honey" tabindex="-1" autocomplete="off"></div>
              <input type="hidden" name="_subject" value="New quote request | Country Roads Cleaning Solutions">
              <input type="hidden" name="_template" value="table">
              <input type="hidden" name="_next" id="q-next-url" value="{BASE}/quote/?sent=1">
              <p class="form-status" id="q-status" role="alert" hidden></p>
              <div class="quiz-nav" id="q-nav">
                <button class="button submit-button" id="q-next" type="button">Continue {ARROW}</button>
                <button class="button submit-button" id="q-submit" type="submit" hidden>Request My Cleaning Quote {ARROW}</button>
                <button class="quote-back" id="q-back" type="button" hidden>Back</button>
              </div>
              <p class="form-footnote">We’ll use your contact details only to follow up about this cleaning quote.</p>
            </form>
          </div>
          <div class="form-success" id="q-thanks" role="status" hidden>
            <div class="success-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg></div>
            <div class="form-label">One step closer to a cleaner home</div>
            <h2>Thank you for reaching out.</h2>
            <p>Your cleaning quote request has been submitted. We’ll use the contact details you provided to follow up about what you need.</p>
            <button type="button" id="q-new-request">Request another quote</button>
          </div>
        </div>
      </div>
    </section>
    """
    return document(page, main, include_about_in_footer=True, dialogs=privacy_dialog()).replace(mobile_cta(), "")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def all_content_pages() -> list[tuple[dict, str]]:
    home = homepage()
    rendered = [(home, render_home())]
    for page in service_pages() + city_pages():
        page = dict(page)
        page["file"] = ROOT / page["path"].strip("/") / "index.html"
        rendered.append((page, render_inner(page)))
    return rendered


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1 = 0
        self.metas = []
        self.links = []
        self.hrefs = []
        self.ids = set()
        self.alts = []
        self.json_blocks = []
        self._capture = None
        self._buf = []
        self.text_parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag in {"script", "style"}:
            self.skip_depth += 1
            if tag == "script" and attr.get("type") == "application/ld+json":
                self._capture = "json"
                self._buf = []
        if "id" in attr:
            self.ids.add(attr["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            self.metas.append(attr)
        if tag == "a" and "href" in attr:
            self.hrefs.append(attr["href"])
        if tag == "img":
            self.alts.append(attr.get("alt"))
        if tag == "link":
            self.links.append(attr)
        if tag == "title":
            self._capture = "title"
            self._buf = []

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "script" and self._capture == "json":
            self.json_blocks.append("".join(self._buf))
            self._capture = None
        if tag == "title" and self._capture == "title":
            self.title = "".join(self._buf).strip()
            self._capture = None

    def _push_text(self, data: str) -> None:
        if self._capture in {"json", "title"}:
            self._buf.append(data)
        elif self.skip_depth == 0:
            self.text_parts.append(data)

    def handle_data(self, data):
        self._push_text(data)

    def handle_entityref(self, name):
        self._push_text(html.unescape(f"&{name};"))

    def handle_charref(self, name):
        try:
            char = chr(int(name[1:], 16) if name.lower().startswith("x") else int(name))
        except ValueError:
            return
        self._push_text(char)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.text_parts)).strip()


def check_business(node: dict, errors: list[str], where: str) -> None:
    required = ["name", "telephone", "email", "openingHoursSpecification", "address", "geo", "areaServed", "logo", "image", "url", "description"]
    for key in required:
        if key not in node:
            errors.append(f"{where}: missing {key}")
    address = node.get("address", {})
    if "streetAddress" in address:
        errors.append(f"{where}: streetAddress must not be published")
    for key in ("addressLocality", "addressRegion", "postalCode", "addressCountry"):
        if key not in address:
            errors.append(f"{where}: address missing {key}")
    if address.get("addressLocality") != "Kenova" or address.get("postalCode") != "25530":
        errors.append(f"{where}: address locality/postal mismatch")
    geo = node.get("geo", {})
    if geo.get("latitude") != 38.4022 or geo.get("longitude") != -82.5821:
        errors.append(f"{where}: geo is not the Kenova point")
    names = [item.get("name") for item in node.get("areaServed", [])]
    expected = [town[0] for town in TOWNS]
    if names != expected:
        errors.append(f"{where}: areaServed towns mismatch: {names}")
    if node.get("name") != "Country Roads Cleaning Solutions":
        errors.append(f"{where}: business name mismatch")
    if node.get("telephone") != "+1-304-710-5430":
        errors.append(f"{where}: phone mismatch")
    if node.get("email") != EMAIL:
        errors.append(f"{where}: email mismatch")
    hours = node.get("openingHoursSpecification", [{}])[0]
    if hours.get("opens") != "08:00" or hours.get("closes") != "17:00":
        errors.append(f"{where}: hours mismatch")
    for key in ("logo", "image"):
        url = node.get(key, {}).get("url", "")
        if not url.startswith(BASE + "/assets/"):
            errors.append(f"{where}: {key} url {url}")
    if node.get("sameAs") != [GBP_URL]:
        errors.append(f"{where}: sameAs should be the Google Business Profile URL")


def validate(pages: list[tuple[dict, str]]) -> None:
    errors = []
    titles = []
    descriptions = []
    files = {}
    for page, markup in pages:
        path = page["file"]
        files[page["path"]] = path
        parser = PageParser()
        parser.feed(markup)
        titles.append(page["title"])
        descriptions.append(page["description"])
        if parser.h1 != 1:
            errors.append(f"{page['path']}: h1 count {parser.h1}")
        if parser.title != page["title"]:
            errors.append(f"{page['path']}: title tag mismatch")
        canonical = next((item.get("href") for item in parser.links if item.get("rel") == "canonical"), "")
        if canonical != BASE + page["path"]:
            errors.append(f"{page['path']}: canonical {canonical}")
        gsc = [item for item in parser.metas if item.get("name") == "google-site-verification"]
        if not gsc or gsc[0].get("content") != GSC:
            errors.append(f"{page['path']}: missing exact Search Console tag")
        desc = [item for item in parser.metas if item.get("name") == "description"]
        if not desc or desc[0].get("content") != page["description"]:
            errors.append(f"{page['path']}: meta description mismatch")
        if len(page["description"]) > 170:
            errors.append(f"{page['path']}: meta description is {len(page['description'])} characters")
        if len(page["title"]) > 70:
            errors.append(f"{page['path']}: title is {len(page['title'])} characters")
        for alt in parser.alts:
            if alt is None:
                errors.append(f"{page['path']}: img missing alt")
            elif alt == "" and "lightbox-image" not in parser.ids:
                errors.append(f"{page['path']}: empty alt")
        if TEL.replace("tel:", "") not in markup and PHONE not in parser.text:
            errors.append(f"{page['path']}: phone not visible")
        if "8:00 AM" not in parser.text and "8 AM" not in parser.text:
            errors.append(f"{page['path']}: hours not visible")
        visible = parser.text
        for forbidden in ("Kane", "Katlyn", "Walnut", "1801"):
            if re.search(forbidden, visible, re.I) or re.search(forbidden, markup, re.I):
                errors.append(f"{page['path']}: forbidden term {forbidden}")
        if re.search(r"Heavenly", markup) and EMAIL not in markup:
            errors.append(f"{page['path']}: Heavenly branding")
        if re.search(r"Heavenly(?!cleaningsolutions@gmail.com)", markup):
            errors.append(f"{page['path']}: Heavenly outside the email address")
        if re.search(r"Country Road(?!s)", markup):
            errors.append(f"{page['path']}: singular Road in the name")
        if not parser.json_blocks:
            errors.append(f"{page['path']}: no JSON-LD")
            continue
        try:
            data = json.loads(parser.json_blocks[0])
        except json.JSONDecodeError as exc:
            errors.append(f"{page['path']}: JSON-LD did not parse: {exc}")
            continue
        nodes = data.get("@graph", [])
        business = next(node for node in nodes if "LocalBusiness" in node.get("@type", []))
        check_business(business, errors, page["path"])
        if ABOUT not in visible:
            errors.append(f"{page['path']}: Description A is not visible")
        for node in nodes:
            if node.get("@type") == "FAQPage":
                for entity in node["mainEntity"]:
                    question = entity["name"]
                    answer = entity["acceptedAnswer"]["text"]
                    if question not in visible or answer not in visible:
                        errors.append(f"{page['path']}: FAQ not visible: {question}")
            if node.get("@type") == "Service":
                description = node.get("description", "")
                if description and description not in visible:
                    errors.append(f"{page['path']}: Service description not visible: {node.get('name')}")
        if page.get("faqs") and not any(node.get("@type") == "FAQPage" for node in nodes):
            errors.append(f"{page['path']}: missing FAQPage schema")
        if not page.get("faqs") and any(node.get("@type") == "FAQPage" for node in nodes):
            errors.append(f"{page['path']}: FAQ schema without FAQ content")
        page["_parser"] = parser

    if len(set(titles)) != len(titles):
        errors.append("duplicate titles")
    if len(set(descriptions)) != len(descriptions):
        errors.append("duplicate meta descriptions")

    not_found = {
        "path": "/404.html",
        "file": ROOT / "404.html",
        "title": "Page not found | Country Roads Cleaning Solutions",
        "description": "That page isn’t on the Country Roads Cleaning Solutions site. Call (304) 710-5430 or go back to house cleaning in Kenova and Huntington.",
    }
    # 404 is validated separately below after write; include file map now
    file_for_url = {page["path"]: page["file"] for page, _markup in pages}
    file_for_url["/404.html"] = ROOT / "404.html"
    file_for_url["/quote/"] = ROOT / "quote" / "index.html"
    file_for_url["/apply/"] = ROOT / "apply" / "index.html"

    def page_by_path(path: str):
        for candidate, _markup in pages:
            if candidate["path"] == path:
                return candidate
        return None

    def resolve(url: str, source: str) -> None:
        if url.startswith(("tel:", "mailto:", "https://", "http://")):
            return
        path, _, fragment = url.partition("#")
        if path == "":
            owner = page_by_path(source)
            lookup = source
        elif path == "/":
            owner = page_by_path("/")
            lookup = "/"
        elif path.endswith(".html"):
            owner = None
            lookup = path
        elif path.endswith("/"):
            owner = page_by_path(path)
            lookup = path
        else:
            owner = None
            lookup = path
        target = file_for_url.get(lookup)
        if path == "":
            target = file_for_url.get(source)
        if target is None or not Path(target).exists():
            errors.append(f"{source}: missing target {url}")
            return
        if fragment:
            parser = owner.get("_parser") if owner else None
            if parser and fragment not in parser.ids:
                errors.append(f"{source}: fragment #{fragment} missing on {lookup or source}")

    for page, _markup in pages:
        for href in page["_parser"].hrefs:
            resolve(href, page["path"])

    for markup in [page_markup for _page, page_markup in pages]:
        for srcset in re.findall(r'srcset="([^"]+)"', markup):
            for part in srcset.split(","):
                url = part.strip().split(" ")[0]
                if url.startswith("/") and not (ROOT / url.lstrip("/")).exists():
                    errors.append(f"missing srcset asset {url}")

    asset_refs = re.findall(r'(?:src|href)="(/[^"]+)"', "\n".join(markup for _page, markup in pages))
    for ref in asset_refs:
        if ref.startswith(("tel:",)):
            continue
        path = ref.split("#", 1)[0].split("?", 1)[0]
        if path.startswith("/assets/") or path.startswith("/css/") or path.startswith("/js/") or path in {"/favicon.ico", "/favicon-32.png", "/apple-touch-icon.png"}:
            if not (ROOT / path.lstrip("/")).exists():
                errors.append(f"missing asset {path}")

    print("\nTitles and descriptions:")
    for page, _markup in pages:
        print(f"  {len(page['title']):2}  {len(page['description']):3}  {page['path']}  {page['title']}")

    if errors:
        print("\nVALIDATION FAILED")
        for error in errors:
            print(" -", error)
        sys.exit(1)
    print(f"\nValidated {len(pages)} pages.")


def main() -> None:
    cname = (ROOT / "CNAME").read_text(encoding="utf-8")
    if cname.strip() != "countryroadscleaningsolutions.com":
        sys.exit("CNAME was modified unexpectedly")
    pages = all_content_pages()
    not_found_html = render_404()
    for page, markup in pages:
        write_text(page["file"], markup)
    write_text(ROOT / "404.html", not_found_html)
    write_text(ROOT / "apply" / "index.html", render_apply())
    quote_html = render_quote()
    write_text(ROOT / "quote" / "index.html", quote_html)
    urls = [BASE + page["path"] for page, _markup in pages]
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        sitemap.append("  <url>")
        sitemap.append(f"    <loc>{url}</loc>")
        sitemap.append("    <lastmod>2026-10-24</lastmod>")
        sitemap.append("  </url>")
    sitemap.append("</urlset>")
    write_text(ROOT / "sitemap.xml", "\n".join(sitemap) + "\n")
    write_text(ROOT / "robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://countryroadscleaningsolutions.com/sitemap.xml\n")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    validate(pages)
    # 404 checks that don't belong in the indexable set
    if 'content="MBFMHKZPEH1q2RIueenmKA9H5wVpUnKhdF_wFM3hnpw"' not in not_found_html:
        sys.exit("404 missing Search Console tag")
    if 'noindex' not in not_found_html:
        sys.exit("404 should be noindex")
    if "/404.html" in (ROOT / "sitemap.xml").read_text(encoding="utf-8"):
        sys.exit("404 leaked into the sitemap")
    # /quote/ is an unlisted soft-lead page: noindex, out of the sitemap and menu, no mobile quote bar.
    quote_errors = []
    if '<meta name="robots" content="noindex">' not in quote_html:
        quote_errors.append("missing noindex")
    if "/quote/" in (ROOT / "sitemap.xml").read_text(encoding="utf-8"):
        quote_errors.append("leaked into the sitemap")
    if any(href.startswith("/quote") for href, _label in NAV):
        quote_errors.append("listed in the main menu")
    if 'id="mobile-cta"' in quote_html:
        quote_errors.append("has the mobile quote bar")
    if quote_html.count("<h1") != 1:
        quote_errors.append("h1 count")
    for forbidden in ("Kane", "Katlyn", "Walnut", "1801", "$", "rating", "stars"):
        body = quote_html.split("</head>", 1)[1]
        if forbidden.lower() in body.lower():
            quote_errors.append(f"forbidden term {forbidden}")
    if f'action="https://formsubmit.co/{EMAIL}"' not in quote_html or f'value="{BASE}/quote/?sent=1"' not in quote_html:
        quote_errors.append("FormSubmit action/_next wrong")
    if quote_home_fields() not in quote_form(False) or quote_contact_fields() not in quote_form(False):
        quote_errors.append("fields drifted from the site quote form")
    for line in quote_home_fields("q-").splitlines() + quote_contact_fields("q-").splitlines():
        stripped = line.strip()
        if stripped and stripped not in quote_html:
            quote_errors.append("quiz is missing a shared field: " + stripped[:80])
    if "Question 1 of 9" not in quote_html or 'id="q-form"' not in quote_html:
        quote_errors.append("quiz progress or form missing")
    if quote_html.count('class="quiz-step') != 9:
        quote_errors.append("quiz should have 9 questions")
    if PHONE not in quote_html or "8:00 AM" not in quote_html:
        quote_errors.append("phone/hours not visible")
    home_markup = next(markup for page, markup in pages if page["path"] == "/")
    if 'id="quote-form"' in home_markup or 'class="form-card"' in home_markup:
        quote_errors.append("homepage still embeds the quote form")
    for needle in (
        "You already have plenty on your plate. Let us help with the cleaning.",
        f'Call or text <a href="{TEL}">{PHONE}</a> and tell us a little about the home or business. Then our team can get you a personalized quote.',
        "Monday–Friday, 8:00 AM–5:00 PM. We serve homes and businesses within about 25 miles of Kenova.",
        'id="home-carousel"',
        "/assets/photos/carousel-bedroom-960.jpg",
        "/assets/photos/carousel-bathroom-960.jpg",
        "/assets/photos/carousel-hallway-960.jpg",
        "/assets/photos/carousel-kitchen-960.jpg",
    ):
        if needle not in home_markup:
            quote_errors.append("homepage quote section missing: " + needle[:70])
    if "You don't have to figure out the whole plan before asking for a quote." in home_markup:
        quote_errors.append("homepage still has the old quote paragraph")
    linked = [markup for _page, markup in pages] + [not_found_html, render_apply(), quote_html]
    for blob in linked:
        if 'href="/#quote"' in blob or 'href="#quote"' in blob:
            quote_errors.append("a generated page still links to #quote")
            break
    if quote_errors:
        sys.exit("/quote/ validation failed: " + "; ".join(quote_errors))
    print("Validated /quote/ (noindex, unlisted, no mobile bar, one question at a time, homepage carousel).")
    print("CNAME unchanged:", cname.strip())


if __name__ == "__main__":
    main()
