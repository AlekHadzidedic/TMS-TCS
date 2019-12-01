class Team:
    default_team_size = 0
    default_min_size = 0

    def __init__(self, name):
        self.name = name
        self.team_number = 0
        self.num_team_members = 0
        self.min_team_size = Team.default_min_size
        self.max_team_size = Team.default_team_size

    def set_max_team_size(self, max_team_size):
        self.max_team_size = max_team_size

    def set_min_team_size(self, min_team_size):
        self.min_team_size = min_team_size

    def increment_team_members(self):
        self.num_team_members += 1

    def decrement_team_members(self):
        self.num_team_members -= 1


