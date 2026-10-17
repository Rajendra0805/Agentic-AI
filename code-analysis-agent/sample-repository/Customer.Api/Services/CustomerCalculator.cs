namespace Customer.Api.Services;

public class CustomerCalculator
{
    public decimal Calculate(decimal amount)
    {
        if (amount > 1000)
        {
            return amount * 0.90m;
        }

        if (amount > 500)
        {
            return amount * 0.95m;
        }

        return amount;
    }
}