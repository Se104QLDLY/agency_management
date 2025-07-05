from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from authentication.models import Account, User

class Command(BaseCommand):
    help = 'Creates a new agent user with an associated user profile.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='The username for the new agent.')
        parser.add_argument('--password', type=str, required=True, help='The password for the new agent.')
        parser.add_argument('--fullname', type=str, required=True, help='The full name for the user profile.')
        parser.add_argument('--email', type=str, required=True, help='The email for the user profile.')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        fullname = options['fullname']
        email = options['email']

        if Account.objects.filter(username=username).exists():
            raise CommandError(f"Error: User with username '{username}' already exists.")

        try:
            with transaction.atomic():
                # The create_user method now handles password hashing
                account = Account.objects.create_user(
                    username=username,
                    password=password,
                    account_role='admin'
                )

                # Create the associated User profile
                User.objects.create(
                    account=account,
                    full_name=fullname,
                    email=email
                )

            self.stdout.write(self.style.SUCCESS(f"Successfully created agent user '{username}'."))

        except Exception as e:
            raise CommandError(f"An error occurred: {e}") 