using Xunit;
using System;
using SimpleApp;

public class CalculatorTests
{
    private readonly Calculator _calculator = new();

    [Fact]
    public void Add_TwoNumbers_ReturnsSum()
    {
        int a = 5, b = 3;
        int result = _calculator.Add(a, b);
        Assert.Equal(8, result);
    }

    [Fact]
    public void Divide_ByZero_ThrowsException()
    {
        Assert.Throws<DivideByZeroException>(() => _calculator.Divide(10, 0));
    }

    [Theory]
    [InlineData(2, true)]
    [InlineData(3, true)]
    [InlineData(4, false)]
    [InlineData(17, true)]
    public void IsPrime_VariousNumbers_ReturnsCorrect(int number, bool expected)
    {
        bool result = _calculator.IsPrime(number);
        Assert.Equal(expected, result);
    }
}
