# Project Agribot-Net

Agribot-Net is a collaborative robotic system designed for agricultural applications. It comprises two agribots. The first, a Fertilizer Spraying Agribot, detects disease-affected plants and administers fertilizer specifically to those plants. The second, a Harvesting Agribot, identifies and harvests ripened vegetables. Together, these agribots aim to enhance efficiency and precision in agricultural practices.


## Physical Construction
<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="text-align: center; border: none;">
      <img src="https://github.com/DonKurianDavis/Project_Agribot/blob/main/readme%20images/FERTILIZER_AGRIBOT%20v4.jpg" width="600" height="480" alt="Fertilizer Agribot" /><br />
      <strong>Fertilizer Spraying Agribot</strong>
    </td>
    <td style="text-align: center; border: none;">
      <img src="https://github.com/DonKurianDavis/Project_Agribot/blob/main/readme%20images/Harvesting_Agribot.jpg" width="600" height="480" alt="Harvesting Agribot" /><br />
      <strong>Harvesting Agribot</strong>
    </td>
  </tr>
</table>

The mobile components of both agribots are identical. They include:

* Four motors equipped with encoders for precise movement tracking.

* A Raspberry Pi Pico.

* Two L298N Motor Drivers to power the motors.

* Currently, a laptop is used for computational tasks.

* An Intel Realsense D455 camera that provides both color and depth images, which are combined to create a 3D virtual world.

## Navigation
<img src="https://github.com/DonKurianDavis/Project_Agribot/blob/main/readme%20images/RVIZ.png" alt="RVIZ" />

* Mapping: The Intel Realsense camera captures images and depth data, which are processed by RTAB-Map to create a map of the environment.

* Localization: The robot uses the map created by RTAB-Map to localize itself within the environment.

* Navigation: Nav2 uses the map and localization data to plan a path to the target location, avoiding obstacles and ensuring safe navigation.

## Manipulator working of Fertilizer Spraying Agribot

* Disease Detection: Uses a depth camera and a machine learning model to detect the presence of disease.

* Manipulator Motion: Follows a consistent set of motions.

* Action: Sprays fertilizer on the affected plants if a disease is detected.

## Manipulator working of Harvesting Agribot

* Chilly Detection: Detects ripe chilies.

* Inverse Kinematics: Utilizes MoveIt to perform inverse kinematics for accurate harvesting of the chilies.

## Implementation 
- All the bots and the master system are connected via WiFi.
- A main system is used to monitor and control the agribots.
- Initially, the area is mapped using a harvesting bot.
- The positions of the plants are manually marked on the 2D map using the master system and stored locally.
- The harvesting agribot autonomously navigates to the marked positions (provided by the master system) and performs its task.
- It also detects the presence of disease and reports the plant's position to the master system if disease is detected.
- The fertilizer spraying agribot visits only those plant positions (provided by the master system) that are affected by disease.

## Dataset for Machine Learning
Can only be edited if you are a team member of this project.

https://drive.google.com/drive/folders/10nGa2Z8sbqDThqM_toTPskSZHXusqtVr?usp=drive_link

## Authors
- Aisha Nasrin TN
- Anan Ali Sha S
- Aneesh K
- Don Kurian Davis
