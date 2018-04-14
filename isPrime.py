from pynocle import Monocle

a = Monocle("isPrime.py","/home/darren/Desktop/Software/test/","/home/darren/Desktop/Software/MyOwnCode/ELEN4020-Group-ADJU-Lab-3/")

num = 407

# take input from the user
# num = int(input("Enter a number: "))

# prime numbers are greater than 1
if num > 1:
   # check for factors
   for i in range(2,num):
       if (num % i) == 0:
           print(num,"is not a prime number")
           print(i,"times",num//i,"is",num)
           break
   else:
       print(num,"is a prime number")
       
# if input number is less than
# or equal to 1, it is not prime
else:
   print(num,"is not a prime number")

