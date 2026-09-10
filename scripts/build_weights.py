"""Rebuild ai_activity_weights.csv over the full O*NET 4.A work-activity taxonomy.

activity_name is taken verbatim from data/raw/onet/work_activities.parquet so the
seed stays readable next to the raw data; the join key is activity_id.
"""

import duckdb
import pandas as pd

RAW = "/home/hoan/VSCode/projects/ai-displacement-observatory/data/raw"

# category/weight per activity id. high = LLM-substitutable cognitive/information work,
# low = physical, in-person, or relational work that resists current AI automation.
SCORES = {
    "4.A.1.a.1": ("high", 0.6),   # Getting Information
    "4.A.1.a.2": ("low", 0.4),    # Monitoring Processes, Materials, or Surroundings
    "4.A.1.b.1": ("low", 0.3),    # Identifying Objects, Actions, and Events
    "4.A.1.b.2": ("low", 0.7),    # Inspecting Equipment, Structures, or Materials
    "4.A.1.b.3": ("high", 0.8),   # Estimating the Quantifiable Characteristics
    "4.A.2.a.1": ("high", 0.5),   # Judging the Qualities of Objects, Services, or People
    "4.A.2.a.2": ("high", 1.0),   # Processing Information
    "4.A.2.a.3": ("high", 0.9),   # Evaluating Information to Determine Compliance
    "4.A.2.a.4": ("high", 1.0),   # Analyzing Data or Information
    "4.A.2.b.1": ("high", 0.6),   # Making Decisions and Solving Problems
    "4.A.2.b.2": ("high", 0.8),   # Thinking Creatively
    "4.A.2.b.3": ("high", 0.9),   # Updating and Using Relevant Knowledge
    "4.A.2.b.4": ("high", 0.5),   # Developing Objectives and Strategies
    "4.A.2.b.5": ("high", 0.6),   # Scheduling Work and Activities
    "4.A.2.b.6": ("high", 0.5),   # Organizing, Planning, and Prioritizing Work
    "4.A.3.a.1": ("low", 1.0),    # Performing General Physical Activities
    "4.A.3.a.2": ("low", 1.0),    # Handling and Moving Objects
    "4.A.3.a.3": ("low", 0.8),    # Controlling Machines and Processes
    "4.A.3.a.4": ("low", 0.9),    # Operating Vehicles, Mechanized Devices, or Equipment
    "4.A.3.b.1": ("high", 1.0),   # Working with Computers
    "4.A.3.b.2": ("high", 0.8),   # Drafting, Laying Out, and Specifying Technical Devices
    "4.A.3.b.4": ("low", 0.9),    # Repairing and Maintaining Mechanical Equipment
    "4.A.3.b.5": ("low", 0.8),    # Repairing and Maintaining Electronic Equipment
    "4.A.3.b.6": ("high", 0.9),   # Documenting/Recording Information
    "4.A.4.a.1": ("high", 0.7),   # Interpreting the Meaning of Information for Others
    "4.A.4.a.2": ("low", 0.5),    # Communicating with Supervisors, Peers, or Subordinates
    "4.A.4.a.3": ("low", 0.4),    # Communicating with People Outside the Organization
    "4.A.4.a.4": ("low", 0.7),    # Establishing and Maintaining Interpersonal Relationships
    "4.A.4.a.5": ("low", 1.0),    # Assisting and Caring for Others
    "4.A.4.a.6": ("low", 0.5),    # Selling or Influencing Others
    "4.A.4.a.7": ("low", 0.7),    # Resolving Conflicts and Negotiating with Others
    "4.A.4.a.8": ("low", 0.9),    # Performing for or Working Directly with the Public
    "4.A.4.b.1": ("low", 0.5),    # Coordinating the Work and Activities of Others
    "4.A.4.b.2": ("low", 0.7),    # Developing and Building Teams
    "4.A.4.b.3": ("low", 0.5),    # Training and Teaching Others
    "4.A.4.b.4": ("low", 0.8),    # Guiding, Directing, and Motivating Subordinates
    "4.A.4.b.5": ("low", 0.8),    # Coaching and Developing Others
    "4.A.4.b.6": ("low", 0.4),    # Providing Consultation and Advice to Others
    "4.A.4.c.1": ("high", 0.8),   # Performing Administrative Activities
    "4.A.4.c.2": ("low", 0.4),    # Staffing Organizational Units
    "4.A.4.c.3": ("high", 0.4),   # Monitoring and Controlling Resources
}

acts = duckdb.sql(
    f"select distinct activity_id, activity_name "
    f"from '{RAW}/onet/work_activities.parquet' order by 1"
).df()

missing = set(acts["activity_id"]) ^ set(SCORES)
assert not missing, f"taxonomy mismatch: {sorted(missing)}"

acts["ai_exposure_category"] = acts["activity_id"].map(lambda i: SCORES[i][0])
acts["weight"] = acts["activity_id"].map(lambda i: SCORES[i][1])
acts.to_csv("ai_activity_weights.csv", index=False)
print(acts["ai_exposure_category"].value_counts().to_dict(), len(acts))
