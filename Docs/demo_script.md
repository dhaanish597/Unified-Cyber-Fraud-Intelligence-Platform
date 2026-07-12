# FinSpark'26 Demo Script
**Title**: Unified Cyber-Fraud Intelligence Platform
**Duration**: 90 seconds
**Speaker**: Lead Presenter

---

## 🎬 T-0:00 (Setup & Calm)
*Action: Start the "Play Demo" on the Live Monitor tab. The dashboard is completely green and calm. TPS is normal.*

**Voiceover:**
> "Welcome to the Unified Cyber-Fraud Intelligence Platform. Right now, you're looking at a live, calm SOC dashboard. On the left, we ingest raw SIEM events—logins, device changes. On the right, our core transaction ledger. Notice the Threat Level is currently normal."

---

## 🚨 T+0:00 (Cyber Compromise Event)
*Action: The SIEM timeline fires a CRITICAL 'impossible_travel_login' for `usr_abc` from a brand new IP/device, over 4,500 km away from their baseline.*

**Voiceover:**
> "Suddenly, our SIEM detects a critical anomaly—an impossible travel login for User ABC from an unrecognized device. Traditionally, the fraud prevention team wouldn't see this alert until tomorrow morning's report. We've logged it instantly, but there's no money moving yet."

---

## 💸 T+0:40 (The Transaction)
*Action: A massive ₹7,50,000 UPI transfer from `usr_abc` to a new beneficiary (`ACC_MULE_NEW`) pops into the Transaction Ledger.*

**Voiceover:**
> "Just 40 seconds later, User ABC attempts a massive 7.5 lakh Rupee UPI transfer to a brand-new beneficiary."

---

## 🛑 T+0:41 (Fusion Engine BLOCK & Threat Graph)
*Action: The central verdict badge flashes red, screaming 'BLOCK' with a score of 94/100. The Threat Graph visualizer instantly expands, showing `usr_abc` linked to `ACC_MULE_NEW`, which spiderwebs out to 6 other known mule accounts.*

**Voiceover:**
> "In under a second, our Fusion Risk Engine intervenes. It doesn't just see a high-value transfer—it fused the cyber context of the compromised login with the transaction itself, jumping the risk score to 94 and blocking the transfer mid-flight. Furthermore, our graph engine instantly mapped the destination account to a known 6-node mule cluster."

---

## 🧠 T+0:55 (XAI & Counterfactual)
*Action: Direct attention to the XAI panel at the bottom. Highlight the SHAP top features and the Counterfactual sentence.*

**Voiceover:**
> "Why exactly was it blocked? Our Explainable AI panel gives the exact feature breakdown. More importantly, check the Quantum-Ready Counterfactual at the bottom: Without that prior cyber compromise, the tabular score alone was just a 61—meaning this would have been allowed or merely challenged by a legacy fraud system. Fusion is what caught it."

---

## 📄 T+1:10 (CERT-In Report)
*Action: Click the glowing red 'Generate CERT-In Report' button inside the Verdict Badge. The PDF downloads immediately.*

**Voiceover:**
> "Because this is a verified breach, we need to meet the 6-hour CERT-In mandate. One click, and a fully compliant, timestamped incident PDF is generated and ready for the regulator."

---

## 🔐 T+1:25 (Quantum Monitor & HNDL)
*Action: Click the 'Quantum Posture' tab at the top. The gauge displays the vulnerable percentage and flags a massive red HNDL alert.*

**Voiceover:**
> "Finally, let's look at the future. Clicking into our Quantum Posture tab, we actively monitor TLS handshakes for quantum vulnerabilities. We can see that the compromised session for User ABC used an aging ECDHE cipher. Because sensitive financial data was intercepted, our system explicitly flags this as a Harvest-Now-Decrypt-Later, or HNDL, risk, warning our security teams of future exposure."
> 
> "This is proactive, quantum-aware, unified intelligence. Thank you."
