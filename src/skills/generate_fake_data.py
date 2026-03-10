from faker import Faker
import json

def generate_fake_data(num_records: int = 5) -> str:
    """Generates a specified number of realistic mock user profiles (name, address, email, job, company) and returns them as a JSON formatted string."""
    try:
        # Cap the records to prevent massive payload hanging
        num_records = min(num_records, 100)
        
        fake = Faker()
        records = []
        
        for _ in range(num_records):
            profile = {
                "name": fake.name(),
                "address": fake.address().replace('\n', ', '),
                "email": fake.email(),
                "job": fake.job(),
                "company": fake.company(),
                "phone_number": fake.phone_number(),
                "birthdate": str(fake.date_of_birth())
            }
            records.append(profile)
            
        return json.dumps(records, indent=2)
    except Exception as e:
        return f"Error generating fake data: {str(e)}"
