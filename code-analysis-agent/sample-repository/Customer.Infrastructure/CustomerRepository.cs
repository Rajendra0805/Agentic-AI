using Microsoft.Data.SqlClient;

namespace Customer.Infrastructure;

public class CustomerRepository
{
    public void GetCustomer(int id)
    {
        var connectionString =
            "Server=localhost;Database=CustomerDb;User Id=sa;Password=Password123;";

        using var connection =
            new SqlConnection(connectionString);

        connection.Open();
    }
}