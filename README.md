# hsecure
rpi home security with usb webcam


1) first installl all the apt dependencies from `required-apt-packages.txt`  ... some more dependencies maybe needed, resolve as required.


2) Next follow the below tutorial for Setting up the flask app with gunicorn and nginx\
Link : https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04\
The custom `hsecure.local.conf` file is provided for your ease of setup, make required changes


4) Setup ssl with the below tutorial and replace the certificate and key filenames with the ones you generated in `hsecure.local.conf`\
Link : https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/


3) Once the webapp is running properly , open browser in your system gui and access https://hsecure.local to keep the application running\
You need to make changes to `/etc/hosts` add a entry `192.168.1.101 hsecure.local` when accessing locally in rpi where `192.168.1.101` is your rpi's IP address\
To enable https in firefox localy in your rpi you need to generate the .pkcs12 of your certificate using openssl and import the certificate in Firefox settings.


5) Voila! you have a running home security system with rpi\
Now whenever a person gets detected, you can get notifications on your phone in Pushbullet app once you provide the api key

