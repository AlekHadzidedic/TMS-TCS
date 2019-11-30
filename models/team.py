class Team:
    default_team_size = 4

    def __init__(self, name):
        self.name = name
        self.num_team_members = 0
        self.max_team_members = Team.default_team_size

    def set_max_team_size(self, max_team_size):
        self.max_team_members = max_team_size

    def increment_team_members(self):
        self.num_team_members += 1

    def decrement_team_members(self):
        self.num_team_members -= 1


