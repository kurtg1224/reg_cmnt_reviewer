import os
import pandas as pd

os.makedirs("data", exist_ok=True)

rows = [
    {
        "UID": 1,
        "submitter_name": "Alex P",
        "date": "2025-08-15",
        "comment": "I support yearly reviews. We need to be careful with public funds, and more frequent checks help ensure continued eligibility."
    },
    {
        "UID": 2,
        "submitter_name": "Maria R",
        "date": "2025-08-16",
        "comment": "Opposed. Annual paperwork and medical appointments are a heavy burden for disabled recipients, especially those with fluctuating conditions."
    },
    {
        "UID": 3,
        "submitter_name": "Jordan K",
        "date": "2025-08-16",
        "comment": "The cost of conducting yearly reviews seems excessive. The money and staff time could be better used improving initial determinations."
    },
    {
        "UID": 4,
        "submitter_name": "Taylor S",
        "date": "2025-08-17",
        "comment": "I like the proposal. More frequent reviews will reduce fraud and make sure the program stays sustainable."
    },
    {
        "UID": 5,
        "submitter_name": "Jane Doe",
        "date": "2025-08-17",
        "comment": "Please contact me at jane.doe@example.com or (555) 010-2000. I think annual reviews might be okay if forms are simplified."
    },
    {
        "UID": 6,
        "submitter_name": "Chris L",
        "date": "2025-08-18",
        "comment": "My neighbor John was born 02/10/1970 and has multiple conditions. Yearly reviews would be extremely stressful and confusing for him."
    },
    {
        "UID": 7,
        "submitter_name": "Sam F",
        "date": "2025-08-18",
        "comment": "As an SSA field office employee, I use PCOM and MCS daily. From what I’ve seen, yearly reviews will flood offices with more cases than we can handle."
    },
    {
        "UID": 8,
        "submitter_name": "Lee W",
        "date": "2025-08-19",
        "comment": "This is a cruel, idiotic policy that punishes people for being disabled. It’s harsh and out of touch."
    },
    {
        "UID": 9,
        "submitter_name": "Priya N",
        "date": "2025-08-19",
        "comment": "Rural recipients may struggle to find transportation to annual evaluations. Consider telehealth or allowing a two-year cadence."
    },
    {
        "UID": 10,
        "submitter_name": "Omar H",
        "date": "2025-08-19",
        "comment": "Doctors are already booked months out. Requiring yearly assessments could delay care and increase system bottlenecks."
    },
    # Additional examples to cover all categories and theme scenarios
    # PII-focused (explicit identifiers)
    {
        "UID": 11,
        "submitter_name": "Nina Q",
        "date": "2025-08-20",
        "comment": "You can reach me at 202-555-0175, SSN 123-45-6789, and my bank account is 000123456789 at Test Bank. I want to discuss my eligibility."
    },
    # Third-party personal information
    {
        "UID": 12,
        "submitter_name": "Parent Advocate",
        "date": "2025-08-20",
        "comment": "My daughter, Emily Carter, born 2012-03-05, has autism. Her pediatrician Dr. Lee (555-014-2222) says annual reviews would be disruptive to her therapy schedule."
    },
    # SSA employee/contractor reference
    {
        "UID": 13,
        "submitter_name": "FO Employee",
        "date": "2025-08-20",
        "comment": "I’m an SSA disability examiner; my ssa.gov email is firstname.lastname@ssa.gov. Our systems (PCOM/eView) already lag; annual reviews will overwhelm our queues."
    },
    # Offensive language variants (5 different forms)
    # Threatening tone
    {
        "UID": 14,
        "submitter_name": "Anon1",
        "date": "2025-08-21",
        "comment": "Push this garbage through and you’ll regret it. I’ll show up at your meetings and make sure you hear from me every single day."
    },
    # Profanity
    {
        "UID": 15,
        "submitter_name": "Anon2",
        "date": "2025-08-21",
        "comment": "This rule is a stupid, damn idea. It’s a total waste of time and money and it screws people over."
    },
    # Dehumanizing/derogatory toward a group (no slurs used)
    {
        "UID": 16,
        "submitter_name": "Anon3",
        "date": "2025-08-21",
        "comment": "People who wrote this are parasites on the public. You treat claimants like trash with this nonsense."
    },
    # Vulgar/abusive insults
    {
        "UID": 17,
        "submitter_name": "Anon4",
        "date": "2025-08-21",
        "comment": "Whoever drafted this needs to get their head out of the sand. It’s an obnoxious, insulting proposal and you should be ashamed."
    },
    # Harsh, targeted offensive language (without explicit slurs)
    {
        "UID": 18,
        "submitter_name": "Anon5",
        "date": "2025-08-21",
        "comment": "This is cruel policy. Only a bunch of heartless bureaucrats would dream this up and dump it on disabled folks."
    },
    # Long personal story with single theme at the end
    {
        "UID": 19,
        "submitter_name": "Story Teller",
        "date": "2025-08-22",
        "comment": "I’ve been on benefits for years after a workplace injury. My weeks revolve around appointments, paperwork, and managing pain. The last time I had to update records, it took three trips, two appeals, and months of anxiety about losing rent money. My spouse takes off work to drive me, and we scramble to find childcare. I volunteer at a food pantry when I can, and any extra paperwork means I miss those days. After all this, the main point is simple: please reduce the review frequency or simplify forms dramatically because the current burden is too much."
    },
    # Professional letter with 5 distinct arguments
    {
        "UID": 20,
        "submitter_name": "House Committee Staff",
        "date": "2025-08-22",
        "comment": (
            "On behalf of the Committee, we oppose the proposed annual review rule for five reasons: "
            "(1) Cost-effectiveness: projected administrative costs exceed fraud-prevention gains; "
            "(2) Capacity constraints: current staffing and IT systems cannot absorb the volume; "
            "(3) Equity: annual reviews disproportionately burden rural, disabled, and low-income communities; "
            "(4) Legal risk: increased denials without adequate process heighten litigation exposure; "
            "(5) Alternatives: targeted, risk-based reviews achieve oversight without universal burden."
        )
    },
    # Five similar-theme variants (same core theme phrased differently)
    {
        "UID": 21,
        "submitter_name": "Variant A",
        "date": "2025-08-23",
        "comment": "Annual reviews are too frequent and bureaucratic. Please shift to a two-year cadence."
    },
    {
        "UID": 22,
        "submitter_name": "Variant B",
        "date": "2025-08-23",
        "comment": "A yearly cycle is unnecessary; biennial reviews would reduce paperwork while preserving integrity."
    },
    {
        "UID": 23,
        "submitter_name": "Variant C",
        "date": "2025-08-23",
        "comment": "Please move to every two years—annual forms create avoidable stress and delays."
    },
    {
        "UID": 24,
        "submitter_name": "Variant D",
        "date": "2025-08-23",
        "comment": "Once a year is overkill. A 24-month review window would be more reasonable."
    },
    {
        "UID": 25,
        "submitter_name": "Variant E",
        "date": "2025-08-23",
        "comment": "Make it biennial. You’ll cut costs and reduce burdens without meaningfully increasing risk."
    },
    # Additional neutral/misc examples for broader coverage
    {
        "UID": 26,
        "submitter_name": "Neutral Note",
        "date": "2025-08-24",
        "comment": "I don’t have a strong opinion but appreciate the chance to comment. Please publish clear instructions."
    },
    {
        "UID": 27,
        "submitter_name": "Telehealth Advocate",
        "date": "2025-08-24",
        "comment": "Please allow telehealth evaluations and remote document submission to ease the burden on rural communities."
    },
    {
        "UID": 28,
        "submitter_name": "Phased Approach",
        "date": "2025-08-24",
        "comment": "Pilot annual reviews with a small cohort first, evaluate outcomes, then scale if benefits outweigh costs."
    },
    {
        "UID": 29,
        "submitter_name": "Data Security",
        "date": "2025-08-24",
        "comment": "I worry about identity theft. If you require more frequent document uploads, please invest in secure portals and clear breach notifications."
    },
    {
        "UID": 30,
        "submitter_name": "Caregiver",
        "date": "2025-08-25",
        "comment": "I’m a caregiver. Taking time off for yearly appointments means lost wages and jeopardizes my job. A longer interval would help."
    },
    {
        "UID": 31,
        "submitter_name": "Conditional Supporter",
        "date": "2025-08-25",
        "comment": "Support with safeguards: keep reviews for high-risk cases but streamline renewals for stable conditions."
    },
    {
        "UID": 32,
        "submitter_name": "Contact Info",
        "date": "2025-08-25",
        "comment": "Email me at alex.perez@example.org to share any updates. My mailing address is 1010 Maple St, Apt 5, Springfield."
    },
    {
        "UID": 33,
        "submitter_name": "Third-Party Case",
        "date": "2025-08-25",
        "comment": "My mother, Linda, DOB 05/05/1955, can’t travel easily. Please consider exceptions for people like her."
    },
    {
        "UID": 34,
        "submitter_name": "SSA Contractor",
        "date": "2025-08-25",
        "comment": "As a contractor supporting SSA systems, I see firsthand that MCS and related tools can’t handle surges."
    },
    {
        "UID": 35,
        "submitter_name": "Heated Critic",
        "date": "2025-08-25",
        "comment": "This proposal is insulting and tone-deaf. Stop wasting our time with policies that kick people when they’re down."
    },
]

df = pd.DataFrame(rows)
out_path = "data/mock_comments.xlsx"
df.to_excel(out_path, index=False)
print(f"Wrote {len(df)} rows to {out_path}")

