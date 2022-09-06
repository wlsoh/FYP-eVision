# e-Vision: Traffic Accident Detection System
<p align="center">
  <img src="./readme_img/interface.png" />
</p>
Individual Final Year Project (FYP) for Asia Pacific University (APU). A computer vision-based system that able to automatically detect for traffic accidents throughout the CCTV sources and provide immediate report to the responsible authority. Equipped with a graphical desktop interface that provide the convenient usage for interacting with the system to utilize the functionalities provided. In addition, a web view functionality was provided for the remote reviewing usage of the detected accident. The overall core features of the e-Vision system are as following.
1) Automatic traffic accident detection
2) Record detected accident with evidence images
3) Notify detected accident to person in charge
4) Review detected accident
5) Revise accident records that had been reviewed
6) Remote review detected accident (through web application)
7) User management
8) Camera source management & allocation

## Technical Approach Implementation
<p align="center">
  <img src="./readme_img/approach_overview.png" />
</p>
Instead of directly processing entire image frame to detect for traffic accidents, e-Vision implemented vehicle detection, vehicle tracking and accident detection phases in order to track every individual vehicle from the CCTV footage to monitor for accidents occurance. It cannot completely agreed that tracking individual vehicle able to provide more advantages as compared to processing entire frame because it depends on what kind of scenario that the system dealing with. However, such approach able to effectively track distinct vehicles that exist within the frame image with a great performance result.

## Algorithms & Techniques Implementation
<p align="center">
  <img src="./readme_img/algorithms_applied.png" />
</p>
<p>As the problems involved real time scenarios, single stage detector was preferred due to its speed performance. In this context, RetinaNet was implemented for the vehicle detection part due to its fascinating speed while maintaining a good overall accuracy. Initially, YOLO algorithm was chosen but was later replaced with RetinaNet due to its balancing within accuracy and speed.</p>
<p>Due to the time limitation of the project, a simpler tracking algorithm which known as centroid tracking was implemented for the vehicle tracking part over a standard algorithm such as DeepSORT. Since Euclidean distance was involved within this phase, the magnitude of the detected vehicle vector was able to be generated which used for the accident detection part.</p>
<p>In order to enhance the accident detection process, the model will process the magnitude anomaly for each individual vehicles over the frames. If the particular vehicle exceed the pre-defined threshold, the vehicle will be marked as suspicious accident which will further cropped and send to the deep CNN model to compute accident classification. Overall, all the sub-models created will be integrated together to enable the automated traffic accident detection task.</p>

