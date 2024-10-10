class NumberUtils:
    def __init__(self, num):
        self.num = num

    def abbreviate(self):
        if self.num >= 1_000_000_000:
            return f'{self.num / 1_000_000_000:.1f}B'
        elif self.num >= 1_000_000:
            return f'{self.num / 1_000_000:.1f}M'
        elif self.num >= 1_000:
            return f'{self.num / 1_000:.1f}K'
        else:
            return f'{str(self.num)}'

