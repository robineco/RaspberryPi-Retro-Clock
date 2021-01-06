#!/bin/bash

sudo cp ./clock.service /lib/systemd/system/

sudo chmod 644 /lib/systemd/system/clock.service

sudo chmod +x /home/pi/main.py
sudo systemctl daemon-reload

sudo systemctl enable clock.service
sudo systemctl start clock.service