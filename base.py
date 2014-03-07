from abc import ABCMeta, abstractmethod
from collections import Iterable
from functools import partial, wraps
from operator import rshift
from itertools import repeat, imap, chain

F = partial

class Monad(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __rshift__(self, other):
        pass

    @abstractmethod
    def wrap(self, other):
        pass

class Maybe(Monad):
    @classmethod
    def wrap(cls, other):
        return Just(other)

    def fmap(self, f):
        if isinstance(self, Just):
            return Just(f(self.value))

class Just(Maybe):
    def __rshift__(self, other):
        return other(self.value)

    def __repr__(self):
        return "Just {}".format(self.value)

    def __init__(self, value):
        self.value = value

class Nothing(Maybe):
    def __rshift__(self, other):
        return Nothing()

    def __repr__(self):
        return "Nothing"


class MList(Monad):
    def __init__(self, ls):
        if isinstance(ls, tuple):
            self.value = ls
        else:
            raise TypeError("The list monad only accepts values subclassed from the abstract base class Iterable.")

    def __iter__(self):
        return iter(self.value)

    def __rshift__(self, f):
        mapped = map(f, self.value)
        catted = tuple(chain(*mapped))
        return MList(catted)

    def __repr__(self):
        return repr(self.value)

    @classmethod
    def wrap(cls, value):
        return cls((value,))

def threemultsof(n, v):
    return [n*v, 2*n*v, 3*n*v]

def div(n, d):
    if d == 0:
        return Nothing()
    else:
        return Just(n / d)

def iseven(n):
    return Just(not (n % 2))

def filterm(pred, ls, monad):
    #hack to find what kind of monad pred returns
    #monad = pred(ls[0]).__class__
    if not ls:
        return monad.wrap(tuple(ls))

    return pred(ls[0]) >> (lambda flag: \
        filterm(pred, ls[1:], monad) >> (lambda ys: \
        monad.wrap((ls[0],) + ys if flag else ys)))

def main():
    print Just(5) >> F(div, 15) >> F(div, 1)
    print Just(10) >> F(div, 0) >> F(div, 2)

    mls = MList((1,2,3)) >> (lambda _: MList((1,)))
    print mls

    mls2 = MList((1,2,3)) >> (lambda xs: \
           MList((1,)) >> (lambda _: \
           threemultsof(3, xs)))
    print mls2

    result = filterm(iseven, range(100), Maybe)
    print result

    result = filterm(lambda _: MList((True, False)), range(5), MList)
    print result

    pass

if __name__ == "__main__":
    main()