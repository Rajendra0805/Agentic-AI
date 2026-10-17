using Microsoft.AspNetCore.Mvc;

namespace Customer.Api.Controllers;

[ApiController]
[Route("api/customers")]
public class CustomerController : ControllerBase
{
    [HttpGet("{id}")]
    public IActionResult GetCustomer(int id)
    {
        if (id <= 0)
        {
            return BadRequest();
        }

        var customerName = "Customer-" + id;

        if (customerName.Length > 5)
        {
            return Ok(customerName);
        }

        return NotFound();
    }

    [HttpPost]
    public IActionResult CreateCustomer()
    {
        return Ok();
    }
}