class User:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user_type = 'Logged Out'

    def set_user_to_student(self):
        self.user_type = 'Student'

    def set_user_to_liaison(self):
        self.user_type = 'Liaison'

    def set_user_to_instructor(self):
        self.user_type = 'Instructor'
