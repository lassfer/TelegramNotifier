using System;

namespace SimpleApp
{
    public class Calculator
    {
        public int Add(int a, int b) => a + b;
        public int Subtract(int a, int b) => a - b;
        public int Multiply(int a, int b) => a * b;

        public double Divide(int a, int b)
        {
            if (b == 0)
            {
                throw new DivideByZeroException("Деление на ноль невозможно!");
            }
            return (double)a / b;
        }

        public bool IsEven(int number) => number % 2 == 0;

        public bool IsPrime(int number)
        {
            if (number <= 1) return false;
            for (int i = 2; i <= Math.Sqrt(number); i++)
                if (number % i == 0) return false;
            return true;
        }
    }
}
