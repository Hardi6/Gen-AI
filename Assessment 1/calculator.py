def add(x,y):
    return x+y
def sub(x,y):
    return x-y
def mul(x,y):
    return x*y
def div(x,y):
    if y==0:
        return 'Cannot divide'
    return x/y
a=int(input('Enter the number:'))
b=int(input('Enter the number:'))

print("Select operation")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")

select=int(input("Select (1/2/3/4): "))
if select in(1,2,3,4):
    if select==1:
        print('Result:', add(a,b))
    elif select==2:
        print('Result:',sub(a,b))
    elif select==3:
        print('Result:',mul(a,b))
    elif select==4:
        print('Result:',div(a,b))
else:
    print('invalid input')
    