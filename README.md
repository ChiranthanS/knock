# **Knock - Real-time Carrier Price Comparison Platform**

## **Overview**
Knock is a real-time carrier price comparison platform that helps users find the best transportation solutions for their needs. The platform integrates with various carrier APIs like FedEx and UPS to provide real-time data on shipment prices, ensuring users can make informed decisions. The platform also features a chatbot for payments, enhancing the user experience by streamlining the payment process.

## **Features**
- **Real-time Carrier Price Comparison:**  
  Compare prices from multiple carriers (e.g., FedEx, UPS) in real-time to find the most cost-effective shipping options.
  
- **API Integration:**  
  The platform integrates with external APIs to retrieve real-time shipping data, ensuring that users receive accurate, up-to-date pricing.

- **Chatbot Payments:**  
  A built-in chatbot simplifies the payment process, allowing users to complete transactions quickly and efficiently through a conversational interface.

- **Two-Factor Authentication:**  
  Ensures secure transactions and protects user data with an additional layer of security.

- **Cloud Deployment:**  
  The platform is deployed on Google Cloud Platform (GCP) for scalability and high availability, ensuring that it can handle large numbers of users and requests without downtime.

## **Tech Stack**
- **Frontend:**  
  React.js – A powerful JavaScript library for building user interfaces.
  
- **Backend:**  
  Flask – A lightweight Python framework for building RESTful APIs.  
  MySQL – A relational database management system for handling user data and carrier information.

- **API Integration:**  
  FedEx and UPS APIs for real-time carrier price retrieval.

- **Security:**  
  Two-factor authentication for enhanced security.

- **Cloud:**  
  Google Cloud Platform (GCP) – For hosting and scaling the application.

## **How It Works**
1. **User Input:**  
   Users provide shipment details (e.g., origin, destination, package weight).

2. **Carrier Comparison:**  
   The platform fetches real-time shipping prices from carriers using their respective APIs.

3. **Results Display:**  
   Users are presented with the most cost-effective shipping options, ranked by price.

4. **Chatbot Payment:**  
   Once a carrier is selected, users can complete the payment process through the chatbot interface, making the transaction seamless.

## **Future Enhancements**
- **Additional Carrier Support:**  
  Integration with more carriers to expand the platform’s comparison options.
  
- **Advanced Analytics:**  
  Providing users with detailed insights on shipment trends, helping them make data-driven decisions.

- **Mobile App Development:**  
  Expanding the platform’s functionality to mobile devices for a broader user base.



