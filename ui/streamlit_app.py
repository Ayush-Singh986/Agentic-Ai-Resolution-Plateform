import html
import json
import os

import requests
import streamlit as st


api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Incident Desk | AI Ops",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --ink: #18233b;
        --muted: #77829a;
        --violet: #7867f7;
        --blue: #6889ff;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--ink);
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 75% 8%, rgba(174, 184, 255, .34), transparent 32%),
            radial-gradient(ellipse at 13% 68%, rgba(170, 232, 236, .24), transparent 28%),
            #f3f5fb;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1240px;
        padding: 1.5rem 2rem 4rem;
    }

    .topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.25rem;
        color: #68748e;
        font-size: .82rem;
    }
    .wordmark {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #1e2942;
        font-size: .94rem;
        font-weight: 750;
        letter-spacing: -.02em;
    }
    .wordmark-icon {
        display: grid;
        width: 34px;
        height: 34px;
        place-items: center;
        border: 1px solid rgba(255,255,255,.85);
        border-radius: 12px;
        color: white;
        background: linear-gradient(145deg, #8f81ff, #6276ee);
        box-shadow: 0 7px 18px rgba(103,112,230,.27);
    }
    .top-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 11px;
        border: 1px solid rgba(255,255,255,.85);
        border-radius: 999px;
        background: rgba(255,255,255,.56);
        color: #66718a;
        font-size: .73rem;
        backdrop-filter: blur(12px);
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #8f7cff;
        box-shadow: 0 0 0 4px rgba(143,124,255,.13);
    }

    .hero {
        position: relative;
        display: flex;
        min-height: 275px;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        overflow: hidden;
        padding: 2.25rem 2.6rem;
        border: 1px solid rgba(255,255,255,.18);
        border-radius: 28px;
        color: white;
        background:
            radial-gradient(ellipse at 78% 45%, rgba(129,111,255,.38), transparent 32%),
            radial-gradient(ellipse at 95% 0%, rgba(89,159,255,.22), transparent 34%),
            linear-gradient(115deg, #18223b 0%, #222c4a 57%, #292d56 100%);
        box-shadow: 0 24px 64px rgba(34,43,78,.2), inset 0 1px rgba(255,255,255,.16);
        animation: hero-in .65s cubic-bezier(.2,.7,.25,1) both;
    }
    .hero::after {
        position: absolute;
        top: -118px;
        right: 22%;
        width: 320px;
        height: 320px;
        border: 1px solid rgba(211,216,255,.12);
        border-radius: 50%;
        content: "";
        box-shadow: 0 0 0 28px rgba(211,216,255,.035), 0 0 0 58px rgba(211,216,255,.025);
        pointer-events: none;
    }
    @keyframes hero-in {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .hero-copy { position: relative; z-index: 1; max-width: 620px; }
    .hero-kicker {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 1rem;
        color: #c6c6ff;
        font-size: .69rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .hero-kicker span {
        padding: 5px 9px;
        border: 1px solid rgba(206,207,255,.2);
        border-radius: 999px;
        background: rgba(161,153,255,.1);
        letter-spacing: .08em;
    }
    .hero-title {
        max-width: 610px;
        margin: 0;
        color: #fff !important;
        font-size: clamp(2.2rem, 4.5vw, 3.65rem);
        font-weight: 760;
        letter-spacing: -.065em;
        line-height: 1.03;
        -webkit-text-fill-color: #fff;
    }
    .hero-title em {
        color: #b5aaff;
        font-style: normal;
        -webkit-text-fill-color: #b5aaff;
    }
    .hero-description {
        max-width: 500px;
        margin: 1rem 0 0;
        color: #bbc4dc;
        font-size: .94rem;
        line-height: 1.65;
    }
    .hero-graphic {
        position: relative;
        z-index: 1;
        display: grid;
        width: 188px;
        height: 188px;
        flex: 0 0 188px;
        place-items: center;
        border: 1px solid rgba(225,228,255,.2);
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, rgba(188,181,255,.22), rgba(119,123,255,.055) 55%, transparent 72%);
        box-shadow: 0 0 0 16px rgba(230,232,255,.035), inset 0 1px rgba(255,255,255,.12);
        animation: float 5s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-7px); }
    }
    .orb-core {
        display: grid;
        width: 82px;
        height: 82px;
        place-items: center;
        border: 1px solid rgba(255,255,255,.32);
        border-radius: 27px;
        color: white;
        background: linear-gradient(145deg, rgba(177,163,255,.85), rgba(99,126,255,.82));
        box-shadow: 0 12px 36px rgba(124,119,255,.38), inset 0 1px rgba(255,255,255,.55);
        font-size: 2.2rem;
        transform: rotate(-9deg);
    }
    .orb-spark {
        position: absolute;
        top: 30px;
        right: 28px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #b6f5e7;
        box-shadow: 0 0 18px #8ce8df;
    }
    .orb-spark.second {
        top: auto;
        right: auto;
        bottom: 33px;
        left: 23px;
        width: 6px;
        height: 6px;
        background: #ffd997;
        box-shadow: 0 0 14px #ffd997;
    }

    .workflow-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 14px 0 24px;
    }
    .workflow-chip {
        display: flex;
        align-items: center;
        gap: 12px;
        min-height: 62px;
        padding: 11px 15px;
        border: 1px solid rgba(255,255,255,.82);
        border-radius: 17px;
        background: rgba(255,255,255,.49);
        box-shadow: 0 9px 25px rgba(52,64,105,.055), inset 0 1px rgba(255,255,255,.9);
        backdrop-filter: blur(16px);
        transition: transform .2s ease, background .2s ease, box-shadow .2s ease;
    }
    .workflow-chip:hover {
        transform: translateY(-3px);
        background: rgba(255,255,255,.78);
        box-shadow: 0 15px 30px rgba(52,64,105,.1);
    }
    .step-number {
        display: grid;
        width: 32px;
        height: 32px;
        flex: 0 0 32px;
        place-items: center;
        border-radius: 11px;
        color: #6359d6;
        background: #eeedff;
        font-size: .73rem;
        font-weight: 750;
    }
    .step-name { color: #29344c; font-size: .83rem; font-weight: 700; }
    .step-detail { margin-top: 2px; color: #828ca1; font-size: .72rem; }

    .st-key-incident-card, .st-key-process-card {
        padding: 1.45rem 1.5rem;
        border: 1px solid rgba(255,255,255,.9);
        border-radius: 24px;
        background: linear-gradient(145deg, rgba(255,255,255,.8), rgba(255,255,255,.53));
        box-shadow: 0 18px 48px rgba(49,63,108,.09), inset 0 1px rgba(255,255,255,.95);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
        transition: transform .22s ease, box-shadow .22s ease;
    }
    .st-key-incident-card:hover, .st-key-process-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 25px 54px rgba(49,63,108,.13), inset 0 1px white;
    }
    .card-kicker {
        margin-bottom: .35rem;
        color: #7166e8;
        font-size: .67rem;
        font-weight: 750;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .card-title {
        margin: 0 0 .35rem;
        color: #202b43;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: -.04em;
    }
    .card-copy { color: #7b869b; font-size: .84rem; line-height: 1.55; }
    .sample-heading { margin: 1.1rem 0 .42rem; color: #77829a; font-size: .74rem; font-weight: 650; }
    [data-testid="stWidgetLabel"] p, label {
        color: #35415a !important;
        font-size: .82rem !important;
        font-weight: 650 !important;
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        border: 1px solid rgba(205,213,230,.9);
        border-radius: 12px;
        background: rgba(255,255,255,.72);
        color: #202b43;
        transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
    }
    [data-testid="stTextInput"] input:hover, [data-testid="stTextArea"] textarea:hover {
        border-color: #a9a1f6;
        background: #fff;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: #887cf0;
        box-shadow: 0 0 0 3px rgba(120,103,247,.14);
    }
    [data-testid="stTextArea"] textarea { min-height: 150px; }
    [data-testid="stButton"] button {
        min-height: 40px;
        border: 1px solid rgba(255,255,255,.95);
        border-radius: 12px;
        background: rgba(255,255,255,.65);
        color: #4b4e83;
        font-size: .8rem;
        font-weight: 650;
        transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
    }
    [data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        border-color: #fff;
        background: white;
        color: #554bd1;
        box-shadow: 0 8px 20px rgba(75,76,148,.11);
    }
    [data-testid="stFormSubmitButton"] button {
        min-height: 49px;
        border: 0;
        border-radius: 13px;
        color: white;
        background: linear-gradient(105deg, #6f68ed, #7771f3 53%, #5e8af5);
        box-shadow: 0 10px 22px rgba(105,103,235,.27), inset 0 1px rgba(255,255,255,.3);
        font-weight: 700;
        transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px);
        border: 0;
        color: white;
        filter: saturate(1.18);
        box-shadow: 0 15px 28px rgba(105,103,235,.35), inset 0 1px rgba(255,255,255,.35);
    }
    [data-testid="stFormSubmitButton"] button:disabled {
        color: rgba(255,255,255,.8);
        background: #a9add0;
        box-shadow: none;
    }

    .insight-card {
        position: relative;
        overflow: hidden;
        padding: 1.45rem;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 24px;
        color: white;
        background:
            radial-gradient(ellipse at 100% 0%, rgba(129,112,255,.26), transparent 45%),
            linear-gradient(145deg, #202a45, #2d3158);
        box-shadow: 0 18px 44px rgba(39,48,83,.17), inset 0 1px rgba(255,255,255,.12);
        transition: transform .22s ease, box-shadow .22s ease;
    }
    .insight-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 24px 52px rgba(39,48,83,.23), inset 0 1px rgba(255,255,255,.16);
    }
    .insight-label {
        color: #b8b5ff;
        font-size: .66rem;
        font-weight: 750;
        letter-spacing: .15em;
        text-transform: uppercase;
    }
    .insight-title {
        margin: .45rem 0 .45rem;
        color: white;
        font-size: 1.28rem;
        font-weight: 700;
        letter-spacing: -.04em;
    }
    .insight-copy { color: #b8c1d8; font-size: .82rem; line-height: 1.6; }
    .signal-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 18px;
        padding: 11px 12px;
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 14px;
        background: rgba(255,255,255,.055);
        color: #e1e6f4;
        font-size: .77rem;
    }
    .signal-icon {
        display: grid;
        width: 28px;
        height: 28px;
        flex: 0 0 28px;
        place-items: center;
        border-radius: 9px;
        color: #d6d2ff;
        background: rgba(153,140,255,.17);
    }
    .result-heading {
        margin: 1.8rem 0 .8rem;
        color: #202b43;
        font-size: 1.4rem;
        font-weight: 740;
        letter-spacing: -.045em;
    }
    [data-testid="stMetric"] {
        padding: 14px 16px;
        border: 1px solid rgba(255,255,255,.88);
        border-radius: 16px;
        background: rgba(255,255,255,.66);
        box-shadow: 0 10px 24px rgba(49,63,108,.07);
        backdrop-filter: blur(14px);
    }
    [data-testid="stMetricLabel"] { color: #77829a; }
    [data-testid="stMetricValue"] { color: #27334d; }
    [data-testid="stAlert"] { border-radius: 14px; }
    .result-card {
        min-height: 100px;
        padding: 1.3rem 1.45rem;
        border: 1px solid rgba(255,255,255,.9);
        border-radius: 20px;
        background: rgba(255,255,255,.66);
        box-shadow: 0 12px 28px rgba(49,63,108,.07);
        backdrop-filter: blur(16px);
        color: #35415a;
        line-height: 1.65;
    }

    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 3rem; }
        .hero { min-height: 0; padding: 1.6rem; }
        .hero-graphic { width: 92px; height: 92px; flex-basis: 92px; }
        .orb-core { width: 54px; height: 54px; border-radius: 18px; font-size: 1.55rem; }
        .workflow-strip { gap: 7px; }
        .workflow-chip { padding: 9px 8px; gap: 7px; }
        .step-detail { display: none; }
        .step-name { font-size: .72rem; }
    }
    @media (max-width: 520px) {
        .hero-graphic { display: none; }
        .top-pill { font-size: .65rem; }
        .workflow-strip { grid-template-columns: 1fr; }
        .workflow-chip { min-height: 48px; }
        .step-detail { display: block; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topline">
        <div class="wordmark"><span class="wordmark-icon">✳</span> Incident Desk</div>
        <div class="top-pill"><span class="pulse-dot"></span> AI INCIDENT ANALYST</div>
    </div>
    <section class="hero">
        <div class="hero-copy">
            <div class="hero-kicker">OPERATIONS INTELLIGENCE <span>INCIDENT WORKSPACE</span></div>
            <h1 class="hero-title">Turn incidents<br>into <em>understanding.</em></h1>
            <p class="hero-description">
                Bring the symptoms. Get a clear first read on severity, likely cause,
                and what your team can investigate next.
            </p>
        </div>
        <div class="hero-graphic" aria-hidden="true">
            <div class="orb-core">✳</div>
            <span class="orb-spark"></span>
            <span class="orb-spark second"></span>
        </div>
    </section>
    <div class="workflow-strip">
        <div class="workflow-chip"><span class="step-number">01</span><div><div class="step-name">Triage</div><div class="step-detail">Severity + domain</div></div></div>
        <div class="workflow-chip"><span class="step-number">02</span><div><div class="step-name">Investigate</div><div class="step-detail">Relevant knowledge</div></div></div>
        <div class="workflow-chip"><span class="step-number">03</span><div><div class="step-name">Recommend</div><div class="step-detail">Cause + next steps</div></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)


def load_sample(incident_id, title, description):
    st.session_state["incident_id"] = incident_id
    st.session_state["title"] = title
    st.session_state["description"] = description


form_column, insight_column = st.columns([1.35, 0.8], gap="medium")

with form_column:
    with st.container(key="incident-card"):
        st.markdown('<div class="card-kicker">Start an investigation</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">What’s happening?</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-copy">Add a few details. Your analyst will help connect the dots.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sample-heading">NEED A STARTING POINT? &nbsp; TRY A SAMPLE</div>', unsafe_allow_html=True)
        sample_columns = st.columns(2)
        sample_columns[0].button(
            "↗  Payment API",
            on_click=load_sample,
            args=(
                "INC-2048",
                "Payment API timeouts after deployment",
                "Payment requests began timing out shortly after the latest deployment. "
                "Customers are unable to complete transactions.",
            ),
            use_container_width=True,
        )
        sample_columns[1].button(
            "↗  Database latency",
            on_click=load_sample,
            args=(
                "INC-2051",
                "Database latency spike",
                "Database query latency increased sharply and several services are "
                "reporting intermittent connection timeouts.",
            ),
            use_container_width=True,
        )
        with st.form("incident_form"):
            incident_id = st.text_input("Incident ID", placeholder="e.g. INC-2048", key="incident_id")
            title = st.text_input(
                "Title",
                placeholder="e.g. Payment API timeouts after deployment",
                key="title",
            )
            description = st.text_area(
                "Describe the symptoms",
                placeholder="What changed? When did it start? What are users experiencing?",
                help="Avoid including passwords, access tokens, or other secrets.",
                key="description",
            )
            submitted = st.form_submit_button("✦   Analyze incident")

with insight_column:
    st.markdown(
        """
        <div class="insight-card">
            <div class="insight-label">YOUR AI ANALYST</div>
            <div class="insight-title">A clearer first read.</div>
            <div class="insight-copy">One incident report becomes a focused starting point for your response.</div>
            <div class="signal-row"><span class="signal-icon">◈</span><span>Classifies impact and service domain</span></div>
            <div class="signal-row"><span class="signal-icon">⌕</span><span>Finds context from your knowledge base</span></div>
            <div class="signal-row"><span class="signal-icon">↗</span><span>Suggests a cause and next steps</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = None

if submitted:
    if not all((incident_id.strip(), title.strip(), description.strip())):
        st.session_state.analysis_result = None
        st.session_state.analysis_error = "Enter an incident ID, title, and description to continue."
    else:
        payload = {
            "incident_id": incident_id.strip(),
            "title": title.strip(),
            "description": description.strip(),
        }
        try:
            response = requests.post(
                f"{api_base_url}/incident",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            st.session_state.analysis_result = response.json()
            st.session_state.analysis_error = None
        except requests.exceptions.JSONDecodeError as exc:
            st.session_state.analysis_result = None
            st.session_state.analysis_error = f"The incident API returned invalid JSON: {exc}"
        except requests.RequestException as exc:
            st.session_state.analysis_result = None
            st.session_state.analysis_error = f"Could not reach the incident API: {exc}"

if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error)

result = st.session_state.analysis_result
if result:
    root_cause = html.escape(result.get("root_cause") or "No root cause was returned.")
    plan = result.get("remediation_plan") or []
    remediation_plan = (
        "<br>".join(
            f"{index}. {html.escape(str(step))}"
            for index, step in enumerate(plan, start=1)
        )
        if isinstance(plan, list)
        else html.escape(str(plan))
    )
    st.markdown('<div class="result-heading">Analysis overview</div>', unsafe_allow_html=True)
    metric_columns = st.columns(3)
    metric_columns[0].metric("Severity", result.get("severity", "—"))
    metric_columns[1].metric("Domain", result.get("domain", "—"))
    confidence = result.get("confidence_score")
    metric_columns[2].metric(
        "Confidence",
        f"{confidence:.0%}" if isinstance(confidence, (int, float)) else "—",
    )

    result_left, result_right = st.columns([1.2, 0.8], gap="medium")
    with result_left:
        st.markdown('<div class="card-kicker">ROOT CAUSE</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-card">{root_cause}</div>',
            unsafe_allow_html=True,
        )
    with result_right:
        st.markdown('<div class="card-kicker">RECOMMENDED NEXT STEPS</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-card">{remediation_plan}</div>',
            unsafe_allow_html=True,
        )
    st.warning(
        "Recommendations are advisory only. A human must review them; "
        "this application does not execute remediation."
    )
    evidence = result.get("evidence") or []
    with st.expander("View retrieved knowledge-base evidence"):
        if evidence:
            for item in evidence:
                st.markdown(f"- {item}")
        else:
            st.info("No matching knowledge-base evidence was retrieved.")
    ticket_draft = result.get("ticket_draft")
    if ticket_draft:
        st.download_button(
            "Download local ticket draft (JSON)",
            data=json.dumps(ticket_draft, indent=2),
            file_name=f"{result.get('incident_id', 'incident')}-ticket-draft.json",
            mime="application/json",
        )
    with st.expander("View full analysis response"):
        st.json(result)
