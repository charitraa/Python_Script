
#!/usr/bin/env python3
"""
Yautō survey pipeline tester.

Creates 10 varied SYNTHETIC profiles for testing a separate
Google Form -> Google Sheets -> analysis pipeline.

Default: dry run only.
--send: submits clearly marked synthetic responses.
-n 3: choose 1 to 10 profiles.

Use a dedicated test copy of the form for submissions.
"""

import argparse
import random
import time
import urllib.parse
import urllib.request

FORM_ID = "1FAIpQLSdz4ygQIL23S8JcC6It2o58zs9a9oPnw1e32TFRwwt8BPnAcg"
SUBMIT_URL = (
    f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
)
MAX_TESTS = 5

# Each profile has distinct, internally consistent answers.
# Checkbox answers are lists; single-choice answers are strings.

PROFILES = [
    {
        "name": "Dipesh Bhandari",
        "gender": "Male", "age": "21-23",
        "status": "College/University student",
        "transport": "Public vehicle", "duration": "15-30 minutes",
        "cost": "Rs. 50-100", "alone": "Sometimes with someone",
        "know": "Yes, a few",
        "discovery": "Social Media",
        "willing": "Probably",
        "reason": ["Reduce transportation cost",
                   "Meet/connect with other students"],
        "communicate": "Yes", "reliability": "Important",
        "info": ["Name", "College/university", "Travel time",
                 "Starting location/area"],
        "verification": "4",
        "concerns": ["Different schedules", "Route mismatch"],
        "app": "Probably",
        "features": ["Match based on location and time",
                     "Group/community chat", "Journey history"],
    },
    {
        "name": "Manisha K.C.",
        "gender": "Female", "age": "24-26",
        "status": "College/University student",
        "transport": "Ride-sharing apps (Pathao, inDrive, etc.)",
        "duration": "45-60 minutes",
        "cost": "Rs. 200-300", "alone": "Mostly alone",
        "know": "Maybe / I'm not sure",
        "discovery": "I don't usually look for someone",
        "willing": "Maybe",
        "reason": ["Safety/feeling more comfortable",
                   "Reduce waiting time for public vehicle"],
        "communicate": "Yes", "reliability": "Very important",
        "info": ["Profile", "College/university", "Destination",
                 "Previous ratings/reviews"],
        "verification": "5",
        "concerns": ["Safety", "Privacy", "Cost/payment issues"],
        "app": "Probably",
        "features": ["Student verification", "Ratings and reviews",
                     "Send/accept ride requests", "Report/block users"],
    },
    {
        "name": "Prabin Khadka",
        "gender": "Male", "age": "18-20",
        "status": "College/University student",
        "transport": "Bicycle", "duration": "30-45 minutes",
        "cost": "Less than Rs.50", "alone": "Always alone",
        "know": "No",
        "discovery": "I ask my friends",
        "willing": "Probably",
        "reason": ["Avoid travelling alone", "Convenience"],
        "communicate": "Maybe", "reliability": "Neutral",
        "info": ["Name", "Starting location/area", "Destination"],
        "verification": "3",
        "concerns": ["Not knowing the person", "Route mismatch"],
        "app": "Maybe",
        "features": ["Find students travelling on similar routes",
                     "Match based on location and time"],
    },
    {
        "name": "Roshani Basnet",
        "gender": "Female", "age": "21-23",
        "status": "College/University student",
        "transport": "Public vehicle", "duration": "More than 1 hour",
        "cost": "Rs. 100-200", "alone": "Mostly alone",
        "know": "Yes, a few",
        "discovery": "College/class group chats",
        "willing": "Definitely",
        "reason": ["Reduce transportation cost",
                   "Reduce waiting time for public vehicle",
                   "Avoid travelling alone"],
        "communicate": "Yes", "reliability": "Very important",
        "info": ["Name", "Profile", "College/university",
                 "Starting location/area", "Destination", "Travel time",
                 "Previous ratings/reviews"],
        "verification": "5",
        "concerns": ["Safety", "Trust",
                     "Reliability (someone cancelling)"],
        "app": "Definitely",
        "features": ["Find students travelling on similar routes",
                     "Match based on location and time",
                     "Student verification", "Journey history",
                     "Ratings and reviews", "Report/block users"],
    },
    {
        "name": "Sagar Panta",
        "gender": "Male", "age": "27+",
        "status": "Working professional",
        "transport": "Personal Car", "duration": "15-30 minutes",
        "cost": "Rs. 200-300", "alone": "Usually with someone",
        "know": "Yes, many",
        "discovery": "I already know someone who travels same route as me",
        "willing": "Probably not",
        "reason": ["Convenience"],
        "communicate": "No", "reliability": "Important",
        "info": ["Name", "College/university", "Travel time"],
        "verification": "4",
        "concerns": ["Different schedules",
                     "Reliability (someone cancelling)"],
        "app": "Maybe",
        "features": ["Journey history", "Ratings and reviews"],
    },
]

# Google Forms entry ID -> profile key
FIELD_MAP = {
    1266497757: "gender",
    366340186: "age",
    2081574952: "status",
    2143341637: "transport",
    1209240842: "duration",
    686007298: "cost",
    602687841: "alone",
    2035651651: "know",
    1103148576: "discovery",
    1166762282: "willing",
    365110847: "reason",
    757037173: "communicate",
    1998314424: "reliability",
    779341981: "info",
    1888243636: "verification",
    1945192345: "concerns",
    1563270935: "app",
    760579727: "features",
}


def build_payload(profile):
    data = [
        # Always mark synthetic records in the name field.
        ("entry.2002059705", f"SYNTHETIC TEST - {profile['name']}")
    ]

    for entry_id, field in FIELD_MAP.items():
        value = profile[field]

        if isinstance(value, list):
            for choice in value:
                data.append((f"entry.{entry_id}", choice))
        else:
            data.append((f"entry.{entry_id}", value))

    data.append(("pageHistory", "0"))
    return data


def submit(data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        SUBMIT_URL,
        data=body,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        page = response.read().decode(errors="replace")
        return response.status, page



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send",
        action="store_true",
        help="submit synthetic responses to a dedicated test form",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=5,
        help="number of profiles to preview or submit (1-5)",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="shuffle the order of the predefined profiles",
    )
    args = parser.parse_args()

    if not 1 <= args.n <= len(PROFILES):
        parser.error(f"-n must be between 1 and {len(PROFILES)}")

    profiles = PROFILES.copy()

    if args.shuffle:
        random.shuffle(profiles)

    for i, profile in enumerate(profiles[:args.n], start=1):
        payload = build_payload(profile)

        if not args.send:
            print(f"\n--- SYNTHETIC PROFILE {i}: {profile['name']} ---")
            for key, value in payload:
                print(f"{key} = {value}")
            continue

        print(f"Submitting synthetic profile: {profile['name']}")
        try:
            status, page = submit(payload)
            print(
                f"HTTP {status}. Check the test form's response Sheet "
                "to confirm it was recorded."
            )
            if "Your Name" in page:
                print("WARNING: The form may have been re-shown.")
        except Exception as exc:
            print(f"Submission failed: {exc}")

        if i < args.n:
            time.sleep(2)

    if not args.send:
        print("\nDRY RUN ONLY: nothing was submitted.")
        print("Use --send only with a dedicated test form.")


if __name__ == "__main__":
    main()
