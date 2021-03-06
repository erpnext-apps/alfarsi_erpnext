## Alfarsi ERPNext
> Dependency: [From ERPNext v13.13.0+](https://github.com/frappe/erpnext/releases/tag/v13.13.0). `develop/v14` support is yet to be added.

A custom app for Alfarsi International. This app contains:

## Quick Order
> This feature is ony available after login
> It works on Item Code input (from the Item master)

<details>
  <summary>Quick Order let's you quickly add regularly shopped items to cart from a popup.</summary>
  
  ![photo_2021-10-26 13 13 53](https://user-images.githubusercontent.com/25857446/138831911-979be837-b84a-4129-9066-5f7f9ff26b5e.jpeg)
</details>

Once the Item is selected, its price is fetched if it exists against this customer
Rows in this popup can be added or deleted.
<details>
  <summary>There are validations for qty and item code</summary>
  <img width="718" alt="Screenshot 2021-10-26 at 1 15 40 PM" src="https://user-images.githubusercontent.com/25857446/138832184-5862f0e3-96c6-487e-b24c-3d54eb1a2da7.png">
</details>

<details>
  <summary>A success message is included too</summary>
  
  ![photo_2021-10-26 13 13 58](https://user-images.githubusercontent.com/25857446/138832259-2780ba9a-dfc8-4e0c-9113-41ee530688b1.jpeg)
</details>

## Redirect to Sales Order from Quotation
- In cases where some items already have pre-negotiated prices, while other's dont: items that have prices are auto-picked into a Sales Order.
- Users are given feedback on the portal if a Sales order is generated against the current Quotation.
  <img width="1265" alt="Screenshot 2021-10-26 at 6 33 52 PM" src="https://user-images.githubusercontent.com/25857446/138888235-e790946e-999b-490f-822d-4d5731a97db8.png">

## Auto Create User from Customer
> Prerequisites: Email Account must be set up

- A custom field **Create a New User** is added to Customer master, and is **enabled by default**.
- It will create a new user against customer if **it does not already exist** and **if Create a New User is enabled**. It will also send a welcome email to this user so they can set up a password.


#### License

MIT
