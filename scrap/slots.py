class ImmutableThing:
    __slots__ = ['a', 'b', 'c']

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    @property
    def ab(self):
        return self.a * self.b


paul = ImmutableThing(1, 2, 3)

paul.c = 4

print(paul.a, paul.b, paul.c, paul.ab)
