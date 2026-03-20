import sys
import os

base_dir = r"c:\Users\franc\Desktop\ZenPlanner"
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.csp_scheduler.domain import UserProfile, TimeSlot
from src.csp_scheduler.scheduler import ZenSchedulerEngine

user = UserProfile(
    age=22, gpa=3.0, social_media_hours_per_day=2.0, sleep_hours_per_night=8.0,
    physical_exercise_hours_per_week=3.0, family_support=3, financial_stress=3,
    peer_pressure=3, relationship_stress=2, diet_quality=3, coping_mechanisms={}
)

engine = ZenSchedulerEngine(user)
slots = [TimeSlot(day_of_week=d, start_time=h) for d in range(7) for h in range(9, 18)]

assignment, msg = engine.generate_schedule({"Studio": 15}, slots)
print(msg)
if assignment:
    sorted_a = sorted(assignment.items(), key=lambda x: (x[1].day_of_week, x[1].start_time))
    for s, t in sorted_a:
        print(f"[{t.day_of_week}] {t.start_time}:00 - {s.id}")
else:
    print("NO SOLUTION FOUND!")
