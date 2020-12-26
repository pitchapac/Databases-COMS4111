# databases-real-estate Group 8
## Account information
PostgreSQL account name: cba2126
PostgreSQL account password: 3534

URL: http://35.237.76.245:8111/


## What we implemented:
Our idea is to make an application with information about residential real estate in New York City. Customers, sellers and agents can create accounts on our site. Customers can filter  based on their criteria to find apartments and houses represented by agents. Potential customers and sellers can come to our website to create an account and connect with one of our agents by creating a booking.  

On our site customers, sellers, and agents can make accounts with personal information such as name and contact information. Customers are able to filter based on their criteria to find apartments and houses represented by agents. Sellers can list their houses on our site for customers to see. Agents will be able to mark properties as sold after they reach agreements with customers and sellers offline. Customers can make bookings with agents. Customers and agents can review each other.

On our application, users can first create an account with personal information such as name, date of birth, and contact information. They will then be able to filter the listings by price, location, number of bedrooms, and number of bathrooms. They will be able to save properties they like and view the email addresses for the agents of the properties.

The differences from our description of part 1 are that we allowed sellers to pick what agent represents their property, rather than matching the agent to the property for them. We felt that this modeled the real world better. We also removed the ability for agents to make bookings since we felt that it shouldn’t be the job of the agent to make the booking. 

## The most interesting database operations:
 
The first most interesting thing as a seller you are able to view the properties that you listed that have either sold or still available. The resulted table shows all information about each property including the property_id, dated listed, address, zip code, price, and the property type (house or apartment). In addition, the table also shows the agent representing each property along with their contact information which includes name, email, and phone number. This is interesting because the query involves a lot of joins from multiple tables and case statements. For an example for the seller_id = 30120043324 we have the following query: 
 
SELECT table_1.property_id,  table_1.day_listed,  table_1.num_beds,  table_1.num_baths,  table_1.address,  table_1.zipcode, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN 'apartment' ELSE 'house' END) AS property_type, (CASE WHEN table_1.property_id IN (SELECT rentable_id FROM rentable) THEN (SELECT monthly_rent from rentable WHERE rentable_id = table_1.property_id) ELSE (SELECT total_price FROM buyable WHERE buyable_id = table_1.property_id) END) AS price, name AS agent_name, email AS agent_email, phone AS agent_phone FROM (SELECT property_id, day_listed, num_beds, num_baths, address, zipcode FROM property LEFT OUTER JOIN buyable ON property_id = buyable_id WHERE property.property_id NOT IN (SELECT property_id FROM sold) AND property.seller_id = 30120043324) AS table_1 INNER JOIN (SELECT property_id FROM property LEFT OUTER JOIN rentable ON property_id = rentable_id WHERE property.property_id NOT IN (SELECT property_id FROM sold) AND property.seller_id = 30120043324) AS table_2 ON table_1.property_id = table_2.property_id INNER JOIN (SELECT property_id, name, email, phone FROM represents, person WHERE person_id = agent_id) AS table_3 ON table_3.property_id = table_2.property_id;
 
The second most interesting page is our filter listing page for the customer. When a customer creates a customer profile, they fill in their preferences for the type of property they want, the number of bedrooms, the number of bathrooms, the address, and the zipcode. This information is stored in the customer table and is retrived from a form on the setup customer account page. Then, when they first click on the filter listings page to enter search criteria, they will see properties that match their preferences already on the page without them having to search. Additionally, customers can use this page to query the database based on their preferences. From the results of their queries, customers can contact the agents that represent the properties by clicking a link that takes them to a page with information about the representing agent. The application queries the rentable properties table and the properties table if the customer is looking for a rental, and it queries the buyable properties table and the properties table if the customer is looking for a property to buy. The application also has to query the represents and agent tables to get information about the representing agent as well as the customer table to get information about the customers preferences. 
 
## Other notes
Source on how to prevent SQL injection attacks when using SQLAlchemy in Python from: https://blog.sqreen.com/preventing-sql-injections-in-python/

We imported urllib.parse from the standard Python library to ensure the special characters in addresses where preserved when being displayed on our site. We also imported datetime from the standard Python library to be able to get the current date for listing dates and such.

