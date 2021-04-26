import os

in_production = os.getenv('GAE_ENV', '').startswith('standard')

avg_days_to_death = 15