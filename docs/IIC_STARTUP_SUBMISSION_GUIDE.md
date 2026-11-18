# RAKSHA-NET: IIITDM Jabalpur IIC Incubation Application & 5-Slide Pitch Guide
*(2024–2026 Market Intelligence & Defense-Grounded Edition)*

> **Target Body:** Institute Innovation & Incubation Centre (IIC), PDPM IIITDM Jabalpur  
> **Scheme:** Startup Incubation & B.Tech Startup Semester Conversion  
> **Deadline:** 15 November 2026  
> **Submission Link:** [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSc3AET6rwluHIYyYNaPKSPLUWuoiUAiCdZoD0eluL4MMT5h1g/viewform)  
> **Generated PPT Deck:** [`raksha-net/results/raksha_net_iic_5slide_presentation.pptx`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/results/raksha_net_iic_5slide_presentation.pptx)  
> **Faculty Mentor:** Dr. Satish Kumar Tiwari, Assistant Professor, Department of ECE, PDPM IIITDM Jabalpur  
> **Student Founders:**  
> - **G Rahul Reddy** — Roll No: `24BEC038` (2nd Year B.Tech, ECE) | `24bec038@iiitdmj.ac.in`  
> - **Rajarwar Deependra Sahebrao** — Roll No: `22BCS220` (3rd Year B.Tech, CSE) | `22bcs220@iiitdmj.ac.in`

---

## 1. Grounded Market Intelligence & Real-World Precedents (2024–2026)

When the IIC faculty jury asks, *"Why now? What is the actual market demand?"*, you have real, verified data points to back your pitch:

### A. Real Battlefield Precedents (Why Rigid Satellite Hardware Fails):
1. **The Viasat KA-SAT Sabotage ("AcidRain Wiper", Feb 2022):** Tens of thousands of fixed satellite modems were permanently bricked on the first morning of the Ukraine war, paralyzing military command and control. Proves fixed-frequency, non-agile hardware is vulnerable.
2. **Dense Russian EW Jamming:** Systems like *Zhitel* and *Tirada-2S* blanket frontline areas. A RUSI defense study documented up to **10,000 Ukrainian UAVs lost per month** due to RF jamming and GPS spoofing.
3. **Starlink's Software-Defined Agility:** SpaceX defeated jamming not by replacing hardware, but by pushing rapid software updates for dynamic frequency-hopping and beam null-steering—the exact software-defined agility RAKSHA-NET introduces for 5G NTN.

### B. The Cryptographic Deadline ("Harvest Now, Decrypt Later"):
1. **NIST Milestone (August 13, 2024):** NIST officially released finalized post-quantum standards: **FIPS 203 (ML-KEM)**, FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA).
2. **NSA CNSA 2.0 Timeline:** Mandates post-quantum algorithm support for networking gear, routers, and gateways by **2026**, deprecating classical RSA/ECC completely by **2030**.
3. **Orbital Lifetime Reality:** Satellites designed and launched today have 7–15 year operational lifetimes. A satellite launched today without ML-KEM post-quantum key exchange will be cryptographically compromised while still in orbit.

### C. Market Projections & CAGRs (2024–2032):
- **5G Non-Terrestrial Networks (NTN):** Growing from **$4.2B (2024) to $23.5B (2030)** at an explosive **33.2% CAGR** (driven by 3GPP Rel-17/18 satellite convergence).
- **Global Military SATCOM + Tactical Comms (TAM):** Projected to reach **$41.3 Billion** ($16.5B MILSATCOM + $24.8B Tactical Comms) by 2030–2032.
- **Indian Market Opportunity (SOM):** **$450 Million – $800 Million** over 5 years across Indian Armed Forces modernization and commercial NewSpace LEO CubeSats (IN-SPACe).

### D. Specific Indian Defense & Space Funding Pipelines:
- **iDEX (Innovations for Defence Excellence) DISC:** Grants-in-Aid up to **₹1.5 Crore** (zero equity).
- **iDEX ADITI Scheme (DefConnect 2024, ₹750 Cr corpus):** Grants up to **₹25 Crore** for strategic defense deep-tech (secure tactical satellite transceivers & quantum-safe encryption).
- **DRDO Technology Development Fund (TDF):** Enhanced to **₹50 Crore** for indigenous military component replacements.
- **IN-SPACe Seed Fund Scheme:** Grants up to **₹1 Crore** for CubeSat payloads & communication subsystems.
- **DST NIDHI-PRAYAS (via IIITDM Jabalpur IIC):** Prototyping grant up to **₹10 Lakhs** for student hardware.

---

## 2. Google Form Submission Text (Copy-Paste Ready)

### Startup / Idea Name:
```text
RAKSHA-NET: Quantum-Resilient Autonomous Controller for 5G NTN & Satellite Links
```

### Faculty Mentor (Mandatory Field):
```text
Dr. Satish Kumar Tiwari
Assistant Professor, Department of Electronics & Communication Engineering
PDPM IIITDM Jabalpur
```

### Short Description of the Idea (What problem it solves and how):
```text
OPERATIONAL PROBLEM:
Recent global conflicts (e.g., Ukraine and the Red Sea) have exposed two critical vulnerabilities in satellite and tactical communications:
1. Active RF Jamming: Dense Electronic Warfare (EW) jamming collapses packet delivery ratio (PDR) down to ~32%, with traditional static routing taking minutes or human intervention to recover.
2. "Harvest Now, Decrypt Later" (HNDL): Hostile nation-states actively archive encrypted military satellite signals today. Following NIST's official release of FIPS 203 (ML-KEM) in August 2024 and the NSA CNSA 2.0 mandate enforcing post-quantum router support by 2026, satellites launched without post-quantum crypto today will be decrypted in orbit once quantum computing scales.
3. Import Dependency: Indian defense spends crores on imported, proprietary cryptographic hardware appliances (₹40L–₹1Cr+ per box) that are too heavy for drones and carry foreign supply-chain risks.

OUR SOLUTION & HOW IT WORKS:
RAKSHA-NET is an indigenous, 100% software-defined autonomous controller that integrates routing resilience and post-quantum security into a closed-loop engine on standard computing hardware:
- Live Sensing: Continuously monitors latency, jitter, loss, and queue depths from an active 5G Core tunnel interface (ogstun).
- Sub-Second Rerouting: An anomaly engine detects RF jamming (a_t >= 0.60), decays Bayesian trust, and autonomously migrates traffic to a healthy satellite relay in 190 milliseconds with zero route flapping (delivering a +64.5% net PDR gain).
- NIST FIPS 203 Cryptography: Concurrently executes ML-KEM-768 in native C liboqs, establishing quantum forward secrecy in just 0.065 ms (65 microseconds, 3x faster than classical ECC) while programmatically quarantining the compromised relay.

LAB VERIFICATION & TRACTION:
Fully verified on an active 3GPP Release-17 Open5GS core with 17 running daemons and native C liboqs, passing all 53 automated unit tests with 100% reliability.

NEXT STEPS & INCUBATION OBJECTIVE:
Under the mentorship of Dr. Satish Kumar Tiwari (Dept. of ECE), our 6-month goal is to move from software emulation to a physical over-the-air Software-Defined Radio (HackRF / ADALM-Pluto) and Raspberry Pi 5 testbed in the college lab, and apply for the B.Tech Startup Semester.
```

### Target Market & Revenue Model:
```text
- Market: 5G Non-Terrestrial Networks (growing at 33.2% CAGR to $23.5B by 2030) and Tactical SATCOM ($41.3B TAM). Target customers include Indian Armed Forces tactical 5G, DRDO, and Indian NewSpace CubeSat operators (IN-SPACe).
- Revenue Model: Software-defined containerized licensing per satellite/gNodeB relay, and non-dilutive defense grants (iDEX DISC up to ₹1.5 Cr, iDEX ADITI up to ₹25 Cr, DRDO TDF up to ₹50 Cr).
```

### Support Requested from IIC & Startup Semester Ask:
```text
1. Incubation space and access to communication & signal processing laboratory facilities under Faculty Mentor Dr. Satish Kumar Tiwari.
2. Endorsement for institute prototyping seed grants (NIDHI-PRAYAS / TIDE 2.0) for an entry-level hardware budget (~₹90,000 for 2x HackRF/PlutoSDRs and 2x Raspberry Pi 5 boards).
3. Approval for official B.Tech Startup Semester conversion for 2nd and 3rd year founders.
```

---

## 3. Spoken 5-Minute Script for the IIC Presentation

### Slide 1: Introduction & Identity (0:00 – 1:00)
> *"Respected IIC committee members and faculty mentors, good morning.  
> We are Rahul Reddy (2nd year ECE) and Deependra Rajarwar (3rd year CSE) from IIITDM Jabalpur, working under the mentorship of Dr. Satish Kumar Tiwari. Today, we present **RAKSHA-NET**: an indigenous software controller that preserves communication availability and quantum-safe security for 5G Non-Terrestrial and defense satellite networks.  
> Modern military communications face a dual crisis: aggressive Electronic Warfare jamming and the Harvest Now Decrypt Later quantum threat. Instead of relying on expensive foreign hardware boxes, we built a 100% software-defined controller that restores link delivery from 32% back to 97% in 190 milliseconds, while rekeying sessions with NIST FIPS 203 post-quantum cryptography in under one millisecond.  
> We have verified this on a live 5G Core in our lab, and we are applying for IIC incubation and the Startup Semester to test it on physical Software-Defined Radios."*

### Slide 2: Real Defense Need & Battlefield Lessons (1:00 – 2:00)
> *"Why is RAKSHA-NET urgently needed today? Look at lessons from recent conflicts:  
> First, on the opening day of the Ukraine conflict, the Viasat AcidRain wiper attack knocked out tens of thousands of satellite terminals, blinding military command. A RUSI study documented up to 10,000 UAVs lost per month to Russian jamming complexes like Zhitel and Tirada-2S. SpaceX defeated this not by swapping hardware, but by pushing rapid software-defined updates for frequency hopping and null-steering. That software-first resilience is what RAKSHA-NET brings to 5G NTN.  
> Second, nation-states are executing 'Harvest Now, Decrypt Later' espionage today. Because defense intelligence has a 10-to-30 year lifespan, NIST officially released FIPS 203 ML-KEM in August 2024, and the NSA CNSA 2.0 timeline mandates post-quantum router support by 2026. A satellite launched today without ML-KEM is practically obsolete in orbit.  
> Third, India spends crores on imported hardware appliances that carry foreign backdoor risks. We replace that with an indigenous, containerized software controller."*

### Slide 3: How RAKSHA-NET Works (2:00 – 3:00)
> *"RAKSHA-NET operates as a closed 4-pillar loop on standard computing hardware:  
> 1. Telemetry Sensing: It continuously reads latency, jitter, loss, and queue depths directly from the live 5G Core tunnel interface `ogstun`.  
> 2. Anomaly Detection: An EWMA anomaly engine detects RF jamming when deviations exceed 0.60 in under 100 milliseconds.  
> 3. Zero-Trust Routing: Bayesian trust on the attacked link decays, and our multi-criteria engine autonomously shifts traffic to a healthy satellite in 190 milliseconds. Our 5% hysteresis margin prevents route flapping.  
> 4. Post-Quantum Rekeying: Simultaneously, the controller invokes NIST FIPS 203 ML-KEM-768 in native C, rekeying the session in 0.48 milliseconds and isolating the compromised link.  
> The entire controller requires under 60 megabytes of memory and runs inside standard Linux containers."*

### Slide 4: Real Lab Measurements & Validation (3:00 – 4:00)
> *"Here are our empirical lab results:  
> Our 5G Core is live Open5GS with 17 active daemons running on Linux. Our Post-Quantum Cryptography is compiled native C code running real NIST ML-KEM-768. The satellite RF interference was shaped using Linux kernel traffic control (`tc netem`).  
> In our 10-trial benchmark:  
> - Without our controller, static routing collapses to 32.3% PDR and flatlines.  
> - With RAKSHA-NET, traffic dips momentarily during its 190ms reaction window and immediately recovers to 96.8%—a net gain of **+64.5% packet delivery** ($p = 5.6 \times 10^{-15}$).  
> - We have debunked the myth that post-quantum crypto is too heavy: pure NIST ML-KEM-768 key encapsulation takes just **65 microseconds**—three times faster than classical elliptic curve cryptography!  
> - All 53 automated unit tests pass with 100% reliability."*

### Slide 5: Market Opportunity, Defense Grants & Lab Roadmap (4:00 – 5:00)
> *"To commercialize RAKSHA-NET, we are targeting a $41.3 Billion global defense communications market, with 5G Non-Terrestrial Networks growing at 33.2% CAGR to $23.5B by 2030.  
> The Indian Ministry of Defence has instituted aggressive non-dilutive funding: from iDEX DISC grants of up to ₹1.5 Crore to the newly launched ADITI scheme providing up to ₹25 Crore for quantum-safe tactical transceivers, and DRDO's enhanced ₹50 Crore Technology Development Fund.  
> Our 6-month lab roadmap under Dr. Satish Kumar Tiwari is completely feasible: with an entry hardware budget under ₹1 Lakh, we will procure two HackRF Software-Defined Radios, port the controller to a Raspberry Pi 5, and demonstrate live over-the-air failover with an open-source srsRAN 5G basestation.  
> We are seeking incubation at IIC IIITDM Jabalpur, mentorship under Dr. Satish Kumar Tiwari, endorsement for NIDHI-PRAYAS prototyping support, and approval for the Startup Semester to build a sovereign defense deep-tech startup. Thank you!"*
