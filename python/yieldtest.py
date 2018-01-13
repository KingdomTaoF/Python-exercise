def fib(max):
    n,a,b = 0,0,1
    while n < max:
        yield b
        a,b = b,a+b
        
        n += 1
    return "done"
    
data = fib(10)
try:
    for i in data:
        print(i)
except StopIteration as e:
    print("stop flag:",e.value)