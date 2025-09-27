from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from elections.models import Election, Candidate
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample elections with candidates for testing purposes'

    def handle(self, *args, **options):
        # Get or create an admin user to associate with these elections
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Election 1: College Union President Election 2025
        election1 = Election.objects.create(
            name='College Union President Election 2025',
            description='Election to select the College Union President for the academic year 2025–26.',
            election_type='single_choice',
            start_time=timezone.make_aware(datetime.datetime(2025, 9, 20, 9, 0)),
            end_time=timezone.make_aware(datetime.datetime(2025, 9, 20, 17, 0)),
            voting_start_time=datetime.time(9, 0),
            voting_end_time=datetime.time(17, 0),
            max_votes_per_voter=1,
            require_confirmation=True,
            created_by=admin_user
        )
        
        # Add candidates for Election 1
        Candidate.objects.create(
            name='Rahul Verma',
            position='President',
            description='Advocates for better sports facilities and student welfare.',
            order=0,
            election=election1
        )
        
        Candidate.objects.create(
            name='Anjali Sharma',
            position='President',
            description='Promises cultural fests and academic support initiatives.',
            order=1,
            election=election1
        )

        # Election 2: Residents' Welfare Association (RWA) Committee
        election2 = Election.objects.create(
            name="Residents' Welfare Association (RWA) Committee",
            description='Election for selecting members of the Residents’ Welfare Association for Green Park Colony, New Delhi.',
            election_type='multiple_choice',
            start_time=timezone.make_aware(datetime.datetime(2025, 10, 5, 8, 0)),
            end_time=timezone.make_aware(datetime.datetime(2025, 10, 5, 18, 0)),
            voting_start_time=datetime.time(8, 0),
            voting_end_time=datetime.time(18, 0),
            max_votes_per_voter=3,
            require_confirmation=True,
            created_by=admin_user
        )
        
        # Add candidates for Election 2
        Candidate.objects.create(
            name='Suresh Iyer',
            position='Treasurer',
            description='Experienced in community finance.',
            order=0,
            election=election2
        )
        
        Candidate.objects.create(
            name='Priya Nair',
            position='Secretary',
            description='Focused on women’s safety and welfare.',
            order=1,
            election=election2
        )
        
        Candidate.objects.create(
            name='Arjun Reddy',
            position='Executive Member',
            description='Plans for improving cleanliness and greenery.',
            order=2,
            election=election2
        )
        
        Candidate.objects.create(
            name='Kavita Joshi',
            position='Executive Member',
            description='Dedicated to youth and cultural activities.',
            order=3,
            election=election2
        )

        # Election 3: Employee of the Month
        election3 = Election.objects.create(
            name='Employee of the Month – Infosys Bangalore, September 2025',
            description='Voting to recognize the best employee contribution at Infosys Bangalore campus.',
            election_type='single_choice',
            start_time=timezone.make_aware(datetime.datetime(2025, 9, 28, 9, 0)),
            end_time=timezone.make_aware(datetime.datetime(2025, 9, 28, 19, 0)),
            voting_start_time=datetime.time(9, 0),
            voting_end_time=datetime.time(19, 0),
            max_votes_per_voter=1,
            require_confirmation=False,
            created_by=admin_user
        )
        
        # Add candidates for Election 3
        Candidate.objects.create(
            name='Meena Raghavan',
            position='Software Engineer',
            description='Delivered critical project ahead of deadline.',
            order=0,
            election=election3
        )
        
        Candidate.objects.create(
            name='Karan Malhotra',
            position='Business Analyst',
            description='Great client handling and documentation skills.',
            order=1,
            election=election3
        )

        # Election 4: Best Start-up Idea
        election4 = Election.objects.create(
            name='Best Start-up Idea – IIT Delhi Annual Tech Fest',
            description='Students vote for the most innovative start-up ideas presented at the Tech Fest 2025.',
            election_type='ranked_choice',
            start_time=timezone.make_aware(datetime.datetime(2025, 11, 15, 10, 0)),
            end_time=timezone.make_aware(datetime.datetime(2025, 11, 16, 18, 0)),
            voting_start_time=datetime.time(10, 0),
            voting_end_time=datetime.time(18, 0),
            max_votes_per_voter=1,
            require_confirmation=True,
            created_by=admin_user
        )
        
        # Add candidates for Election 4
        Candidate.objects.create(
            name='Project Surya',
            position='Innovation Entry',
            description='Affordable solar energy solutions for villages.',
            order=0,
            election=election4
        )
        
        Candidate.objects.create(
            name='Project Aarogya',
            position='Innovation Entry',
            description='AI-driven health monitoring for rural clinics.',
            order=1,
            election=election4
        )
        
        Candidate.objects.create(
            name='Project Shiksha',
            position='Innovation Entry',
            description='Mobile app to improve access to education in rural India.',
            order=2,
            election=election4
        )

        self.stdout.write(self.style.SUCCESS('Successfully created 4 sample elections with candidates'))
