#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system_backend.settings')
django.setup()

from elections.models import Election
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive

def debug_election_timing():
    print("=== Election Timing Debug ===")
    print(f"Current time (UTC): {timezone.now()}")
    print(f"Current time (local): {timezone.localtime(timezone.now())}")
    print()
    
    elections = Election.objects.all()
    for election in elections:
        print(f"Election: {election.name}")
        print(f"  ID: {election.id}")
        print(f"  is_active: {election.is_active}")
        print(f"  start_time: {election.start_time} (naive: {is_naive(election.start_time)})")
        print(f"  end_time: {election.end_time} (naive: {is_naive(election.end_time)})")
        
        # Convert to aware datetimes if needed
        start = election.start_time
        end = election.end_time
        if is_naive(start):
            start = make_aware(start, timezone.get_current_timezone())
        if is_naive(end):
            end = make_aware(end, timezone.get_current_timezone())
            
        print(f"  start_time (aware): {start}")
        print(f"  end_time (aware): {end}")
        
        # Check if election should be active
        now = timezone.now()
        start_utc = start.astimezone(timezone.utc) if start.tzinfo else start
        end_utc = end.astimezone(timezone.utc) if end.tzinfo else end
        now_utc = now.astimezone(timezone.utc)
        
        print(f"  start_utc: {start_utc}")
        print(f"  end_utc: {end_utc}")
        print(f"  now_utc: {now_utc}")
        
        is_in_time_window = start_utc <= now_utc <= end_utc
        print(f"  In time window: {is_in_time_window}")
        print(f"  Should be active: {election.is_active and is_in_time_window}")
        
        # Check daily voting hours
        print(f"  voting_start_time: {election.voting_start_time}")
        print(f"  voting_end_time: {election.voting_end_time}")
        
        now_local = timezone.localtime(now)
        now_time = now_local.time()
        start_t = election.voting_start_time
        end_t = election.voting_end_time
        
        within_daily_window = False
        if start_t <= end_t:
            within_daily_window = (start_t <= now_time <= end_t)
        else:
            # Window crosses midnight
            within_daily_window = (now_time >= start_t or now_time <= end_t)
            
        print(f"  current_time: {now_time}")
        print(f"  In daily window: {within_daily_window}")
        print(f"  Overall can vote: {election.is_active and is_in_time_window and within_daily_window}")
        print("-" * 50)

if __name__ == "__main__":
    debug_election_timing()
