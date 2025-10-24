class Budgeting():
    def __init__(self):
        pass
    
    async def write_user_profile(self, user_id, profile_data):
        pass 
    
    async def read_user_profile(self, user_id):
        pass 
    
    async def create_budget(self, user_id, budget_data):
        pass 
    
    async def updated_budget(self, user_id, budget_data):
        pass 
    
    async def check_progress(self, user_id):
        pass 
    
    async def get_all_budgets(self, user_id):
        pass 
    
    async def set_alert(self, user_id):
        pass 
    
    async def schedule_reminder(self, user_id):
        pass 
    
    async def generate_budget_summary(self, user_id):
        pass 
    
    # These happen IMMEDIATELY - no scheduling
    async def send_immediate_alert(self, user_id, message):
        pass 
    
