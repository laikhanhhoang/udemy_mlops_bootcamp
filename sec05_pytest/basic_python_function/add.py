def add(a,b):
    return a + b

def test_add():
    assert add(2,3) == 5
    assert add(-1,1) == 0



def test_add2():
    assert add(4,3) == 7
    assert add(-1,-2) == -3