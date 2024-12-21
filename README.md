# SmartParkingSystem
Intelligent system for parking management: data acquisition, analysis, and dashboard for real-time monitoring and availability forecasting.

## Assignment
Smart Parking Management System: Design a smart parking management system using big data technologies to alleviate urban congestion and optimize parking availability. Collect data from sensors installed in parking spaces, CCTV cameras, and mobile apps to monitor parking occupancy in real-time. Develop algorithms to predict parking demand, optimize parking space allocation, and provide real-time parking availability information to drivers. Additionally, consider incorporating features such as dynamic pricing, parking reservation systems, and integration with public transportation to encourage sustainable urban mobility.v

## General Idea 
The architecture could contain multiple data generators, that correspond to different parking lots. The generators would send the images, videos and structured data of the state of the parking lot to a central datalake or other storage.
A processing program would read the data from the datalake and analyse it. The results are either stored in an other database or are immediatly displayed on a dashboard.
The analyses could contain current parking capacity, redirections to other parking lots incase one is full and forecasting. For example a user could ask the dashboard at 5:30 on a monday the probability of there to be a free spot.

### Useful links

https://www.kaggle.com/datasets/iasadpanwhar/parking-lot-detection-counter
(Dataset containing images, videos and structured data)
